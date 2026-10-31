"""mastodon plugin: the REST API of a Mastodon (or compatible) server.

Secrets (`mastodon/<key>`): `uri` (the server, e.g. https://mastodon.social)
and `token` (an access token of an application made in the account's
Preferences → Development, scopes `read:accounts read:statuses
write:statuses`). The server's own character limit is asked once and checked
before sending; links count as 23 characters, as Mastodon counts them.
"""

import uuid
from typing import Any, ClassVar
from urllib.parse import urlparse

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_mastodon.text import compose, length, to_text

DEFAULT_LIMIT = 500


class Mastodon(HttpPlugin):
    """Mastodon's REST API on the instance the vault names.

    The length limit is the instance's own, asked once.
    """

    name: ClassVar[str] = "mastodon"
    description: ClassVar[str] = (
        "Mastodon (REST API): post, read, reply, delete"
    )
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = (
        "uri",
        "token",
    )

    _account: dict[str, Any] | None = None
    _limit: int | None = None

    def _call(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """One authorized request to the platform's API; its address can be replaced by the `uri` secret."""

        headers = {
            "Authorization": f"Bearer {self.secret('token')}"
        } | kwargs.pop("headers", {})

        return self.request(
            method,
            f"{self.secret('uri').rstrip('/')}{path}",
            headers=headers,
            **kwargs,
        )

    def _me(self) -> dict[str, Any]:
        """The account of the token, asked once."""

        if self._account is None:
            self._account = self._call(
                "GET",
                "/api/v1/accounts/verify_credentials",
            )

        return self._account

    def _max_characters(self) -> int:
        """This instance's limit, asked once; the usual one when it doesn't say."""

        if self._limit is None:
            try:
                instance = self._call(
                    "GET",
                    "/api/v2/instance",
                )

                self._limit = int(
                    instance["configuration"]["statuses"]["max_characters"]
                )
            except (AmoorionError, KeyError, TypeError, ValueError):
                self._limit = DEFAULT_LIMIT

        return self._limit

    def _message(
        self,
        status: dict[str, Any],
    ) -> Message:
        """The platform's answer as a `Message`."""

        account = status.get("account") or {}

        return Message(
            platform=self.name,
            text=to_text(
                status.get(
                    "content",
                    "",
                )
            ),
            id=status["id"],
            url=status.get("url"),
            author=Account(
                platform=self.name,
                handle=account.get(
                    "acct",
                    "",
                ),
                name=account.get("display_name") or None,
            ),
            reply_to=status.get("in_reply_to_id"),
            created_at=status.get("created_at"),
        )

    def _status(
        self,
        text: str,
        links: list[str],
        reply_to: str | None = None,
    ) -> Message:
        """Publish one status, after checking its length."""

        limit = self._max_characters()

        if length(text, links) > limit:
            raise AmoorionError(
                f"this mastodon server takes {limit} characters, this is {length(text, links)}"
            )

        body = {"status": text} | (
            {"in_reply_to_id": reply_to} if reply_to else {}
        )

        # The same key on a retried request makes the server post only once.
        status = self._call(
            "POST",
            "/api/v1/statuses",
            json=body,
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )

        message = self._message(status)

        # The server answers with HTML; keep the text as it was sent.
        return message.model_copy(update={"text": text})

    def post(
        self,
        post: Post,
    ) -> Message:
        """Publish a post; answers the message as the platform stored it."""

        return self._status(
            compose(post),
            post.links,
        )

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:
        """The latest messages, newest first, at most `limit`."""

        statuses = self._call(
            "GET",
            f"/api/v1/accounts/{self._me()['id']}/statuses",
            params={
                "limit": min(
                    limit,
                    40,
                )
            },
        )

        return [self._message(status) for status in statuses]

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:
        """Answer a message by its id; answers the new message."""

        if not to.id:
            raise AmoorionError(
                "mastodon needs the id of the status to reply to"
            )

        return self._status(
            text,
            [],
            reply_to=to.id,
        )

    def delete(
        self,
        message: Message,
    ) -> None:
        """Delete a message by its id."""

        if not message.id:
            raise AmoorionError("mastodon needs the id of the status to delete")

        self._call(
            "DELETE",
            f"/api/v1/statuses/{message.id}",
        )

    def profile(self) -> str:
        """The name this account gets in the dataset."""

        return f"{self._me()['acct']}@{urlparse(self.secret('uri')).hostname}"
