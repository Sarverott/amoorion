"""bluesky plugin: the AT Protocol's XRPC API over HTTP.

Secrets (`bluesky/<key>`): `username` (handle or e-mail), `password` (an app
password, not the account's), optional `uri` (the PDS, default
https://bsky.social). Links and tags of a post are appended to its text and
made clickable with facets; posts longer than 300 graphemes are refused
before sending.
"""

import unicodedata
from datetime import UTC, datetime
from typing import Any, ClassVar

import requests

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins.base import Capability, Plugin

SERVICE = "https://bsky.social"
LIMIT = 300  # graphemes


def graphemes(text: str) -> int:
    """Approximate count: combining marks, joiners and variation selectors join the previous character."""
    return sum(
        1
        for char in text
        if not (unicodedata.combining(char) or char in "‍︎️" or 0x1F3FB <= ord(char) <= 0x1F3FF)
    )


def compose(post: Post) -> tuple[str, list[dict[str, Any]]]:
    """Text of the post with its links and tags, and facets marking them (byte offsets)."""
    parts: list[tuple[str, dict[str, Any] | None]] = []
    if post.title:
        parts.append((post.title + "\n\n", None))
    parts.append((post.text, None))
    for link in post.links:
        parts.append(("\n" + link, {"$type": "app.bsky.richtext.facet#link", "uri": link}))
    for index, tag in enumerate(post.tags):
        tag = tag.lstrip("#")
        parts.append(("\n" if index == 0 else " ", None))
        parts.append(("#" + tag, {"$type": "app.bsky.richtext.facet#tag", "tag": tag}))
    text, facets, offset = "", [], 0
    for piece, feature in parts:
        encoded = piece.encode()
        if feature:
            start = offset + (1 if piece.startswith("\n") else 0)
            facets.append({"index": {"byteStart": start, "byteEnd": offset + len(encoded)}, "features": [feature]})
        text += piece
        offset += len(encoded)
    return text, facets


class Bluesky(Plugin):
    name: ClassVar[str] = "bluesky"
    description: ClassVar[str] = "Bluesky (AT Protocol): post, read, reply"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = ("username", "password")

    _session: dict[str, Any] | None = None

    @property
    def service(self) -> str:
        try:
            return self.secret("uri").rstrip("/")
        except AmoorionError:
            return SERVICE

    def _call(self, method: str, nsid: str, **kwargs: Any) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._session['accessJwt']}"} if self._session else {}
        try:
            response = requests.request(method, f"{self.service}/xrpc/{nsid}", headers=headers, timeout=30, **kwargs)
        except requests.RequestException as error:
            raise AmoorionError(f"bluesky unreachable: {error}") from None
        if not response.ok:
            try:
                reason = response.json().get("message") or response.json().get("error")
            except ValueError:
                reason = response.text[:200]
            raise AmoorionError(f"bluesky {nsid} answered {response.status_code}: {reason}")
        return response.json() if response.content else {}

    def _login(self) -> dict[str, Any]:
        if self._session is None:
            identifier, password = self.secret("username"), self.secret("password")
            self._session = self._call(
                "POST", "com.atproto.server.createSession", json={"identifier": identifier, "password": password}
            )
        return self._session

    def _url(self, uri: str, handle: str) -> str:
        return f"https://bsky.app/profile/{handle}/post/{uri.rsplit('/', 1)[-1]}"

    def _create(self, record: dict[str, Any]) -> Message:
        session = self._login()
        record = {"$type": "app.bsky.feed.post", "createdAt": datetime.now(UTC).isoformat()} | record
        if graphemes(record["text"]) > LIMIT:
            raise AmoorionError(f"bluesky takes {LIMIT} graphemes, this is {graphemes(record['text'])}")
        created = self._call(
            "POST",
            "com.atproto.repo.createRecord",
            json={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
        )
        return Message(
            platform=self.name,
            text=record["text"],
            id=created["uri"],
            url=self._url(created["uri"], session["handle"]),
            author=Account(platform=self.name, handle=session["handle"]),
            reply_to=record.get("reply", {}).get("parent", {}).get("uri"),
            created_at=datetime.fromisoformat(record["createdAt"]),
        )

    def post(self, post: Post) -> Message:
        text, facets = compose(post)
        return self._create({"text": text} | ({"facets": facets} if facets else {}))

    def read(self, limit: int = 20) -> list[Message]:
        session = self._login()
        feed = self._call("GET", "app.bsky.feed.getAuthorFeed", params={"actor": session["did"], "limit": limit})
        messages = []
        for item in feed.get("feed", []):
            post, record = item["post"], item["post"].get("record", {})
            author = post.get("author", {})
            messages.append(
                Message(
                    platform=self.name,
                    text=record.get("text", ""),
                    id=post["uri"],
                    url=self._url(post["uri"], author.get("handle", session["handle"])),
                    author=Account(platform=self.name, handle=author.get("handle", ""), name=author.get("displayName")),
                    reply_to=record.get("reply", {}).get("parent", {}).get("uri"),
                    created_at=record.get("createdAt"),
                )
            )
        return messages

    def reply(self, to: Message, text: str) -> Message:
        if not to.id:
            raise AmoorionError("bluesky needs the id (at:// URI) of the post to reply to")
        self._login()
        posts = self._call("GET", "app.bsky.feed.getPosts", params={"uris": to.id}).get("posts", [])
        if not posts:
            raise AmoorionError(f"bluesky has no post {to.id}")
        parent = {"uri": posts[0]["uri"], "cid": posts[0]["cid"]}
        root = posts[0].get("record", {}).get("reply", {}).get("root", parent)
        return self._create({"text": text, "reply": {"root": root, "parent": parent}})
