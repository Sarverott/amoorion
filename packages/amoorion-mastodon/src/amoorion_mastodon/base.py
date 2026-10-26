"""mastodon plugin: the REST API of a Mastodon (or compatible) server.

Secrets (`mastodon/<key>`): `uri` (the server, e.g. https://mastodon.social)
and `token` (an access token of an application made in the account's
Preferences → Development, scopes `read:accounts read:statuses
write:statuses`). The server's own character limit is asked once and checked
before sending; links count as 23 characters, as Mastodon counts them.
"""

import uuid
from html.parser import HTMLParser
from typing import Any, ClassVar

import requests

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, Plugin

LINK_LENGTH = 23
DEFAULT_LIMIT = 500


class _Text(HTMLParser):
    """Status HTML to plain text: paragraphs and line breaks kept, tags dropped."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            self.parts.append("\n")
        elif tag == "p" and self.parts:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def to_text(html: str) -> str:
    parser = _Text()
    parser.feed(html)
    return "".join(parser.parts).strip()


def compose(post: Post) -> str:
    parts = [part for part in (post.title, post.text) if part]
    text = "\n\n".join(parts)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


def length(text: str, links: list[str]) -> int:
    for link in links:
        text = text.replace(link, "x" * LINK_LENGTH)
    return len(text)


class Mastodon(Plugin):
    name: ClassVar[str] = "mastodon"
    description: ClassVar[str] = "Mastodon (REST API): post, read, reply"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = ("uri", "token")

    _account: dict[str, Any] | None = None
    _limit: int | None = None

    def _call(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = {"Authorization": f"Bearer {self.secret('token')}"} | kwargs.pop("headers", {})
        url = f"{self.secret('uri').rstrip('/')}{path}"
        try:
            response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        except requests.RequestException as error:
            raise AmoorionError(f"mastodon unreachable: {error}") from None
        if not response.ok:
            try:
                reason = response.json().get("error")
            except ValueError:
                reason = response.text[:200]
            raise AmoorionError(f"mastodon {path} answered {response.status_code}: {reason}")
        return response.json()

    def _me(self) -> dict[str, Any]:
        if self._account is None:
            self._account = self._call("GET", "/api/v1/accounts/verify_credentials")
        return self._account

    def _max_characters(self) -> int:
        if self._limit is None:
            try:
                instance = self._call("GET", "/api/v2/instance")
                self._limit = int(instance["configuration"]["statuses"]["max_characters"])
            except (AmoorionError, KeyError, TypeError, ValueError):
                self._limit = DEFAULT_LIMIT
        return self._limit

    def _message(self, status: dict[str, Any]) -> Message:
        account = status.get("account") or {}
        return Message(
            platform=self.name,
            text=to_text(status.get("content", "")),
            id=status["id"],
            url=status.get("url"),
            author=Account(platform=self.name, handle=account.get("acct", ""), name=account.get("display_name") or None),
            reply_to=status.get("in_reply_to_id"),
            created_at=status.get("created_at"),
        )

    def _status(self, text: str, links: list[str], reply_to: str | None = None) -> Message:
        limit = self._max_characters()
        if length(text, links) > limit:
            raise AmoorionError(f"this mastodon server takes {limit} characters, this is {length(text, links)}")
        body = {"status": text} | ({"in_reply_to_id": reply_to} if reply_to else {})
        # The same key on a retried request makes the server post only once.
        status = self._call("POST", "/api/v1/statuses", json=body, headers={"Idempotency-Key": str(uuid.uuid4())})
        message = self._message(status)
        # The server answers with HTML; keep the text as it was sent.
        return message.model_copy(update={"text": text})

    def post(self, post: Post) -> Message:
        return self._status(compose(post), post.links)

    def read(self, limit: int = 20) -> list[Message]:
        statuses = self._call("GET", f"/api/v1/accounts/{self._me()['id']}/statuses", params={"limit": min(limit, 40)})
        return [self._message(status) for status in statuses]

    def reply(self, to: Message, text: str) -> Message:
        if not to.id:
            raise AmoorionError("mastodon needs the id of the status to reply to")
        return self._status(text, [], reply_to=to.id)
