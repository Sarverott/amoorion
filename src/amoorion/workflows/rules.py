"""Rules: steps run for each message of the inbox a rule matches, once per message.

Remembered in the inbox's database. `$text`, `$author`, `$platform`, `$id` and `$url`
are the message's.
"""

import sqlite3
from pathlib import Path

from pydantic import Field

from amoorion.core import Model
from amoorion.inbox import Inbox
from amoorion.models import Message
from amoorion.workflows.base import Step

SCHEMA = Path(__file__).with_name("schema.handled.sql").read_text()


class Rule(Model):
    name: str = Field(min_length=1)
    steps: list[Step] = Field(min_length=1)
    platform: str | None = Field(
        None,
        description="only messages of this platform (a hook is hook:<name>)",
    )
    contains: str | None = Field(
        None,
        description="only messages with this text, in any case",
    )


def matches(
    rule: Rule,
    message: Message,
) -> bool:

    if rule.platform and message.platform != rule.platform:
        return False

    return (
        not rule.contains or rule.contains.casefold() in message.text.casefold()
    )


def known_of(message: Message) -> dict[str, str]:

    return {
        "text": message.text,
        "author": message.author.handle if message.author else "",
        "platform": message.platform,
        "id": message.id or "",
        "url": message.url or "",
    }


def _connect(inbox: Inbox) -> sqlite3.Connection:

    connection = inbox._connect()

    connection.execute(SCHEMA)

    return connection


def handled(
    inbox: Inbox,
    rule: str,
    message: Message,
) -> bool:

    connection = _connect(inbox)

    try:
        row = connection.execute(
            "SELECT 1 FROM handled WHERE rule = ? AND platform = ? AND id = ?",
            (
                rule,
                message.platform,
                message.id,
            ),
        ).fetchone()
    finally:
        connection.close()

    return row is not None


def mark_handled(
    inbox: Inbox,
    rule: str,
    message: Message,
) -> None:

    connection = _connect(inbox)

    try:
        with connection:
            connection.execute(
                "INSERT OR IGNORE INTO handled VALUES (?, ?, ?)",
                (
                    rule,
                    message.platform,
                    message.id,
                ),
            )
    finally:
        connection.close()
