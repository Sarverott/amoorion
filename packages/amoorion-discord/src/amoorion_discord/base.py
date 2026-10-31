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
    """A Discord bot writing into one channel, with mentions turned off.

    Its token and the channel come from the vault.
    """

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
        """One authorized request to the platform's API; its address can be replaced by the `uri` secret."""

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
        """The API path of the channel."""

        return f"/channels/{self.secret('channel')}"

    def _guild_id(self) -> str | None:
        """The server of the channel, asked once; it is needed for links to messages."""

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
        """Send a text, optionally as a reply; answers the message."""

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
        """Publish a post; answers the message as the platform stored it."""

        return self._send(compose(post))

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:
        """The latest messages, newest first, at most `limit`."""

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
        """Answer a message by its id; answers the new message."""

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
        """Delete a message by its id."""

        if not message.id:
            raise AmoorionError("discord needs the id of the message to delete")

        self._call(
            "DELETE",
            f"{self._channel()}/messages/{message.id}",
        )

    def profile(self) -> str:
        """The name this account gets in the dataset."""

        return f"channel-{self.secret('channel')}"
