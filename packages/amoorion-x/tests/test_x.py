"""The x plugin against a local server shaped like the X API v2, checking OAuth 1.0a signatures."""

import base64
import hashlib
import hmac
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

import pytest
from amoorion_x.base import compose, weight
from oauthlib.oauth1.rfc5849 import signature

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault

USER = {"id": "42", "username": "me", "name": "Me"}


class FakeX(BaseHTTPRequestHandler):
    tweets: list[dict] = []

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _signed(self, method):
        header = self.headers.get("Authorization", "")
        if not header.startswith("OAuth "):
            return False
        params = signature.collect_parameters(
            uri_query=urlparse(self.path).query, headers={"Authorization": header}, exclude_oauth_signature=True
        )
        oauth = dict(signature.collect_parameters(headers={"Authorization": header}, exclude_oauth_signature=False))
        base = signature.signature_base_string(
            method,
            signature.base_string_uri(f"http://{self.headers['Host']}{urlparse(self.path).path}"),
            signature.normalize_parameters(params),
        )
        key = b"api-secret&access-secret"
        expected = base64.b64encode(hmac.new(key, base.encode(), hashlib.sha1).digest()).decode()
        return oauth.get("oauth_consumer_key") == "api-key" and unquote(oauth["oauth_signature"]) == expected

    def do_GET(self):
        if not self._signed("GET"):
            return self._send(401, {"title": "Unauthorized", "detail": "Unauthorized", "status": 401})
        url = urlparse(self.path)
        if url.path == "/2/users/me":
            return self._send(200, {"data": USER})
        if url.path == "/2/users/42/tweets":
            return self._send(200, {"data": self.tweets[::-1]})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if not self._signed("POST"):
            return self._send(401, {"title": "Unauthorized", "detail": "Unauthorized", "status": 401})
        if body["text"] == "duplicate":
            return self._send(403, {"errors": [{"message": "You are not allowed to create a Tweet with duplicate content."}]})
        tweet = {"id": str(100 + len(self.tweets)), "text": body["text"], "created_at": "2026-10-26T12:00:00.000Z"}
        if "reply" in body:
            tweet["referenced_tweets"] = [{"type": "replied_to", "id": body["reply"]["in_reply_to_tweet_id"]}]
        self.tweets.append(tweet)
        self._send(201, {"data": {"id": tweet["id"], "text": tweet["text"]}})

    def do_DELETE(self):
        if not self._signed("DELETE"):
            return self._send(401, {"title": "Unauthorized", "detail": "Unauthorized", "status": 401})
        number = urlparse(self.path).path.rsplit("/", 1)[-1]
        found = any(t["id"] == number for t in self.tweets)
        FakeX.tweets = [t for t in self.tweets if t["id"] != number]
        self._send(200, {"data": {"deleted": found}})

    def log_message(self, *args):
        pass


@pytest.fixture
def x(monkeypatch):
    FakeX.tweets = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeX)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    for key, value in {"API_KEY": "api-key", "API_SECRET": "api-secret", "ACCESS_TOKEN": "access-token",
                       "ACCESS_SECRET": "access-secret", "URI": f"http://127.0.0.1:{server.server_port}"}.items():
        monkeypatch.setenv(f"AMOORION_SECRET_X_{key}", value)
    yield open_plugin("x", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_read_reply_signed(x):
    posted = x.post(Post(text="hello", tags=["amoorion"]))
    assert posted.text == "hello\n#amoorion" and posted.url == "https://x.com/me/status/100"
    answer = x.reply(posted, "again")
    assert answer.reply_to == posted.id
    read = x.read(5)
    assert [message.text for message in read] == ["again", "hello\n#amoorion"]
    assert read[0].reply_to == posted.id


def test_bad_signature_refused(x, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_X_ACCESS_SECRET", "wrong")
    with pytest.raises(AmoorionError, match="answered 401: Unauthorized"):
        x.post(Post(text="hello"))


def test_errors_list_reason(x):
    with pytest.raises(AmoorionError, match="duplicate content"):
        x.post(Post(text="duplicate"))


def test_weighted_limit_before_sending(x):
    with pytest.raises(AmoorionError, match="280 weighted"):
        x.post(Post(text="日" * 141))
    assert FakeX.tweets == []


def test_weight_and_compose():
    assert weight("abc", []) == 3 and weight("日本", []) == 4
    link = "https://example.org/" + "a" * 50
    assert weight(f"see {link}", [link]) == 4 + 23
    assert compose(Post(title="T", text="b", links=["https://a"])) == "T\n\nb\nhttps://a"


def test_delete_a_post(x):
    gone = x.post(Post(text="oops"))
    kept = x.post(Post(text="fine"))
    x.delete(gone)
    assert [m.id for m in x.read()] == [kept.id]
    with pytest.raises(AmoorionError, match="did not delete"):
        x.delete(gone)
    assert x.profile() == USER["username"]
