"""x plugin: the X (twitter) API v2, OAuth 1.0a user context.

Secrets (`x/<key>`): `api-key`, `api-secret`, `access-token`,
`access-secret`; optional `uri` (default https://api.x.com).
"""

from datetime import UTC, datetime
from typing import Any, ClassVar

import requests
from requests_oauthlib import OAuth1

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_x.text import LIMIT, compose, weight

SERVICE = "https://api.x.com"


class X(HttpPlugin):
    """X (Twitter) through API v2, signed with OAuth 1 by four keys from the vault.

    Reading needs a paid tier of the API; posting works on the free one.
    """

    name: ClassVar[str] = "x"
    description: ClassVar[str] = "X (twitter) API v2: post, read, reply, delete"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = (
        "api-key",
        "api-secret",
        "access-token",
        "access-secret",
    )

    _me: dict[str, Any] | None = None

    def reason(
        self,
        response: requests.Response,
    ) -> str:
        """What went wrong, from this platform's own form of errors."""

        try:
            errors = response.json().get("errors")
        except (ValueError, AttributeError):
            errors = None

        if (
            errors
            and isinstance(errors, list)
            and isinstance(errors[0], dict)
            and errors[0].get("message")
        ):
            return "; ".join(error.get("message", "") for error in errors)

        return super().reason(response)

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

        auth = OAuth1(
            self.secret("api-key"),
            self.secret("api-secret"),
            self.secret("access-token"),
            self.secret("access-secret"),
        )

        return self.request(
            method,
            base + path,
            auth=auth,
            **kwargs,
        )

    def _user(self) -> dict[str, Any]:
        """The account of the keys, asked once."""

        if self._me is None:
            self._me = self._call("GET", "/2/users/me")["data"]

        return self._me

    def _tweet(
        self,
        text: str,
        links: list[str],
        reply_to: str | None = None,
    ) -> Message:
        """Publish one post, after checking its weighted length."""

        if weight(text, links) > LIMIT:
            raise AmoorionError(
                f"x takes {LIMIT} weighted characters, this is {weight(text, links)}"
            )

        body: dict[str, Any] = {"text": text}

        if reply_to:
            body["reply"] = {"in_reply_to_tweet_id": reply_to}

        data = self._call("POST", "/2/tweets", json=body)["data"]

        user = self._user()

        return Message(
            platform=self.name,
            text=text,
            id=data["id"],
            url=f"https://x.com/{user['username']}/status/{data['id']}",
            author=Account(
                platform=self.name,
                handle=user["username"],
                name=user.get("name"),
            ),
            reply_to=reply_to,
            created_at=datetime.now(UTC),
        )

    def post(
        self,
        post: Post,
    ) -> Message:
        """Publish a post; answers the message as the platform stored it."""

        return self._tweet(
            compose(post),
            post.links,
        )

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:
        """The latest messages, newest first, at most `limit`."""

        user = self._user()

        answer = self._call(
            "GET",
            f"/2/users/{user['id']}/tweets",
            params={
                "max_results": min(
                    max(
                        limit,
                        5,
                    ),
                    100,
                ),
                "tweet.fields": "created_at,referenced_tweets",
            },
        )

        messages = []

        for tweet in answer.get("data", [])[:limit]:
            replied = next(
                (
                    ref["id"]
                    for ref in tweet.get("referenced_tweets", [])
                    if ref.get("type") == "replied_to"
                ),
                None,
            )

            messages.append(
                Message(
                    platform=self.name,
                    text=tweet["text"],
                    id=tweet["id"],
                    url=f"https://x.com/{user['username']}/status/{tweet['id']}",
                    author=Account(
                        platform=self.name,
                        handle=user["username"],
                        name=user.get("name"),
                    ),
                    reply_to=replied,
                    created_at=tweet.get("created_at"),
                )
            )

        return messages

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:
        """Answer a message by its id; answers the new message."""

        if not to.id:
            raise AmoorionError("x needs the id of the post to reply to")

        return self._tweet(
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
            raise AmoorionError("x needs the id of the post to delete")

        if (
            not self._call("DELETE", f"/2/tweets/{message.id}")
            .get("data", {})
            .get("deleted")
        ):
            raise AmoorionError(f"x did not delete {message.id}")

    def profile(self) -> str:
        """The name this account gets in the dataset."""

        return self._user()["username"]
