from datetime import UTC, datetime

from amoorion.api import create_app
from amoorion.inbox import Inbox
from amoorion.methods import InboxMethod, Publish, Read
from amoorion.models import Message
from amoorion.vault import VaultLink, open_vault


def test_keeps_once_newest_first(tmp_path):
    inbox = Inbox(tmp_path / "inbox.sqlite3")
    old = Message(platform="a", text="old", id="1", created_at=datetime(2026, 1, 1, tzinfo=UTC))
    new = Message(platform="b", text="new", id="1", created_at=datetime(2026, 2, 1, tzinfo=UTC))
    inbox.keep([new, old])
    inbox.keep([old])
    assert [message.text for message in inbox.list()] == ["new", "old"]
    assert [message.text for message in inbox.list("a")] == ["old"]
    assert inbox.list(limit=1)[0].text == "new"


def test_message_without_id_gets_one(tmp_path):
    inbox = Inbox(tmp_path / "inbox.sqlite3")
    [kept] = inbox.keep([Message(platform="hook:generic", text="ping")])
    assert kept.id and inbox.list()[0].id == kept.id


def test_path_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AMOORION_INBOX", str(tmp_path / "here.sqlite3"))
    Inbox().keep([Message(platform="a", text="x", id="1")])
    assert (tmp_path / "here.sqlite3").exists()


def test_read_keeps_what_it_read():
    vault = open_vault(VaultLink(kind="env"))
    [published] = Publish(vault)(text="kept by read", to=["dryrun"])
    Read(vault)(platform="dryrun", limit=1)
    assert InboxMethod(vault)(platform="dryrun")[0]["id"] == published["message"]["id"]


def test_hook_messages_go_to_inbox(monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setenv("AMOORION_SECRET_HOOKS_GENERIC_TOKEN", "tok")
    client = TestClient(create_app(open_vault(VaultLink(kind="env"))))
    answer = client.post("/hooks/generic", json={"text": "deployed"}, headers={"X-Amoorion-Token": "tok"})
    assert answer.status_code == 200 and answer.json()["id"]
    assert Inbox().list("hook:generic")[0].text == "deployed"
