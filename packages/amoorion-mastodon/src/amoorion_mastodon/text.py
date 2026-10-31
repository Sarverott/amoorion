"""A status's text: what goes out, what comes back as HTML, its length."""

from html.parser import HTMLParser

from amoorion.models import Post

LINK_LENGTH = 23


class _Text(HTMLParser):
    """Status HTML to plain text: paragraphs and line breaks kept, tags dropped."""

    def __init__(self) -> None:
        """Start with nothing collected."""

        super().__init__()

        self.parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Line breaks and paragraphs become new lines."""

        if tag == "br":
            self.parts.append("\n")

        elif tag == "p" and self.parts:
            self.parts.append("\n\n")

    def handle_data(
        self,
        data: str,
    ) -> None:
        """Text stays as it is."""

        self.parts.append(data)


def to_text(html: str) -> str:
    """Mastodon's HTML of a status as plain text."""

    parser = _Text()

    parser.feed(html)

    return "".join(parser.parts).strip()


def compose(post: Post) -> str:
    """A post as this platform's text: title, text, links and tags."""

    parts = [part for part in (post.title, post.text) if part]

    text = "\n\n".join(parts)

    if post.links:
        text += "\n" + "\n".join(post.links)

    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)

    return text


def length(
    text: str,
    links: list[str],
) -> int:
    """The length as Mastodon counts: each link as a fixed number of characters."""

    for link in links:
        # A link counts the same, whatever its length, on Mastodon.
        text = text.replace(
            link,
            "x" * LINK_LENGTH,
        )

    return len(text)
