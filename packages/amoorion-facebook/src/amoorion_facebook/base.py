"""facebook plugin: a Facebook Page through the Graph API.

Secrets (`facebook/<key>`): `page-id`, `page-token`; optional `uri` (the
Graph API with its version). Replies are comments on the post.
"""

from datetime import UTC, datetime
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

SERVICE = "https://graph.facebook.com/v24.0"


def compose(post: Post) -> str:
    text = "\n\n".join(part for part in (post.title, post.text) if part)
    if post.links:
        text += "\n\n" + "\n".join(post.links)
    if post.tags:
        text += "\n\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


class Facebook(HttpPlugin):
    name: ClassVar[str] = "facebook"
    description: ClassVar[str] = "Facebook Page (Graph API): post, read, reply as comment, delete"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = ("page-id", "page-token")

    def _call(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            base = self.secret("uri").rstrip("/")
        except AmoorionError:
            base = SERVICE
        # The token goes in a header, so it never lands in URLs or server logs.
        headers = {"Authorization": f"Bearer {self.secret('page-token')}"}
        return self.request(method, f"{base}/{path}", headers=headers, **kwargs)

    def _page(self) -> Account:
        return Account(platform=self.name, handle=self.secret("page-id"))

    def post(self, post: Post) -> Message:
        text = compose(post)
        created = self._call("POST", f"{self.secret('page-id')}/feed", data={"message": text})
        return Message(
            platform=self.name,
            text=text,
            id=created["id"],
            url=f"https://www.facebook.com/{created['id']}",
            author=self._page(),
            created_at=datetime.now(UTC),
        )

    def read(self, limit: int = 20) -> list[Message]:
        answer = self._call(
            "GET",
            f"{self.secret('page-id')}/posts",
            params={"fields": "id,message,created_time,permalink_url", "limit": min(limit, 100)},
        )
        return [
            Message(
                platform=self.name,
                text=item.get("message", ""),
                id=item["id"],
                url=item.get("permalink_url"),
                author=self._page(),
                created_at=item.get("created_time"),
            )
            for item in answer.get("data", [])
        ]

    def reply(self, to: Message, text: str) -> Message:
        if not to.id:
            raise AmoorionError("facebook needs the id of the post to comment on")
        created = self._call("POST", f"{to.id}/comments", data={"message": text})
        return Message(
            platform=self.name,
            text=text,
            id=created["id"],
            url=f"https://www.facebook.com/{created['id']}",
            author=self._page(),
            reply_to=to.id,
            created_at=datetime.now(UTC),
        )

    def delete(self, message: Message) -> None:
        """A post of the page or a comment: both are deleted by their id."""
        if not message.id:
            raise AmoorionError("facebook needs the id of the post or comment to delete")
        if not self._call("DELETE", message.id).get("success"):
            raise AmoorionError(f"facebook did not delete {message.id}")

    def profile(self) -> str:
        return self.secret("page-id")
