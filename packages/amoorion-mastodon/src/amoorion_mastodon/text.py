"""A status's text: what goes out, what comes back as HTML, its length."""

from html.parser import HTMLParser

from amoorion.models import Post

LINK_LENGTH = 23


class _Text(HTMLParser):
    """Status HTML to plain text: paragraphs and line breaks kept, tags dropped."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            self.parts.append("\n")
        elif tag == "p" and self.parts:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def to_text(html: str) -> str:
    parser = _Text()
    parser.feed(html)
    return "".join(parser.parts).strip()


def compose(post: Post) -> str:
    parts = [part for part in (post.title, post.text) if part]
    text = "\n\n".join(parts)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text


def length(text: str, links: list[str]) -> int:
    for link in links:
        text = text.replace(link, "x" * LINK_LENGTH)
    return len(text)
