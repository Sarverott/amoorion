"""The facebook plugin against a local server shaped like the Graph API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest
from amoorion_facebook.base import compose

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault


class FakeGraph(BaseHTTPRequestHandler):
    posts: list[dict] = []
    comments: list[dict] = []
    paths: list[str] = []

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _authorized(self):
        self.paths.append(self.path)
        if self.headers.get("Authorization") == "Bearer page-tok":
            return True
        self._send(400, {"error": {"message": "Invalid OAuth access token.", "type": "OAuthException", "code": 190}})
        return False

    def do_POST(self):
        form = parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
        if not self._authorized():
            return
        path = urlparse(self.path).path
        if path == "/v1/123/feed":
            post = {"id": f"123_{len(self.posts) + 1}", "message": form["message"][0],
                    "created_time": "2026-10-26T12:00:00+0000", "permalink_url": "https://facebook.test/p"}
            self.posts.append(post)
            return self._send(200, {"id": post["id"]})
        if path.endswith("/comments"):
            self.comments.append({"on": path.split("/")[2], "message": form["message"][0]})
            return self._send(200, {"id": f"c{len(self.comments)}"})

    def do_GET(self):
        if not self._authorized():
            return
        query = parse_qs(urlparse(self.path).query)
        self._send(200, {"data": self.posts[::-1][: int(query["limit"][0])]})

    def do_DELETE(self):
        if not self._authorized():
            return
        target = urlparse(self.path).path.rsplit("/", 1)[-1]
        if not any(p["id"] == target for p in self.posts):
            return self._send(400, {"error": {"message": "Unsupported delete request.", "code": 100}})
        FakeGraph.posts = [p for p in self.posts if p["id"] != target]
        self._send(200, {"success": True})

    def log_message(self, *args):
        pass


@pytest.fixture
def facebook(monkeypatch):
    FakeGraph.posts, FakeGraph.comments, FakeGraph.paths = [], [], []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeGraph)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("AMOORION_SECRET_FACEBOOK_PAGE_ID", "123")
    monkeypatch.setenv("AMOORION_SECRET_FACEBOOK_PAGE_TOKEN", "page-tok")
    monkeypatch.setenv("AMOORION_SECRET_FACEBOOK_URI", f"http://127.0.0.1:{server.server_port}/v1")
    yield open_plugin("facebook", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_read_comment(facebook):
    posted = facebook.post(Post(title="Hi", text="there", links=["https://a"]))
    assert posted.id == "123_1" and posted.text == "Hi\n\nthere\n\nhttps://a"
    comment = facebook.reply(posted, "first!")
    assert comment.reply_to == "123_1" and FakeGraph.comments == [{"on": "123_1", "message": "first!"}]
    [read] = facebook.read(5)
    assert read.text == posted.text and read.created_at.year == 2026


def test_token_never_in_urls(facebook):
    facebook.post(Post(text="x"))
    facebook.read()
    assert not any("page-tok" in path for path in FakeGraph.paths)


def test_graph_error_message(facebook, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_FACEBOOK_PAGE_TOKEN", "expired")
    with pytest.raises(AmoorionError, match="Invalid OAuth access token"):
        facebook.post(Post(text="x"))


def test_compose_tags():
    assert compose(Post(text="t", tags=["#a", "b"])) == "t\n\n#a #b"


def test_delete_a_post(facebook):
    gone = facebook.post(Post(text="oops"))
    kept = facebook.post(Post(text="fine"))
    facebook.delete(gone)
    assert [m.id for m in facebook.read()] == [kept.id]
    with pytest.raises(AmoorionError, match="Unsupported delete request"):
        facebook.delete(gone)
    assert facebook.profile() == "123"
