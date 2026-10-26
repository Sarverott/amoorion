"""The bluesky plugin against a local server shaped like a PDS's XRPC API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion_bluesky.base import compose, graphemes
from amoorion.vault import VaultLink, open_vault

DID = "did:plc:me"


class FakePds(BaseHTTPRequestHandler):
    records: list[dict] = []

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _authorized(self):
        if self.headers.get("Authorization") != "Bearer access":
            self._send(401, {"error": "AuthMissing", "message": "Authentication Required"})
            return False
        return True

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/xrpc/com.atproto.server.createSession":
            if body != {"identifier": "me.bsky.social", "password": "app-pass"}:
                return self._send(401, {"error": "AuthenticationRequired", "message": "Invalid identifier or password"})
            return self._send(200, {"accessJwt": "access", "refreshJwt": "r", "handle": "me.bsky.social", "did": DID})
        if self.path == "/xrpc/com.atproto.repo.createRecord" and self._authorized():
            assert body["repo"] == DID and body["collection"] == "app.bsky.feed.post"
            uri = f"at://{DID}/app.bsky.feed.post/rkey{len(self.records) + 1}"
            self.records.append({"uri": uri, "cid": f"cid{len(self.records) + 1}", "record": body["record"]})
            return self._send(200, {"uri": uri, "cid": self.records[-1]["cid"]})

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if not self._authorized():
            return
        if url.path == "/xrpc/app.bsky.feed.getAuthorFeed":
            limit = int(query["limit"][0])
            feed = [
                {"post": record | {"author": {"handle": "me.bsky.social", "displayName": "Me"}}}
                for record in self.records[::-1][:limit]
            ]
            return self._send(200, {"feed": feed})
        if url.path == "/xrpc/app.bsky.feed.getPosts":
            return self._send(200, {"posts": [r for r in self.records if r["uri"] in query["uris"]]})

    def log_message(self, *args):
        pass


@pytest.fixture
def bluesky(monkeypatch):
    FakePds.records = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakePds)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("AMOORION_SECRET_BLUESKY_USERNAME", "me.bsky.social")
    monkeypatch.setenv("AMOORION_SECRET_BLUESKY_PASSWORD", "app-pass")
    monkeypatch.setenv("AMOORION_SECRET_BLUESKY_URI", f"http://127.0.0.1:{server.server_port}")
    yield open_plugin("bluesky", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_with_links_and_tags(bluesky):
    message = bluesky.post(Post(title="Hi", text="zażółć", links=["https://x.example"], tags=["#amoorion", "test"]))
    assert message.text == "Hi\n\nzażółć\nhttps://x.example\n#amoorion #test"
    assert message.url == "https://bsky.app/profile/me.bsky.social/post/rkey1"
    record = FakePds.records[0]["record"]
    assert record["$type"] == "app.bsky.feed.post" and record["createdAt"]
    encoded = record["text"].encode()
    marked = [encoded[f["index"]["byteStart"] : f["index"]["byteEnd"]].decode() for f in record["facets"]]
    assert marked == ["https://x.example", "#amoorion", "#test"]


def test_read_newest_first(bluesky):
    bluesky.post(Post(text="one"))
    bluesky.post(Post(text="two"))
    assert [message.text for message in bluesky.read(5)] == ["two", "one"]
    assert bluesky.read(1)[0].author.name == "Me"


def test_reply_keeps_the_thread_root(bluesky):
    first = bluesky.post(Post(text="root"))
    second = bluesky.reply(first, "answer")
    third = bluesky.reply(second, "answer to answer")
    reply = FakePds.records[2]["record"]["reply"]
    assert reply["root"]["uri"] == first.id and reply["parent"]["uri"] == second.id
    assert third.reply_to == second.id


def test_too_long_is_refused_before_sending(bluesky):
    with pytest.raises(AmoorionError, match="300 graphemes"):
        bluesky.post(Post(text="x" * 301))
    assert FakePds.records == []


def test_wrong_password(bluesky, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_BLUESKY_PASSWORD", "nope")
    with pytest.raises(AmoorionError, match="Invalid identifier or password"):
        bluesky.post(Post(text="x"))


def test_graphemes_and_plain_compose():
    assert graphemes("é") == 1 and graphemes("👍🏽") == 1
    assert compose(Post(text="plain")) == ("plain", [])
