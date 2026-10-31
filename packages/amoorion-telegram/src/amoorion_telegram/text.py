"""A post as Telegram takes it, and links to messages."""

from typing import Any

from amoorion.models import Post

LIMIT = 4096


def compose(post: Post) -> str:
    """A post as this platform's text: title, text, links and tags."""

    text = "\n\n".join(part for part in (post.title, post.text) if part)

    if post.links:
        text += "\n" + "\n".join(post.links)

    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)

    return text


def link(
    chat: dict[str, Any],
    number: int,
) -> str | None:
    """The address of a message: public chats by name, private supergroups by number."""

    if chat.get("username"):
        return f"https://t.me/{chat['username']}/{number}"

    chat_id = str(
        chat.get(
            "id",
            "",
        )
    )

    if chat_id.startswith(
        "-100"
    ):  # a supergroup or channel without a public name
        return f"https://t.me/c/{chat_id[4:]}/{number}"

    return None
