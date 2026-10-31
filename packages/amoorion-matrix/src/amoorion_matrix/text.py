"""A post as a Matrix room takes it, and ids in paths."""

from urllib.parse import quote

from amoorion.models import Post


def compose(post: Post) -> str:
    """A post as this platform's text: title, text, links and tags."""

    text = "\n\n".join(part for part in (post.title, post.text) if part)

    if post.links:
        text += "\n" + "\n".join(post.links)

    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)

    return text


def part(value: str) -> str:
    """Ids like !room:server or $event go into paths quoted whole."""

    return quote(
        value,
        safe="",
    )
