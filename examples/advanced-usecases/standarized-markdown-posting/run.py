"""A directory of Markdown files as the source of posts."""

from pathlib import Path

from amoorion import Amoorion
from amoorion.utilities import post_from_markdown

# Each Markdown file says where it goes, in its head.
amo = Amoorion()
# Sorted: the posts go out in a known order.
for file in sorted(Path(__file__).parent.glob("*.md")):
    post, to = post_from_markdown(file)
    for result in amo.publish(to=to, **post.model_dump()):
        print(
            file.name,
            result["platform"],
            result["ok"],
            result["message"]["text"][:40],
        )
