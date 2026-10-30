"""What both web apps show: amoorion on the dryrun platform, nothing goes anywhere."""

import os
import tempfile
from pathlib import Path

from amoorion import Amoorion

# A public Space must never hold real accounts: its own vault, and only dryrun.
scratch = Path(tempfile.mkdtemp())
os.environ["AMOORION_VAULT"] = "env"
os.environ["AMOORION_INBOX"] = str(scratch / "inbox.sqlite3")
os.environ["AMOORION_DATASET"] = str(scratch / "dataset")

amo = Amoorion().use("dryrun")


def post(text: str) -> list[list[str]]:
    """Publish and read back; rows of (id, text), newest first."""
    if text.strip():
        amo.publish(text=text)
    return [[message["id"], message["text"]] for message in amo.read(limit=20)]
