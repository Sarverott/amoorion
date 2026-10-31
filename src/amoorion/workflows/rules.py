"""Rules: steps run for each message of the inbox a rule matches, once per message.

Remembered in the inbox's database. `$text`, `$author`, `$platform`, `$id` and `$url`
are the message's.
"""

import sqlite3
from pathlib import Path

import yaml
from pydantic import Field

from amoorion.core import AmoorionError, Model
from amoorion.inbox import Inbox
from amoorion.models import Message
from amoorion.workflows.base import Step

SCHEMA = Path(__file__).with_name("schema.handled.sql").read_text()


class Rule(Model):
    """What to do (`steps`) with which messages of the inbox (`platform`, `contains`)."""

    name: str = Field(min_length=1)
    steps: list[Step] = Field(
        [],
        description="methods to run; a rule of a Python workflow may have none",
    )
    platform: str | None = Field(
        None,
        description="only messages of this platform (a hook is hook:<name>)",
    )
    contains: str | None = Field(
        None,
        description="only messages with this text, in any case",
    )


def load_rules(path: str | Path) -> list[Rule]:
    """Rules of a YAML file (`rules: [...]`, a list, or one rule), or of every `*.rule.yml` in a directory."""

    path = Path(path).expanduser()

    if path.is_dir():
        return [
            rule
            for file in sorted(path.glob("*.rule.yml"))
            for rule in load_rules(file)
        ]

    if not path.is_file():
        raise AmoorionError(f"no rules at {path}")

    data = yaml.safe_load(path.read_text()) or []

    if isinstance(data, dict):
        data = data.get(
            "rules",
            [data],
        )

    return [Rule.model_validate(rule) for rule in data]


def matches(
    rule: Rule,
    message: Message,
) -> bool:
    """Whether a rule is about a message; `contains` ignores case."""

    if rule.platform and message.platform != rule.platform:
        return False

    return (
        not rule.contains or rule.contains.casefold() in message.text.casefold()
    )


def known_of(message: Message) -> dict[str, str]:
    """What steps of a rule may use of the message: `$text`, `$author`, `$platform`, `$id`, `$url`."""

    return {
        "text": message.text,
        "author": message.author.handle if message.author else "",
        "platform": message.platform,
        "id": message.id or "",
        "url": message.url or "",
    }


def _connect(inbox: Inbox) -> sqlite3.Connection:
    """A connection to the inbox, with the table of handled messages made when missing."""

    connection = inbox._connect()

    connection.execute(SCHEMA)

    return connection


def handled(
    inbox: Inbox,
    rule: str,
    message: Message,
) -> bool:
    """Whether this rule has already dealt with this message."""

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
    """Remember that it has; asking twice is harmless."""

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
