"""The ntfy plugin against a local server shaped like ntfy's."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault


class FakeNtfy(BaseHTTPRequestHandler):
    events: list[dict] = []
    token = None

    def log_message(self, *args):
        pass

    def _allowed(self):
        if self.token and self.headers.get("Authorization") != f"Bearer {self.token}":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "forbidden"}).encode())
            return False
        return True

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if not self._allowed():
            return
        event = {"id": f"n{len(self.events)}", "time": 1700000000, "event": "message"} | body
        self.events.append(event)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(event).encode())

    def do_GET(self):
        if not self._allowed():
            return
        assert self.path.startswith("/news/json?") and "poll=1" in self.path
        self.send_response(200)
        self.end_headers()
        for event in [{"event": "open"}, *self.events]:
            self.wfile.write((json.dumps(event) + "\n").encode())


@pytest.fixture
def ntfy(monkeypatch):
    FakeNtfy.events, FakeNtfy.token = [], None
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeNtfy)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("AMOORION_SECRET_NTFY_URI", f"http://127.0.0.1:{server.server_port}/")
    monkeypatch.setenv("AMOORION_SECRET_NTFY_TOPIC", "news")
    monkeypatch.delenv("AMOORION_SECRET_NTFY_TOKEN", raising=False)
    yield open_plugin("ntfy", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_sends_title_tags_and_link(ntfy):
    sent = ntfy.post(Post(text="hi", title="T", tags=["#a"], links=["https://x.test/1", "https://x.test/2"]))
    event = FakeNtfy.events[0]
    assert event["topic"] == "news" and event["title"] == "T" and event["tags"] == ["a"]
    assert event["click"] == "https://x.test/1" and event["message"] == "hi\nhttps://x.test/2"
    assert sent.id == "n0" and sent.url == "https://x.test/1"


def test_read_gives_the_newest_first_and_only_messages(ntfy):
    for text in ("one", "two", "three"):
        ntfy.post(Post(text=text))
    assert [message.text for message in ntfy.read(limit=2)] == ["three", "two"]


def test_a_protected_topic_needs_its_token(ntfy, monkeypatch):
    FakeNtfy.token = "tok"
    with pytest.raises(AmoorionError, match="forbidden"):
        ntfy.post(Post(text="hi"))
    monkeypatch.setenv("AMOORION_SECRET_NTFY_TOKEN", "tok")
    assert ntfy.post(Post(text="hi")).id == "n0"
