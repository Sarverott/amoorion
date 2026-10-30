"""The tumblr plugin against a local server shaped like the Tumblr API v2."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest
from amoorion_tumblr.text import blocks, text_of

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import Unsupported, open_plugin
from amoorion.vault import VaultLink, open_vault

BLOG = "me.tumblr.com"


class FakeTumblr(BaseHTTPRequestHandler):
    posts: list[dict] = []
    bodies: list[dict] = []

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _authorized(self):
        header = self.headers.get("Authorization", "")
        if 'oauth_consumer_key="ck"' in header and 'oauth_token="tok"' in header and "oauth_signature=" in header:
            return True
        self._send(401, {"meta": {"status": 401, "msg": "Unauthorized"}, "response": [],
                         "errors": [{"title": "Unauthorized", "code": 1016, "detail": "Unable to authorize"}]})
        return False

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if not self._authorized():
            return
        if urlparse(self.path).path == f"/v2/blog/{BLOG}/post/delete":
            found = [p for p in self.posts if p["id_string"] == body["id"]]
            if not found:
                return self._send(404, {"meta": {"status": 404, "msg": "Not Found"}, "response": []})
            FakeTumblr.posts = [p for p in self.posts if p["id_string"] != body["id"]]
            return self._send(200, {"meta": {"status": 200, "msg": "OK"}, "response": {"id": int(body["id"])}})
        assert urlparse(self.path).path == f"/v2/blog/{BLOG}/posts"
        self.bodies.append(body)
        post_id = str(7000 + len(self.posts))
        self.posts.append({"id": int(post_id), "id_string": post_id, "blog_name": "me", "timestamp": 1792000000,
                           "post_url": f"https://www.tumblr.com/me/{post_id}", "content": body["content"]})
        self._send(201, {"meta": {"status": 201, "msg": "Created"}, "response": {"id": post_id, "state": "published"}})

    def do_GET(self):
        if not self._authorized():
            return
        query = parse_qs(urlparse(self.path).query)
        assert query["npf"] == ["true"]
        posts = self.posts[::-1][: int(query["limit"][0])]
        self._send(200, {"meta": {"status": 200, "msg": "OK"}, "response": {"posts": posts}})

    def log_message(self, *args):
        pass


@pytest.fixture
def tumblr(monkeypatch):
    FakeTumblr.posts, FakeTumblr.bodies = [], []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeTumblr)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    for key, value in {"CONSUMER_KEY": "ck", "CONSUMER_SECRET": "cs", "TOKEN": "tok", "TOKEN_SECRET": "ts",
                       "BLOG": BLOG, "URI": f"http://127.0.0.1:{server.server_port}"}.items():
        monkeypatch.setenv(f"AMOORION_SECRET_TUMBLR_{key}", value)
    yield open_plugin("tumblr", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_and_read(tumblr):
    posted = tumblr.post(Post(title="Hi", text="one\n\ntwo", links=["https://a.example"], tags=["#amoorion", "x"]))
    assert posted.url == "https://www.tumblr.com/me/7000" and posted.text == "Hi\n\none\n\ntwo\n\nhttps://a.example"
    assert FakeTumblr.bodies[0]["tags"] == "amoorion,x" and FakeTumblr.bodies[0]["state"] == "published"
    tumblr.post(Post(text="second"))
    read = tumblr.read(5)
    assert [message.text for message in read] == ["second", posted.text]
    assert read[0].created_at.year == 2026


def test_reply_unsupported(tumblr):
    with pytest.raises(Unsupported):
        tumblr.reply(tumblr.post(Post(text="x")), "y")


def test_error_detail(tumblr, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_TUMBLR_TOKEN", "other")
    with pytest.raises(AmoorionError, match="Unable to authorize"):
        tumblr.post(Post(text="x"))


def test_blocks_round_trip():
    content = blocks(Post(title="T", text="a\n\nb", links=["https://l"]))
    assert [block.get("subtype") for block in content] == ["heading1", None, None, None]
    assert text_of(content) == "T\n\na\n\nb\n\nhttps://l"


def test_delete_a_post(tumblr):
    gone = tumblr.post(Post(text="oops"))
    kept = tumblr.post(Post(text="fine"))
    tumblr.delete(gone)
    assert [m.id for m in tumblr.read()] == [kept.id]
    with pytest.raises(AmoorionError, match="Not Found"):
        tumblr.delete(gone)
    assert tumblr.profile() == BLOG.removesuffix(".tumblr.com")
