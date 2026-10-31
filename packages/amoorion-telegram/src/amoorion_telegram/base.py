"""telegram plugin: a bot in one chat, through the Bot API.

Secrets (`telegram/<key>`): `token` (from @BotFather), `chat` (the chat's id
or a public chat's `@username`); optional `uri` (the Bot API server). The
token is part of every URL, so errors hide it. Reading asks `getUpdates`
without confirming them, so the same updates stay readable for 24 hours.
"""

from datetime import UTC, datetime
from typing import Any, ClassVar

import requests

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_telegram.text import LIMIT, compose, link

SERVICE = "https://api.telegram.org"


class Telegram(HttpPlugin):
    """A Telegram bot in one chat, through the Bot API.

    The token is part of every URL, which is why it is `hidden` from errors. A bot can
    only read updates it hasn't confirmed yet, not a chat's history.
    """

    name: ClassVar[str] = "telegram"
    description: ClassVar[str] = (
        "Telegram bot in one chat (Bot API): post, read, reply, delete"
    )
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = (
        "token",
        "chat",
    )

    def hidden(self) -> list[str]:
        """What must never appear in an error: it is in the URLs."""

        return [self.secret("token")]

    def reason(
        self,
        response: requests.Response,
    ) -> str:
        """What went wrong, from this platform's own form of errors."""

        try:
            return str(response.json()["description"])
        except (ValueError, KeyError, TypeError):
            return super().reason(response)

    def _call(
        self,
        method: str,
        **body: Any,
    ) -> Any:
        """One authorized request to the platform's API; its address can be replaced by the `uri` secret."""

        try:
            base = self.secret("uri").rstrip("/")
        except AmoorionError:
            base = SERVICE

        answer = self.request(
            "POST",
            f"{base}/bot{self.secret('token')}/{method}",
            json=body,
        )

        if not answer.get("ok"):
            raise AmoorionError(
                f"telegram {method}: {answer.get('description', 'not ok')}"
            )

        return answer["result"]

    def _mine(
        self,
        chat: dict[str, Any],
    ) -> bool:
        """Whether an update comes from the chat of the vault, by id or `@name`."""

        wanted = self.secret("chat")

        return (
            str(chat.get("id")) == wanted
            or "@" + str(chat.get("username")) == wanted
        )

    def _message(
        self,
        data: dict[str, Any],
    ) -> Message:
        """The platform's answer as a `Message`."""

        sender = data.get("from") or {}

        sender_chat = data.get("sender_chat") or {}

        handle = (
            sender.get("username")
            or sender_chat.get("username")
            or str(sender.get("id") or sender_chat.get("id") or "")
        )

        name = " ".join(
            filter(None, (sender.get("first_name"), sender.get("last_name")))
        ) or sender_chat.get("title")

        reply = data.get("reply_to_message") or {}

        return Message(
            platform=self.name,
            text=data.get("text") or data.get("caption") or "",
            id=str(data["message_id"]),
            url=link(
                data.get("chat") or {},
                data["message_id"],
            ),
            author=Account(
                platform=self.name,
                handle=handle,
                name=name or None,
            ),
            reply_to=str(reply["message_id"]) if reply else None,
            created_at=datetime.fromtimestamp(
                data["date"],
                UTC,
            )
            if "date" in data
            else None,
        )

    def _send(
        self,
        text: str,
        reply_to: str | None = None,
    ) -> Message:
        """Send a text, optionally as a reply; answers the message."""

        if len(text) > LIMIT:
            raise AmoorionError(
                f"telegram takes {LIMIT} characters, this is {len(text)}"
            )

        body: dict[str, Any] = {
            "chat_id": self.secret("chat"),
            "text": text,
        }

        if reply_to:
            body["reply_parameters"] = {"message_id": int(reply_to)}

        return self._message(
            self._call(
                "sendMessage",
                **body,
            )
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

        updates = self._call(
            "getUpdates",
            allowed_updates=[
                "message",
                "channel_post",
            ],
        )

        said = [
            update.get("message") or update.get("channel_post")
            for update in updates
        ]

        mine = [
            data for data in said if data and self._mine(data.get("chat") or {})
        ]

        return [self._message(data) for data in mine[::-1][:limit]]

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:
        """Answer a message by its id; answers the new message."""

        if not to.id or not to.id.isdigit():
            raise AmoorionError(
                "telegram needs the number of the message to reply to"
            )

        return self._send(
            text,
            reply_to=to.id,
        )

    def delete(
        self,
        message: Message,
    ) -> None:
        """Its own messages always; others' as a group admin, and in groups only within 48 hours."""

        if not message.id or not message.id.isdigit():
            raise AmoorionError(
                "telegram needs the number of the message to delete"
            )

        self._call(
            "deleteMessage",
            chat_id=self.secret("chat"),
            message_id=int(message.id),
        )

    def profile(self) -> str:
        """The name this account gets in the dataset."""

        return f"chat{self.secret('chat')}"
