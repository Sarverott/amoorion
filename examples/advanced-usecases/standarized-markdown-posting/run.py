"""A directory of Markdown files as the source of posts."""

import os
import tempfile
from pathlib import Path

from amoorion import Amoorion
from amoorion.utilities import post_from_markdown

os.environ |= {"AMOORION_VAULT": "env", "AMOORION_INBOX": tempfile.mktemp(), "AMOORION_DATASET": tempfile.mkdtemp()}

amo = Amoorion()
for file in sorted(Path(__file__).parent.glob("*.md")):
    post, to = post_from_markdown(file)
    for result in amo.publish(to=to, **post.model_dump()):
        print(file.name, result["platform"], result["ok"], result["message"]["text"][:40])
