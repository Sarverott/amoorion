"""What the bot and the webhook say: at most 2000 characters, and no mention pings anyone."""

from typing import Any

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post

LIMIT = 2000
# Mentions in the text stay text: no @everyone, no roles, no users pinged.
NO_PINGS = {"allowed_mentions": {"parse": []}}


def compose(post: Post) -> str:
    parts = [f"**{post.title}**" if post.title else None, post.text]
    text = "\n\n".join(part for part in parts if part)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


def checked(text: str) -> str:
    if len(text) > LIMIT:
        raise AmoorionError(f"discord takes {LIMIT} characters, this is {len(text)}")
    return text


def message(platform: str, data: dict[str, Any], guild: str | None) -> Message:
    author = data.get("author") or {}
    reference = data.get("message_reference") or {}
    return Message(
        platform=platform,
        text=data.get("content", ""),
        id=data["id"],
        url=f"https://discord.com/channels/{guild or '@me'}/{data['channel_id']}/{data['id']}",
        author=Account(platform=platform, handle=author.get("username", ""), name=author.get("global_name")),
        reply_to=reference.get("message_id"),
        created_at=data.get("timestamp"),
    )
