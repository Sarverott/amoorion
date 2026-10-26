"""Inbox: the messages amoorion received, kept across platforms (decision Q11).

A small SQLite database. What `read` fetches and what hooks receive is kept
here once (by platform and id), so the CLI, API and MCP can look through
everything in one place. Where it lives is set in `.env`:

    AMOORION_INBOX=<path>   default: $XDG_DATA_HOME/amoorion/inbox.sqlite3

Rules acting on what arrives come in phase 5.
"""

import os
import sqlite3
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from amoorion.models import Message

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    platform TEXT NOT NULL,
    id TEXT NOT NULL,
    at TEXT NOT NULL,
    message TEXT NOT NULL,
    PRIMARY KEY (platform, id)
)
"""


def default_path() -> Path:
    load_dotenv(Path.cwd() / ".env", override=False)
    if path := os.environ.get("AMOORION_INBOX"):
        return Path(path).expanduser()
    data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return data / "amoorion" / "inbox.sqlite3"


class Inbox:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_path()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.execute(SCHEMA)
        return connection

    def keep(self, messages: Iterable[Message]) -> list[Message]:
        """Keep the messages not kept yet; a message without an id gets one. Returns them as kept."""
        kept = []
        now = datetime.now(UTC)
        with self._connect() as connection:
            for message in messages:
                if message.id is None:
                    message = message.model_copy(update={"id": uuid.uuid4().hex})
                at = (message.created_at or now).astimezone(UTC).isoformat()
                connection.execute(
                    "INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?)",
                    (message.platform, message.id, at, message.model_dump_json()),
                )
                kept.append(message)
        connection.close()
        return kept

    def list(self, platform: str | None = None, limit: int = 20) -> list[Message]:
        """Newest first."""
        query = "SELECT message FROM messages"
        args: tuple[str | int, ...] = ()
        if platform:
            query += " WHERE platform = ?"
            args = (platform,)
        connection = self._connect()
        try:
            rows = connection.execute(query + " ORDER BY at DESC, rowid DESC LIMIT ?", (*args, limit)).fetchall()
        finally:
            connection.close()
        return [Message.model_validate_json(row[0]) for row in rows]
