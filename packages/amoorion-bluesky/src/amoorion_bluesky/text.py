"""A post as Bluesky takes it: its text, facets and length."""

import unicodedata
from typing import Any

from amoorion.models import Post

LIMIT = 300  # graphemes


def graphemes(text: str) -> int:
    """Approximate count: combining marks, joiners and variation selectors join the previous character."""

    return sum(
        1
        for char in text
        if not (
            unicodedata.combining(char)
            or char in "‍︎️"
            or 0x1F3FB <= ord(char) <= 0x1F3FF
        )
    )


def compose(post: Post) -> tuple[str, list[dict[str, Any]]]:
    """Text of the post with its links and tags, and facets marking them (byte offsets)."""

    parts: list[tuple[str, dict[str, Any] | None]] = []

    if post.title:
        parts.append(
            (
                post.title + "\n\n",
                None,
            )
        )

    parts.append(
        (
            post.text,
            None,
        )
    )

    for link in post.links:
        parts.append(
            (
                "\n" + link,
                {
                    "$type": "app.bsky.richtext.facet#link",
                    "uri": link,
                },
            )
        )

    for index, tag in enumerate(post.tags):
        tag = tag.lstrip("#")

        parts.append(
            (
                "\n" if index == 0 else " ",
                None,
            )
        )

        parts.append(
            (
                "#" + tag,
                {
                    "$type": "app.bsky.richtext.facet#tag",
                    "tag": tag,
                },
            )
        )

    text, facets, offset = "", [], 0

    for piece, feature in parts:
        encoded = piece.encode()

        if feature:
            start = offset + (1 if piece.startswith("\n") else 0)

            facets.append(
                {
                    "index": {
                        "byteStart": start,
                        "byteEnd": offset + len(encoded),
                    },
                    "features": [feature],
                }
            )

        text += piece

        offset += len(encoded)

    return text, facets
