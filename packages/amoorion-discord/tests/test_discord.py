"""The discord plugins against a local server shaped like Discord's REST API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest
from amoorion_discord.text import compose

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault

BOT = {
    "id": "1",
    "username": "amoorion",
    "global_name": "Amoorion",
}


class FakeDiscord(BaseHTTPRequestHandler):
    messages: list[dict] = []
    bodies: list[dict] = []

    def _send(
        self,
        status,
        body,
    ):

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.end_headers()

        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):

        url = urlparse(self.path)

        if self.headers.get("Authorization") != "Bot tok":
            return self._send(
                401,
                {
                    "message": "401: Unauthorized",
                    "code": 0,
                },
            )

        if url.path == "/api/channels/42":
            return self._send(
                200,
                {
                    "id": "42",
                    "guild_id": "9",
                },
            )

        if url.path == "/api/channels/42/messages":
            limit = int(parse_qs(url.query)["limit"][0])

            return self._send(
                200,
                self.messages[::-1][:limit],
            )

        self._send(
            404,
            {
                "message": "Unknown Channel",
                "code": 10003,
            },
        )

    def do_POST(self):

        url = urlparse(self.path)

        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))

        self.bodies.append(body)

        if url.path == "/api/webhooks/5/hooktoken":
            if parse_qs(url.query).get("wait") != ["true"]:
                return self._send(
                    204,
                    {},
                )

            created = {
                "id": "w1",
                "channel_id": "42",
                "guild_id": "9",
                "content": body["content"],
                "author": {
                    "id": "5",
                    "username": "Captain Hook",
                },
                "timestamp": "2026-10-26T12:00:00+00:00",
            }

            return self._send(
                200,
                created,
            )

        if url.path.startswith("/api/webhooks/"):
            return self._send(
                401,
                {
                    "message": "Invalid Webhook Token",
                    "code": 50027,
                },
            )

        if self.headers.get("Authorization") != "Bot tok":
            return self._send(
                401,
                {
                    "message": "401: Unauthorized",
                    "code": 0,
                },
            )

        if url.path != "/api/channels/42/messages":
            return self._send(
                404,
                {
                    "message": "Unknown Channel",
                    "code": 10003,
                },
            )

        number = str(len(self.messages) + 1)

        created = {
            "id": number,
            "channel_id": "42",
            "content": body["content"],
            "author": BOT,
            "timestamp": "2026-10-26T12:00:00+00:00",
        }

        if "message_reference" in body:
            created["message_reference"] = body["message_reference"]

        self.messages.append(created)

        self._send(
            200,
            created,
        )

    def do_DELETE(self):

        url = urlparse(self.path)

        if url.path == "/api/webhooks/5/hooktoken/messages/w1":
            return self._send(
                204,
                {},
            )

        if self.headers.get("Authorization") != "Bot tok":
            return self._send(
                401,
                {
                    "message": "401: Unauthorized",
                    "code": 0,
                },
            )

        number = url.path.rsplit("/", 1)[-1]

        if not url.path.startswith("/api/channels/42/messages/") or not any(
            m["id"] == number for m in self.messages
        ):
            return self._send(
                404,
                {
                    "message": "Unknown Message",
                    "code": 10008,
                },
            )

        FakeDiscord.messages = [m for m in self.messages if m["id"] != number]

        self.send_response(204)

        self.end_headers()

    def log_message(
        self,
        *args,
    ):

        pass


@pytest.fixture
def server(monkeypatch):

    FakeDiscord.messages, FakeDiscord.bodies = [], []

    server = ThreadingHTTPServer(
        (
            "127.0.0.1",
            0,
        ),
        FakeDiscord,
    )

    threading.Thread(
        target=server.serve_forever,
        daemon=True,
    ).start()

    base = f"http://127.0.0.1:{server.server_port}/api"

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_URI",
        base,
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_TOKEN",
        "tok",
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_CHANNEL",
        "42",
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_WEBHOOK_URL",
        f"{base}/webhooks/5/hooktoken",
    )

    yield base

    server.shutdown()


@pytest.fixture
def vault():

    return open_vault(VaultLink(kind="env"))


def test_bot_post_read_reply(
    server,
    vault,
):

    discord = open_plugin(
        "discord",
        vault,
    )

    posted = discord.post(
        Post(
            title="News",
            text="hello @everyone",
            tags=["amoorion"],
        )
    )

    assert posted.text == "**News**\n\nhello @everyone\n#amoorion"

    assert posted.url == "https://discord.com/channels/9/42/1"

    answer = discord.reply(
        posted,
        "more",
    )

    assert answer.reply_to == "1"

    read = discord.read(5)

    assert [message.text for message in read] == ["more", posted.text]

    assert read[0].author.name == "Amoorion"

    assert all(
        body["allowed_mentions"] == {"parse": []} for body in FakeDiscord.bodies
    )


def test_bot_limit_and_errors(
    server,
    vault,
    monkeypatch,
):

    discord = open_plugin(
        "discord",
        vault,
    )

    with pytest.raises(AmoorionError, match="takes 2000 characters"):
        discord.post(Post(text="x" * 2001))

    assert FakeDiscord.bodies == []

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_CHANNEL",
        "7",
    )

    with pytest.raises(AmoorionError, match="Unknown Channel"):
        open_plugin(
            "discord",
            vault,
        ).read()

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_TOKEN",
        "bad",
    )

    with pytest.raises(AmoorionError, match="Unauthorized"):
        open_plugin(
            "discord",
            vault,
        ).read()


def test_webhook_posts_only(
    server,
    vault,
):

    webhook = open_plugin(
        "discord-webhook",
        vault,
    )

    posted = webhook.post(Post(text="from a hook"))

    assert (
        posted.text == "from a hook" and posted.author.handle == "Captain Hook"
    )

    assert posted.url == "https://discord.com/channels/9/42/w1"

    with pytest.raises(AmoorionError, match="can't read"):
        webhook.read()


def test_webhook_token_never_in_errors(
    server,
    vault,
    monkeypatch,
):

    monkeypatch.setenv(
        "AMOORION_SECRET_DISCORD_WEBHOOK_URL",
        f"{server}/webhooks/5/wrongtoken",
    )

    with pytest.raises(AmoorionError, match="Invalid Webhook Token") as failed:
        open_plugin(
            "discord-webhook",
            vault,
        ).post(Post(text="x"))

    assert "wrongtoken" not in str(failed.value)


def test_compose():

    assert compose(Post(text="t", links=["https://a"])) == "t\nhttps://a"


def test_bot_deletes(
    server,
    vault,
):

    discord = open_plugin(
        "discord",
        vault,
    )

    gone, kept = (
        discord.post(Post(text="oops")),
        discord.post(Post(text="fine")),
    )

    discord.delete(gone)

    assert [m.id for m in discord.read()] == [kept.id]

    with pytest.raises(AmoorionError, match="Unknown Message"):
        discord.delete(gone)

    assert discord.profile() == "channel-42"


def test_webhook_deletes_what_it_posted(
    server,
    vault,
):

    webhook = open_plugin(
        "discord-webhook",
        vault,
    )

    webhook.delete(webhook.post(Post(text="oops")))

    assert webhook.profile() == "webhook-5"
