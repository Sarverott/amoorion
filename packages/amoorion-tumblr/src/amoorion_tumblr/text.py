"""A post as Neue Post Format blocks, and back."""

from typing import Any

from amoorion.models import Post


def blocks(post: Post) -> list[dict[str, Any]]:
    """A post as Neue Post Format blocks: a heading, the text, links and so on."""

    content: list[dict[str, Any]] = []

    if post.title:
        content.append(
            {
                "type": "text",
                "subtype": "heading1",
                "text": post.title,
            }
        )

    content += [
        {"type": "text", "text": paragraph}
        for paragraph in post.text.split("\n\n")
        if paragraph
    ]

    content += [{"type": "link", "url": link} for link in post.links]

    return content


def text_of(content: list[dict[str, Any]]) -> str:
    """Neue Post Format blocks back as plain text."""

    parts = []

    for block in content:
        if block.get("type") == "text":
            parts.append(
                block.get(
                    "text",
                    "",
                )
            )

        elif block.get("type") == "link":
            parts.append(
                block.get(
                    "url",
                    "",
                )
            )

    return "\n\n".join(part for part in parts if part)
