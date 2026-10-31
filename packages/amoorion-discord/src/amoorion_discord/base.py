"""discord plugin: a bot through the REST API.

Secrets (`discord/<key>`): `token` (the bot's), `channel` (the channel's id);
optional `uri` (the API with its version). It posts, reads, replies and deletes
in that channel (others' messages too, with Manage Messages).
"""

from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_discord.text import NO_PINGS, checked, compose, message

SERVICE = "https://discord.com/api/v10"


class Discord(HttpPlugin):
    name: ClassVar[str] = "discord"
    description: ClassVar[str] = (
        "Discord bot in one channel (REST API): post, read, reply, delete"
    )
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = (
        "token",
        "channel",
    )

    _guild: str | None = None

    def _call(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:

        try:
            base = self.secret("uri").rstrip("/")
        except AmoorionError:
            base = SERVICE

        headers = {"Authorization": f"Bot {self.secret('token')}"}

        return self.request(
            method,
            f"{base}{path}",
            headers=headers,
            **kwargs,
        )

    def _channel(self) -> str:

        return f"/channels/{self.secret('channel')}"

    def _guild_id(self) -> str | None:

        # Message links need the server (guild) of the channel; asked once.
        if self._guild is None:
            self._guild = (
                self._call("GET", self._channel()).get("guild_id") or ""
            )

        return self._guild or None

    def _send(
        self,
        text: str,
        reply_to: str | None = None,
    ) -> Message:

        body: dict[str, Any] = {"content": checked(text)} | NO_PINGS

        if reply_to:
            body["message_reference"] = {"message_id": reply_to}

        return message(
            self.name,
            self._call(
                "POST",
                f"{self._channel()}/messages",
                json=body,
            ),
            self._guild_id(),
        )

    def post(
        self,
        post: Post,
    ) -> Message:

        return self._send(compose(post))

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:

        found = self._call(
            "GET",
            f"{self._channel()}/messages",
            params={
                "limit": min(
                    limit,
                    100,
                )
            },
        )

        return [message(self.name, data, self._guild_id()) for data in found]

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:

        if not to.id:
            raise AmoorionError(
                "discord needs the id of the message to reply to"
            )

        return self._send(
            text,
            reply_to=to.id,
        )

    def delete(
        self,
        message: Message,
    ) -> None:

        if not message.id:
            raise AmoorionError("discord needs the id of the message to delete")

        self._call(
            "DELETE",
            f"{self._channel()}/messages/{message.id}",
        )

    def profile(self) -> str:

        return f"channel-{self.secret('channel')}"
