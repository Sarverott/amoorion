"""The mastodon plugin against a local server shaped like Mastodon's REST API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest
from amoorion_mastodon.base import compose, length, to_text

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault

ME = {"id": "7", "acct": "me", "display_name": "Me"}


class FakeMastodon(BaseHTTPRequestHandler):
    statuses: list[dict] = []
    keys: list[str] = []
    max_characters = 60

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _authorized(self):
        if self.headers.get("Authorization") != "Bearer tok":
            self._send(401, {"error": "The access token is invalid"})
            return False
        return True

    def do_GET(self):
        url = urlparse(self.path)
        if not self._authorized():
            return
        if url.path == "/api/v2/instance":
            return self._send(200, {"configuration": {"statuses": {"max_characters": self.max_characters}}})
        if url.path == "/api/v1/accounts/verify_credentials":
            return self._send(200, ME)
        if url.path == "/api/v1/accounts/7/statuses":
            limit = int(parse_qs(url.query)["limit"][0])
            return self._send(200, self.statuses[::-1][:limit])
        self._send(404, {"error": "Record not found"})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if not self._authorized():
            return
        self.keys.append(self.headers.get("Idempotency-Key"))
        number = str(len(self.statuses) + 1)
        html = "".join(f"<p>{part}</p>" for part in body["status"].split("\n\n"))
        status = {
            "id": number,
            "url": f"https://masto.test/@me/{number}",
            "content": html.replace("\n", "<br />"),
            "account": ME,
            "in_reply_to_id": body.get("in_reply_to_id"),
            "created_at": "2026-10-26T12:00:00.000Z",
        }
        self.statuses.append(status)
        self._send(200, status)

    def do_DELETE(self):
        if not self._authorized():
            return
        number = self.path.rsplit("/", 1)[-1]
        found = [s for s in self.statuses if s["id"] == number]
        if not self.path.startswith("/api/v1/statuses/") or not found:
            return self._send(404, {"error": "Record not found"})
        FakeMastodon.statuses = [s for s in self.statuses if s["id"] != number]
        self._send(200, found[0] | {"text": "source"})

    def log_message(self, *args):
        pass


@pytest.fixture
def mastodon(monkeypatch):
    FakeMastodon.statuses, FakeMastodon.keys = [], []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeMastodon)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("AMOORION_SECRET_MASTODON_URI", f"http://127.0.0.1:{server.server_port}/")
    monkeypatch.setenv("AMOORION_SECRET_MASTODON_TOKEN", "tok")
    yield open_plugin("mastodon", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_read_reply(mastodon):
    posted = mastodon.post(Post(title="Hi", text="first", tags=["amoorion"]))
    assert posted.text == "Hi\n\nfirst\n#amoorion" and posted.url == "https://masto.test/@me/1"
    answer = mastodon.reply(posted, "second")
    assert answer.reply_to == posted.id
    read = mastodon.read(5)
    assert [message.text for message in read] == ["second", "Hi\n\nfirst\n#amoorion"]
    assert read[0].author.name == "Me"
    assert len(set(FakeMastodon.keys)) == 2  # one idempotency key per status


def test_server_limit_with_links_as_23(mastodon):
    link = "https://example.org/" + "a" * 100
    mastodon.post(Post(text="short", links=[link]))  # 5 + 1 + 23 characters
    with pytest.raises(AmoorionError, match="takes 60 characters"):
        mastodon.post(Post(text="x" * 61))
    assert len(FakeMastodon.statuses) == 1


def test_wrong_token(mastodon, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_MASTODON_TOKEN", "bad")
    with pytest.raises(AmoorionError, match="access token is invalid"):
        mastodon.read()


def test_text_helpers():
    assert to_text("<p>one<br />two</p><p>three</p>") == "one\ntwo\n\nthree"
    assert compose(Post(text="t", links=["https://a"], tags=["#x", "y"])) == "t\nhttps://a\n#x #y"
    assert length("see https://example.org/long", ["https://example.org/long"]) == 4 + 23


def test_delete_a_status(mastodon):
    gone = mastodon.post(Post(text="oops"))
    kept = mastodon.post(Post(text="fine"))
    mastodon.delete(gone)
    assert [m.id for m in mastodon.read()] == [kept.id]
    with pytest.raises(AmoorionError, match="404: Record not found"):
        mastodon.delete(gone)
    assert mastodon.profile() == "me@127.0.0.1"
