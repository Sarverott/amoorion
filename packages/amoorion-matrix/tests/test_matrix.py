"""The matrix plugin against a local server shaped like a homeserver's client-server API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import pytest
from amoorion_matrix.text import compose

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault

ROOM = "!room:hs.test"
API = "/_matrix/client/v3"


class FakeHomeserver(BaseHTTPRequestHandler):
    events: list[dict] = []
    transactions: list[str] = []

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _authorized(self):
        if self.headers.get("Authorization") != "Bearer tok":
            self._send(401, {"errcode": "M_UNKNOWN_TOKEN", "error": "Invalid access token passed."})
            return False
        return True

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        if not self._authorized():
            return
        if path == f"{API}/account/whoami":
            return self._send(200, {"user_id": "@bot:hs.test"})
        if path == f"{API}/directory/room/#test:hs.test":
            return self._send(200, {"room_id": ROOM})
        if path == f"{API}/rooms/{ROOM}/messages":
            query = parse_qs(url.query)
            assert query["dir"] == ["b"] and json.loads(query["filter"][0]) == {"types": ["m.room.message"]}
            return self._send(200, {"chunk": self.events[::-1][: int(query["limit"][0])]})
        self._send(403, {"errcode": "M_FORBIDDEN", "error": "You are not in this room."})

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
        content = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if not self._authorized():
            return
        redact = f"{API}/rooms/{ROOM}/redact/"
        if path.startswith(redact):
            event_id = path.removeprefix(redact).split("/")[0]
            found = [e for e in self.events if e["event_id"] == event_id]
            if not found:
                return self._send(404, {"errcode": "M_NOT_FOUND", "error": "Event not found."})
            found[0]["content"] = {}
            return self._send(200, {"event_id": "$redaction"})
        prefix = f"{API}/rooms/{ROOM}/send/m.room.message/"
        if not path.startswith(prefix):
            return self._send(403, {"errcode": "M_FORBIDDEN", "error": "You are not in this room."})
        self.transactions.append(path.removeprefix(prefix))
        event_id = f"${len(self.events) + 1}"
        self.events.append({"type": "m.room.message", "event_id": event_id, "sender": "@bot:hs.test",
                            "origin_server_ts": 1793000000000, "content": content})
        self.events.append({"type": "m.reaction", "event_id": "$r", "sender": "@ada:hs.test", "content": {}})
        self._send(200, {"event_id": event_id})

    def log_message(self, *args):
        pass


@pytest.fixture
def matrix(monkeypatch):
    FakeHomeserver.events, FakeHomeserver.transactions = [], []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeHomeserver)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("AMOORION_SECRET_MATRIX_URI", f"http://127.0.0.1:{server.server_port}/")
    monkeypatch.setenv("AMOORION_SECRET_MATRIX_TOKEN", "tok")
    monkeypatch.setenv("AMOORION_SECRET_MATRIX_ROOM", ROOM)
    yield open_plugin("matrix", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_read_reply(matrix):
    posted = matrix.post(Post(title="News", text="hello", tags=["amoorion"]))
    assert posted.text == "News\n\nhello\n#amoorion" and posted.author.handle == "@bot:hs.test"
    assert posted.url == "https://matrix.to/#/%21room%3Ahs.test/%241"
    answer = matrix.reply(posted, "more")
    assert answer.reply_to == "$1"
    read = matrix.read(10)
    assert [message.text for message in read] == ["more", posted.text]  # reactions left out
    assert read[0].reply_to == "$1" and read[0].created_at.year == 2026
    assert len(set(FakeHomeserver.transactions)) == 2


def test_room_alias_is_resolved(matrix, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_MATRIX_ROOM", "#test:hs.test")
    aliased = open_plugin("matrix", open_vault(VaultLink(kind="env")))
    assert aliased.post(Post(text="via alias")).id == "$1"


def test_errors(matrix, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_MATRIX_ROOM", "!other:hs.test")
    with pytest.raises(AmoorionError, match="not in this room"):
        open_plugin("matrix", open_vault(VaultLink(kind="env"))).post(Post(text="x"))
    monkeypatch.setenv("AMOORION_SECRET_MATRIX_TOKEN", "bad")
    with pytest.raises(AmoorionError, match="Invalid access token"):
        matrix.read()


def test_compose():
    assert compose(Post(text="t", links=["https://a"])) == "t\nhttps://a"


def test_delete_redacts(matrix):
    gone = matrix.post(Post(text="oops"))
    kept = matrix.post(Post(text="fine"))
    matrix.delete(gone)
    assert [m.id for m in matrix.read()] == [kept.id]
    with pytest.raises(AmoorionError, match="Event not found"):
        matrix.delete(gone.model_copy(update={"id": "$nope"}))
