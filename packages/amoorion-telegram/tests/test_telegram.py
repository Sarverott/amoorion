"""The telegram plugin against a local server shaped like the Bot API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from amoorion_telegram.base import compose, link

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault

CHAT = {"id": -1009, "type": "supergroup", "title": "Test"}
BOT = {"id": 1, "is_bot": True, "first_name": "Amoorion", "username": "amoorion_bot"}


class FakeTelegram(BaseHTTPRequestHandler):
    sent: list[dict] = []
    updates: list[dict] = []

    def _send(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        token, _, method = self.path.removeprefix("/bot").partition("/")
        if token != "123:tok":
            return self._send(401, {"ok": False, "error_code": 401, "description": "Unauthorized"})
        if method == "getUpdates":
            return self._send(200, {"ok": True, "result": self.updates})
        if method == "deleteMessage":
            if not any(m["message_id"] == body["message_id"] for m in self.sent):
                return self._send(400, {"ok": False, "error_code": 400, "description": "Bad Request: message to delete not found"})
            FakeTelegram.sent = [m for m in self.sent if m["message_id"] != body["message_id"]]
            return self._send(200, {"ok": True, "result": True})
        if method != "sendMessage":
            return self._send(404, {"ok": False, "error_code": 404, "description": "Not Found"})
        if str(body["chat_id"]) != "-1009":
            return self._send(400, {"ok": False, "error_code": 400, "description": "Bad Request: chat not found"})
        number = len(self.sent) + 100
        message = {"message_id": number, "from": BOT, "chat": CHAT, "date": 1793000000, "text": body["text"]}
        if "reply_parameters" in body:
            original = next(m for m in self.sent if m["message_id"] == body["reply_parameters"]["message_id"])
            message["reply_to_message"] = original
        self.sent.append(message)
        self._send(200, {"ok": True, "result": message})

    def log_message(self, *args):
        pass


@pytest.fixture
def telegram(monkeypatch):
    FakeTelegram.sent = []
    FakeTelegram.updates = [
        {"update_id": 1, "message": {"message_id": 7, "chat": CHAT, "date": 1793000000, "text": "hi bot",
                                     "from": {"id": 5, "first_name": "Ada", "username": "ada"}}},
        {"update_id": 2, "message": {"message_id": 3, "chat": {"id": 55, "type": "private"}, "date": 1793000001,
                                     "text": "other chat", "from": {"id": 6, "first_name": "Bob"}}},
        {"update_id": 3, "message": {"message_id": 8, "chat": CHAT, "date": 1793000002, "text": "again",
                                     "from": {"id": 5, "first_name": "Ada", "last_name": "L", "username": "ada"},
                                     "reply_to_message": {"message_id": 7, "chat": CHAT, "date": 1793000000}}},
    ]
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeTelegram)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("AMOORION_SECRET_TELEGRAM_URI", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("AMOORION_SECRET_TELEGRAM_TOKEN", "123:tok")
    monkeypatch.setenv("AMOORION_SECRET_TELEGRAM_CHAT", "-1009")
    yield open_plugin("telegram", open_vault(VaultLink(kind="env")))
    server.shutdown()


def test_post_and_reply(telegram):
    posted = telegram.post(Post(title="News", text="hello", tags=["amoorion"]))
    assert posted.text == "News\n\nhello\n#amoorion" and posted.id == "100"
    assert posted.url == "https://t.me/c/9/100" and posted.author.handle == "amoorion_bot"
    answer = telegram.reply(posted, "more")
    assert answer.reply_to == "100"


def test_read_only_this_chat_newest_first(telegram):
    read = telegram.read(5)
    assert [message.text for message in read] == ["again", "hi bot"]
    assert read[0].reply_to == "7" and read[0].author.name == "Ada L"
    assert telegram.read(1)[0].text == "again"


def test_errors_never_show_the_token(telegram, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_TELEGRAM_CHAT", "-1")
    with pytest.raises(AmoorionError, match="chat not found") as failed:
        telegram.post(Post(text="x"))
    assert "123:tok" not in str(failed.value)
    monkeypatch.setenv("AMOORION_SECRET_TELEGRAM_URI", "http://127.0.0.1:9")
    with pytest.raises(AmoorionError, match="unreachable") as failed:
        telegram.post(Post(text="x"))
    assert "123:tok" not in str(failed.value)


def test_limits(telegram):
    with pytest.raises(AmoorionError, match="takes 4096"):
        telegram.post(Post(text="x" * 4097))
    with pytest.raises(AmoorionError, match="number of the message"):
        telegram.reply(telegram.read(1)[0].model_copy(update={"id": "abc"}), "x")


def test_helpers():
    assert link({"username": "chan"}, 5) == "https://t.me/chan/5"
    assert link({"id": 42}, 5) is None
    assert compose(Post(text="t", links=["https://a"])) == "t\nhttps://a"


def test_delete_a_message(telegram):
    gone = telegram.post(Post(text="oops"))
    telegram.delete(gone)
    assert FakeTelegram.sent == []
    with pytest.raises(AmoorionError, match="message to delete not found"):
        telegram.delete(gone)
    assert telegram.profile() == "chat-1009"
