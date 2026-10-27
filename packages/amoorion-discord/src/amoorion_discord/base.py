"""discord plugins: a bot through the REST API, and a channel webhook.

`discord` secrets (`discord/<key>`): `token` (the bot's), `channel` (the
channel's id); optional `uri` (the API with its version). It posts, reads,
replies and deletes in that channel (others' messages too, with Manage
Messages).

`discord-webhook` secret: `url`, the channel's webhook URL; it posts, and
deletes what it posted.

Both send at most 2000 characters, and no mention pings anyone.
"""

from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

SERVICE = "https://discord.com/api/v10"
LIMIT = 2000
# Mentions in the text stay text: no @everyone, no roles, no users pinged.
NO_PINGS = {"allowed_mentions": {"parse": []}}


def compose(post: Post) -> str:
    parts = [f"**{post.title}**" if post.title else None, post.text]
    text = "\n\n".join(part for part in parts if part)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


def checked(text: str) -> str:
    if len(text) > LIMIT:
        raise AmoorionError(f"discord takes {LIMIT} characters, this is {len(text)}")
    return text


def message(platform: str, data: dict[str, Any], guild: str | None) -> Message:
    author = data.get("author") or {}
    reference = data.get("message_reference") or {}
    return Message(
        platform=platform,
        text=data.get("content", ""),
        id=data["id"],
        url=f"https://discord.com/channels/{guild or '@me'}/{data['channel_id']}/{data['id']}",
        author=Account(platform=platform, handle=author.get("username", ""), name=author.get("global_name")),
        reply_to=reference.get("message_id"),
        created_at=data.get("timestamp"),
    )


class Discord(HttpPlugin):
    name: ClassVar[str] = "discord"
    description: ClassVar[str] = "Discord bot in one channel (REST API): post, read, reply, delete"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = ("token", "channel")

    _guild: str | None = None

    def _call(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            base = self.secret("uri").rstrip("/")
        except AmoorionError:
            base = SERVICE
        headers = {"Authorization": f"Bot {self.secret('token')}"}
        return self.request(method, f"{base}{path}", headers=headers, **kwargs)

    def _channel(self) -> str:
        return f"/channels/{self.secret('channel')}"

    def _guild_id(self) -> str | None:
        # Message links need the server (guild) of the channel; asked once.
        if self._guild is None:
            self._guild = self._call("GET", self._channel()).get("guild_id") or ""
        return self._guild or None

    def _send(self, text: str, reply_to: str | None = None) -> Message:
        body: dict[str, Any] = {"content": checked(text)} | NO_PINGS
        if reply_to:
            body["message_reference"] = {"message_id": reply_to}
        return message(self.name, self._call("POST", f"{self._channel()}/messages", json=body), self._guild_id())

    def post(self, post: Post) -> Message:
        return self._send(compose(post))

    def read(self, limit: int = 20) -> list[Message]:
        found = self._call("GET", f"{self._channel()}/messages", params={"limit": min(limit, 100)})
        return [message(self.name, data, self._guild_id()) for data in found]

    def reply(self, to: Message, text: str) -> Message:
        if not to.id:
            raise AmoorionError("discord needs the id of the message to reply to")
        return self._send(text, reply_to=to.id)

    def delete(self, message: Message) -> None:
        if not message.id:
            raise AmoorionError("discord needs the id of the message to delete")
        self._call("DELETE", f"{self._channel()}/messages/{message.id}")

    def profile(self) -> str:
        return f"channel-{self.secret('channel')}"


class DiscordWebhook(HttpPlugin):
    name: ClassVar[str] = "discord-webhook"
    description: ClassVar[str] = "Discord channel webhook, no bot: post, delete what it posted"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST, Capability.DELETE})
    secrets: ClassVar[tuple[str, ...]] = ("url",)

    def hidden(self) -> list[str]:
        # .../webhooks/<id>/<token>: the token is the secret part.
        return [self.secret("url").rstrip("/").rsplit("/", 1)[-1]]

    def post(self, post: Post) -> Message:
        body = {"content": checked(compose(post))} | NO_PINGS
        # wait=true: Discord answers with the message instead of nothing.
        sent = self.request("POST", self.secret("url"), params={"wait": "true"}, json=body)
        return message(self.name, sent, sent.get("guild_id"))

    def delete(self, message: Message) -> None:
        if not message.id:
            raise AmoorionError("discord-webhook needs the id of the message to delete")
        self.request("DELETE", f"{self.secret('url').rstrip('/')}/messages/{message.id}")

    def profile(self) -> str:
        # .../webhooks/<id>/<token>: the id names it, the token stays secret.
        return "webhook-" + self.secret("url").rstrip("/").rsplit("/", 2)[-2]
