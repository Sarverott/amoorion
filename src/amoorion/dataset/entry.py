"""One post in a profile's index, and the file names of ids."""

import hashlib
import re
from datetime import datetime
from typing import Literal

from amoorion.core import Model

SAFE = re.compile(r"[^A-Za-z0-9._@-]+")


def safe(name: str) -> str:
    """A file name for an id or profile: readable, and different for different ids."""

    cleaned = SAFE.sub("_", name).strip("._") or "_"

    if cleaned == name:
        return name

    return f"{cleaned[:80]}-{hashlib.sha256(name.encode()).hexdigest()[:8]}"


class Entry(Model):
    """One post in a profile's index."""

    id: str
    file: str
    state: Literal["present", "gone", "deleted"] = "present"
    url: str | None = None
    created_at: datetime | None = None
    text: str = ""
    seen_at: datetime | None = None
    deleted_at: datetime | None = None
