"""A post as X takes it: its text and weighted length."""

from amoorion.models import Post

LIMIT = 280
LINK_LENGTH = 23
# Code point ranges counted once; everything else counts twice.
LIGHT = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))


def weight(text: str, links: list[str]) -> int:
    for link in links:
        text = text.replace(link, "")
    light = sum(1 for char in text if any(low <= ord(char) <= high for low, high in LIGHT))
    return light + 2 * (len(text) - light) + LINK_LENGTH * len(links)


def compose(post: Post) -> str:
    text = "\n\n".join(part for part in (post.title, post.text) if part)
    if post.links:
        text += "\n" + "\n".join(post.links)
    if post.tags:
        text += "\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return text
