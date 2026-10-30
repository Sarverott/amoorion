"""bluesky plugin: the AT Protocol's XRPC API over HTTP.

Secrets (`bluesky/<key>`): `username` (handle or e-mail), `password` (an app
password, not the account's), optional `uri` (the PDS, default
https://bsky.social). Links and tags of a post are appended to its text and
made clickable with facets; posts longer than 300 graphemes are refused
before sending.
"""

from datetime import UTC, datetime
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_bluesky.text import LIMIT, compose, graphemes

SERVICE = "https://bsky.social"


class Bluesky(HttpPlugin):
    name: ClassVar[str] = "bluesky"
    description: ClassVar[str] = "Bluesky (AT Protocol): post, read, reply, delete"
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
        return self.request(method, f"{self.service}/xrpc/{nsid}", headers=headers, **kwargs)

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

    def delete(self, message: Message) -> None:
        if not message.id or not message.id.startswith("at://"):
            raise AmoorionError("bluesky needs the id (at:// URI) of the post to delete")
        session = self._login()
        repo, collection, rkey = message.id.removeprefix("at://").split("/", 2)
        if repo not in (session["did"], session["handle"]):
            raise AmoorionError(f"bluesky deletes only posts of {session['handle']}")
        self._call("POST", "com.atproto.repo.deleteRecord", json={"repo": session["did"], "collection": collection, "rkey": rkey})

    def profile(self) -> str:
        return self._login()["handle"]
