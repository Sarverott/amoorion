"""Sentry and Plane hooks, and the small utilities."""

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from amoorion import Amoorion
from amoorion.core import AmoorionError
from amoorion.utilities import open_tunnel, post_from_markdown
from amoorion.vault import open_vault
from amoorion.vault.base import VaultLink


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AMOORION_VAULT", "env")
    monkeypatch.setenv("AMOORION_INBOX", str(tmp_path / "inbox.sqlite3"))
    monkeypatch.setenv("AMOORION_SECRET_HOOKS_SENTRY_SECRET", "s")
    monkeypatch.setenv("AMOORION_SECRET_HOOKS_PLANE_SECRET", "p")
    return TestClient(Amoorion().api())


def signed(key, payload):
    body = json.dumps(payload).encode()
    return body, hmac.new(key, body, hashlib.sha256).hexdigest()


def test_sentry(client):
    body, signature = signed(b"s", {"action": "created", "data": {"issue": {"title": "Boom", "permalink": "https://s/1"}}})
    headers = {"Sentry-Hook-Signature": signature, "Sentry-Hook-Resource": "issue", "Request-ID": "r1"}
    answer = client.post("/hooks/sentry", content=body, headers=headers).json()
    assert answer["text"] == "sentry: issue created: Boom" and answer["url"] == "https://s/1" and answer["id"] == "r1"
    assert client.post("/hooks/sentry", content=body, headers=headers | {"Sentry-Hook-Signature": "x"}).status_code == 403


def test_sentry_installation_is_not_kept(client):
    body, signature = signed(b"s", {"action": "created", "data": {}})
    headers = {"Sentry-Hook-Signature": signature, "Sentry-Hook-Resource": "installation"}
    assert client.post("/hooks/sentry", content=body, headers=headers).json() == {}


def test_plane_keeps_one_message_across_retries(client):
    body, signature = signed(b"p", {"event": "workitem.created", "event_id": "e1", "data": {"name": "Fix it"}})
    headers = {"X-Plane-Signature": signature, "X-Plane-Event": "workitem.created", "X-Plane-Delivery": "d1"}
    answer = client.post("/hooks/plane", content=body, headers=headers).json()
    assert answer["text"] == "plane: workitem.created: Fix it" and answer["id"] == "e1"
    assert client.post("/hooks/plane", content=body, headers={}).status_code == 403


def test_markdown_post():
    post, to = post_from_markdown("---\ntitle: T\ntags: [a]\nto: x\n---\n\nBody\n")
    assert (post.title, post.tags, post.text, to) == ("T", ["a"], "Body", ["x"])
    assert post_from_markdown("Only text")[0].text == "Only text"
    with pytest.raises(AmoorionError):
        post_from_markdown("---\ntitle: T\n")
    with pytest.raises(ValueError):
        post_from_markdown("---\nnonsense: 1\n---\nBody")


def test_tunnel_takes_its_token_from_the_vault(monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_NGROK_TOKEN", "n")
    calls = []
    open_tunnel(8000, open_vault(VaultLink(kind="env")), lambda port, authtoken: calls.append((port, authtoken)))
    assert calls == [(8000, "n")]
