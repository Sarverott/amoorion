"""tumblr plugin: the Tumblr API v2, Neue Post Format, OAuth 1.0a.

Secrets (`tumblr/<key>`): `consumer-key`, `consumer-secret`, `token`,
`token-secret`, `blog`; optional `uri` (default https://api.tumblr.com).
"""

from datetime import UTC, datetime
from typing import Any, ClassVar

import requests
from requests_oauthlib import OAuth1

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_tumblr.text import blocks, text_of

SERVICE = "https://api.tumblr.com"


class Tumblr(HttpPlugin):
    name: ClassVar[str] = "tumblr"
    description: ClassVar[str] = "Tumblr API v2: post, read, delete"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(
        {
            Capability.POST,
            Capability.READ,
            Capability.DELETE,
        }
    )
    secrets: ClassVar[tuple[str, ...]] = (
        "consumer-key",
        "consumer-secret",
        "token",
        "token-secret",
        "blog",
    )

    def reason(
        self,
        response: requests.Response,
    ) -> str:

        try:
            body = response.json()

            errors, meta = body.get("errors"), body.get("meta") or {}
        except (ValueError, AttributeError):
            return super().reason(response)

        if errors and isinstance(errors, list) and isinstance(errors[0], dict):
            return (
                errors[0].get("detail")
                or errors[0].get("title")
                or meta.get("msg", "")
            )

        return meta.get("msg") or super().reason(response)

    @property
    def blog(self) -> str:

        return self.secret("blog")

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

        auth = OAuth1(
            self.secret("consumer-key"),
            self.secret("consumer-secret"),
            self.secret("token"),
            self.secret("token-secret"),
        )

        return self.request(
            method,
            f"{base}/v2/blog/{self.blog}{path}",
            auth=auth,
            **kwargs,
        ).get(
            "response",
            {},
        )

    def _author(
        self,
        name: str | None = None,
    ) -> Account:

        return Account(
            platform=self.name,
            handle=name or self.blog,
        )

    def post(
        self,
        post: Post,
    ) -> Message:

        body: dict[str, Any] = {
            "content": blocks(post),
            "state": "published",
        }

        if post.tags:
            body["tags"] = ",".join(tag.lstrip("#") for tag in post.tags)

        created = self._call(
            "POST",
            "/posts",
            json=body,
        )

        post_id = str(created.get("id_string") or created["id"])

        blog_name = self.blog.removesuffix(".tumblr.com")

        return Message(
            platform=self.name,
            text=text_of(body["content"]),
            id=post_id,
            url=f"https://www.tumblr.com/{blog_name}/{post_id}",
            author=self._author(blog_name),
            created_at=datetime.now(UTC),
        )

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:

        answer = self._call(
            "GET",
            "/posts",
            params={
                "npf": "true",
                "limit": min(
                    limit,
                    20,
                ),
            },
        )

        return [
            Message(
                platform=self.name,
                text=text_of(item.get("content", [])),
                id=str(item.get("id_string") or item["id"]),
                url=item.get("post_url"),
                author=self._author(item.get("blog_name")),
                created_at=datetime.fromtimestamp(item["timestamp"], UTC)
                if item.get("timestamp")
                else None,
            )
            for item in answer.get("posts", [])
        ]

    def delete(
        self,
        message: Message,
    ) -> None:

        if not message.id or not message.id.isdigit():
            raise AmoorionError("tumblr needs the number of the post to delete")

        self._call(
            "POST",
            "/post/delete",
            json={"id": message.id},
        )

    def profile(self) -> str:

        return self.blog.removesuffix(".tumblr.com")
