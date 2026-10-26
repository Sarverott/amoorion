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

SERVICE = "https://api.x.com"
LIMIT = 280
LINK_LENGTH = 23
# Code point ranges counted once; everything else counts twice.
LIGHT = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))


def weight(text: str, links: list[str]) -> int:
    for link in links:
        text = text.replace(link, "")
    light = sum(1 for char in text if any(low <= ord(char) <= high for low, high in LIGHT))
    return light + 2 * (len(text) - light) + LINK_LENGTH * len(links)


def compose(post: Post) -> str:
    text = "\n\n".join(part for part in (post.title, post.text) if part)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


class X(HttpPlugin):
    name: ClassVar[str] = "x"
    description: ClassVar[str] = "X (twitter) API v2: post, read, reply"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = ("api-key", "api-secret", "access-token", "access-secret")

    _me: dict[str, Any] | None = None

    def reason(self, response: requests.Response) -> str:
        try:
            errors = response.json().get("errors")
        except (ValueError, AttributeError):
            errors = None
        if errors and isinstance(errors, list) and isinstance(errors[0], dict) and errors[0].get("message"):
            return "; ".join(error.get("message", "") for error in errors)
        return super().reason(response)

    def _call(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            base = self.secret("uri").rstrip("/")
        except AmoorionError:
            base = SERVICE
        auth = OAuth1(
            self.secret("api-key"), self.secret("api-secret"), self.secret("access-token"), self.secret("access-secret")
        )
        return self.request(method, base + path, auth=auth, **kwargs)

    def _user(self) -> dict[str, Any]:
        if self._me is None:
            self._me = self._call("GET", "/2/users/me")["data"]
        return self._me

    def _tweet(self, text: str, links: list[str], reply_to: str | None = None) -> Message:
        if weight(text, links) > LIMIT:
            raise AmoorionError(f"x takes {LIMIT} weighted characters, this is {weight(text, links)}")
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
            author=Account(platform=self.name, handle=user["username"], name=user.get("name")),
            reply_to=reply_to,
            created_at=datetime.now(UTC),
        )

    def post(self, post: Post) -> Message:
        return self._tweet(compose(post), post.links)

    def read(self, limit: int = 20) -> list[Message]:
        user = self._user()
        answer = self._call(
            "GET",
            f"/2/users/{user['id']}/tweets",
            params={"max_results": min(max(limit, 5), 100), "tweet.fields": "created_at,referenced_tweets"},
        )
        messages = []
        for tweet in answer.get("data", [])[:limit]:
            replied = next(
                (ref["id"] for ref in tweet.get("referenced_tweets", []) if ref.get("type") == "replied_to"), None
            )
            messages.append(
                Message(
                    platform=self.name,
                    text=tweet["text"],
                    id=tweet["id"],
                    url=f"https://x.com/{user['username']}/status/{tweet['id']}",
                    author=Account(platform=self.name, handle=user["username"], name=user.get("name")),
                    reply_to=replied,
                    created_at=tweet.get("created_at"),
                )
            )
        return messages

    def reply(self, to: Message, text: str) -> Message:
        if not to.id:
            raise AmoorionError("x needs the id of the post to reply to")
        return self._tweet(text, [], reply_to=to.id)
