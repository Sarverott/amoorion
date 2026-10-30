"""The hooks of GitHub, GitLab and Discord through the API, with what each service really sends."""

import hashlib
import hmac
import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient

from amoorion.api import create_app
from amoorion.core import AmoorionError
from amoorion.inbox import Inbox
from amoorion.methods import Notify
from amoorion.methods.all_params import NotifyParams
from amoorion.models import Message, Post
from amoorion.vault import VaultLink, open_vault



class Target:
    posts: list[Post] = []

    def __init__(self, name):
        self.name = name

    def post(self, post):
        if self.name == "nope":
            raise AmoorionError("a failing target stops nothing")
        self.posts.append(post)
        return Message(platform=self.name, text=post.text)


KEY = Ed25519PrivateKey.generate()
PUBLIC = KEY.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("AMOORION_SECRET_HOOKS_GITHUB_SECRET", "sekret")
    monkeypatch.setenv("AMOORION_SECRET_HOOKS_GITLAB_TOKEN", "sekret")
    monkeypatch.setenv("AMOORION_SECRET_HOOKS_DISCORD_PUBLIC_KEY", PUBLIC)
    inbox = Inbox(tmp_path / "inbox.sqlite3")
    client = TestClient(create_app(open_vault(VaultLink(kind="env")), inbox))
    client.inbox = inbox
    return client


def github(client, event, payload, secret="sekret"):
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {"X-Hub-Signature-256": signature, "X-GitHub-Event": event, "X-GitHub-Delivery": "d1"}
    return client.post("/hooks/github", content=body, headers=headers)


def test_github_push_is_kept(client):
    payload = {
        "ref": "refs/heads/master",
        "commits": [{}, {}],
        "head_commit": {"message": "fix"},
        "repository": {"full_name": "a/b"},
        "sender": {"login": "me"},
        "compare": "https://github.com/a/b/compare/x",
    }
    answer = github(client, "push", payload)
    assert answer.status_code == 200
    assert answer.json()["text"] == "a/b: 2 commits to refs/heads/master: fix"
    assert answer.json()["url"].endswith("/compare/x") and answer.json()["author"]["handle"] == "me"


def test_github_issue_and_ping(client):
    issue = {"action": "opened", "issue": {"title": "Bug", "html_url": "u"}, "repository": {"full_name": "a/b"}}
    assert github(client, "issues", issue).json()["text"] == "a/b: issue opened: Bug"
    assert github(client, "ping", {"zen": "x"}).json() == {}


def test_github_refuses_a_wrong_signature(client):
    assert github(client, "push", {}, secret="wrong").status_code == 403
    assert client.post("/hooks/github", json={}).status_code == 403


def test_gitlab(client):
    payload = {
        "object_kind": "merge_request",
        "user": {"username": "me"},
        "project": {"path_with_namespace": "a/b"},
        "object_attributes": {"title": "Feature", "action": "open", "url": "u"},
    }
    answer = client.post("/hooks/gitlab", json=payload, headers={"X-Gitlab-Token": "sekret"})
    assert answer.json()["text"] == "a/b: merge request open: Feature"
    assert answer.json()["author"]["handle"] == "me"
    assert client.post("/hooks/gitlab", json=payload, headers={"X-Gitlab-Token": "no"}).status_code == 403
    assert client.post("/hooks/gitlab", json=payload).status_code == 403


def test_what_a_hook_receives_goes_to_the_notify_targets(client, monkeypatch):
    sent = []
    monkeypatch.setenv("AMOORION_NOTIFY", "ntfy, nope")
    monkeypatch.setattr("amoorion.methods.publish_method.open_plugin", lambda name, vault: sent.append(name) or Target(name))
    payload = {"object_kind": "push", "project": {"path_with_namespace": "a/b", "web_url": "u"}, "commits": []}
    assert client.post("/hooks/gitlab", json=payload, headers={"X-Gitlab-Token": "sekret"}).status_code == 200
    assert sent == ["ntfy", "nope"]
    assert Target.posts[-1].links == ["u"] and Target.posts[-1].text.startswith("a/b:")


def test_no_notify_targets_no_notifications(monkeypatch):
    monkeypatch.delenv("AMOORION_NOTIFY", raising=False)
    assert Notify(open_vault(VaultLink(kind="env"))).run(NotifyParams(text="x")) == []


def discord(client, payload, key=KEY):
    body, timestamp = json.dumps(payload).encode(), "1700000000"
    headers = {"X-Signature-Ed25519": key.sign(timestamp.encode() + body).hex(), "X-Signature-Timestamp": timestamp}
    return client.post("/hooks/discord", content=body, headers=headers)


def test_discord_ping_is_answered_and_not_kept(client):
    assert discord(client, {"type": 1}).json() == {"type": 1}
    assert client.inbox.list() == []


def test_discord_command_is_kept_and_answered_privately(client):
    payload = {
        "type": 2,
        "id": "9",
        "data": {"name": "say", "options": [{"name": "text", "value": "hi"}]},
        "member": {"user": {"username": "me"}},
    }
    answer = discord(client, payload).json()
    assert answer["type"] == 4 and answer["data"]["flags"] == 64
    [kept] = client.inbox.list()
    assert kept.text == "/say text=hi" and kept.author.handle == "me"


def test_discord_refuses_a_wrong_signature(client):
    assert discord(client, {"type": 1}, key=Ed25519PrivateKey.generate()).status_code == 403
    assert client.post("/hooks/discord", json={"type": 1}).status_code == 403
