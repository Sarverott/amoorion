"""Inbox: the messages amoorion received, kept across platforms (decision Q11).

A small SQLite database. What `read` fetches and what hooks receive is kept
here once (by platform and id), so the CLI, API and MCP can look through
everything in one place. Where it lives is set in `.env`:

    AMOORION_INBOX=<path>   default: $XDG_DATA_HOME/amoorion/inbox.sqlite3

Rules acting on what arrives: see amoorion.workflows.
"""

import os
import sqlite3
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from amoorion.models import Message

SCHEMA = Path(__file__).with_name("schema.messages.sql").read_text()


def default_path() -> Path:
    """Where the inbox is: AMOORION_INBOX (also from `.env`), or the user's data directory."""

    load_dotenv(
        Path.cwd() / ".env",
        override=False,
    )

    if path := os.environ.get("AMOORION_INBOX"):
        return Path(path).expanduser()

    data = Path(
        os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    )

    return data / "amoorion" / "inbox.sqlite3"


class Inbox:
    """Every message read or received, of all platforms and hooks, in one SQLite file.

    Connections are short: each operation opens one, so several processes can share it.
    """

    def __init__(
        self,
        path: Path | None = None,
    ) -> None:
        """The inbox at `path`, by default the one of the environment."""

        self.path = path or default_path()

    def _connect(self) -> sqlite3.Connection:
        """A connection, with the directory and table made when missing."""

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        connection = sqlite3.connect(self.path)

        connection.execute(SCHEMA)

        return connection

    def keep(
        self,
        messages: Iterable[Message],
    ) -> list[Message]:
        """Keep the messages not kept yet; a message without an id gets one. Returns them as kept."""

        kept = []

        now = datetime.now(UTC)

        with self._connect() as connection:
            for message in messages:
                if message.id is None:
                    message = message.model_copy(
                        update={"id": uuid.uuid4().hex}
                    )

                at = (message.created_at or now).astimezone(UTC).isoformat()

                connection.execute(
                    "INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?)",
                    (
                        message.platform,
                        message.id,
                        at,
                        message.model_dump_json(),
                    ),
                )

                kept.append(message)

        connection.close()

        return kept

    def _messages(
        self,
        query: str,
        args: tuple[str | int, ...],
        limit: int,
    ) -> "list[Message]":
        """Newest first."""

        connection = self._connect()

        try:
            rows = connection.execute(
                query + " ORDER BY at DESC, rowid DESC LIMIT ?",
                (
                    *args,
                    limit,
                ),
            ).fetchall()
        finally:
            connection.close()

        return [Message.model_validate_json(row[0]) for row in rows]

    def list(
        self,
        platform: str | None = None,
        limit: int = 20,
    ) -> "list[Message]":
        """Newest first."""

        if platform:
            return self._messages(
                "SELECT message FROM messages WHERE platform = ?",
                (platform,),
                limit,
            )

        return self._messages(
            "SELECT message FROM messages",
            (),
            limit,
        )

    def search(
        self,
        text: str,
        platform: str | None = None,
        limit: int = 20,
    ) -> "list[Message]":
        """Messages holding this text, in any case (of ASCII letters: SQLite's LIKE); newest first."""

        pattern = (
            "%"
            + text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            + "%"
        )

        query = "SELECT message FROM messages WHERE json_extract(message, '$.text') LIKE ? ESCAPE '\\'"

        if platform:
            return self._messages(
                query + " AND platform = ?",
                (
                    pattern,
                    platform,
                ),
                limit,
            )

        return self._messages(
            query,
            (pattern,),
            limit,
        )
