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

SERVICE = "https://api.telegram.org"
LIMIT = 4096


def compose(post: Post) -> str:
    text = "\n\n".join(part for part in (post.title, post.text) if part)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


def link(chat: dict[str, Any], number: int) -> str | None:
    if chat.get("username"):
        return f"https://t.me/{chat['username']}/{number}"
    chat_id = str(chat.get("id", ""))
    if chat_id.startswith("-100"):  # a supergroup or channel without a public name
        return f"https://t.me/c/{chat_id[4:]}/{number}"
    return None


class Telegram(HttpPlugin):
    name: ClassVar[str] = "telegram"
    description: ClassVar[str] = "Telegram bot in one chat (Bot API): post, read, reply"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = ("token", "chat")

    def hidden(self) -> list[str]:
        return [self.secret("token")]

    def reason(self, response: requests.Response) -> str:
        try:
            return str(response.json()["description"])
        except (ValueError, KeyError, TypeError):
            return super().reason(response)

    def _call(self, method: str, **body: Any) -> Any:
        try:
            base = self.secret("uri").rstrip("/")
        except AmoorionError:
            base = SERVICE
        answer = self.request("POST", f"{base}/bot{self.secret('token')}/{method}", json=body)
        if not answer.get("ok"):
            raise AmoorionError(f"telegram {method}: {answer.get('description', 'not ok')}")
        return answer["result"]

    def _mine(self, chat: dict[str, Any]) -> bool:
        wanted = self.secret("chat")
        return str(chat.get("id")) == wanted or "@" + str(chat.get("username")) == wanted

    def _message(self, data: dict[str, Any]) -> Message:
        sender = data.get("from") or {}
        sender_chat = data.get("sender_chat") or {}
        handle = sender.get("username") or sender_chat.get("username") or str(sender.get("id") or sender_chat.get("id") or "")
        name = " ".join(filter(None, (sender.get("first_name"), sender.get("last_name")))) or sender_chat.get("title")
        reply = data.get("reply_to_message") or {}
        return Message(
            platform=self.name,
            text=data.get("text") or data.get("caption") or "",
            id=str(data["message_id"]),
            url=link(data.get("chat") or {}, data["message_id"]),
            author=Account(platform=self.name, handle=handle, name=name or None),
            reply_to=str(reply["message_id"]) if reply else None,
            created_at=datetime.fromtimestamp(data["date"], UTC) if "date" in data else None,
        )

    def _send(self, text: str, reply_to: str | None = None) -> Message:
        if len(text) > LIMIT:
            raise AmoorionError(f"telegram takes {LIMIT} characters, this is {len(text)}")
        body: dict[str, Any] = {"chat_id": self.secret("chat"), "text": text}
        if reply_to:
            body["reply_parameters"] = {"message_id": int(reply_to)}
        return self._message(self._call("sendMessage", **body))

    def post(self, post: Post) -> Message:
        return self._send(compose(post))

    def read(self, limit: int = 20) -> list[Message]:
        updates = self._call("getUpdates", allowed_updates=["message", "channel_post"])
        said = [update.get("message") or update.get("channel_post") for update in updates]
        mine = [data for data in said if data and self._mine(data.get("chat") or {})]
        return [self._message(data) for data in mine[::-1][:limit]]

    def reply(self, to: Message, text: str) -> Message:
        if not to.id or not to.id.isdigit():
            raise AmoorionError("telegram needs the number of the message to reply to")
        return self._send(text, reply_to=to.id)
