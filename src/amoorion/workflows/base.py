"""Workflows and rules: what amoorion does by itself.

A workflow is a list of steps, each a method with its params. Text in params may
name what is known, `$last` being the text of what the previous step gave:

    steps:
      - {method: compose, params: {prompt: "Announce: $text"}}
      - {method: publish, params: {text: "$last", to: [mastodon]}}

A rule runs steps for each message of the inbox it matches, once per message
(remembered in the inbox's database). `$text`, `$author`, `$platform`, `$id` and `$url`
are the message's. Values are only ever put in as text, never evaluated.
"""

import sqlite3
from string import Template
from typing import Any

from pydantic import Field

from amoorion.core import AmoorionError, Model
from amoorion.inbox import Inbox
from amoorion.models import Message

SCHEMA = "CREATE TABLE IF NOT EXISTS handled (rule TEXT NOT NULL, platform TEXT NOT NULL, id TEXT NOT NULL, PRIMARY KEY (rule, platform, id))"


class Step(Model):
    method: str
    params: dict[str, Any] = {}


class StepResult(Model):
    method: str
    ok: bool
    result: Any = None
    error: str | None = None


class Rule(Model):
    name: str = Field(min_length=1)
    steps: list[Step] = Field(min_length=1)
    platform: str | None = Field(None, description="only messages of this platform (a hook is hook:<name>)")
    contains: str | None = Field(None, description="only messages with this text, in any case")


def fill(value: Any, known: dict[str, str]) -> Any:
    """Put what is known into the text of params; unknown names stay as written."""
    if isinstance(value, str):
        return Template(value).safe_substitute(known)
    if isinstance(value, list):
        return [fill(item, known) for item in value]
    if isinstance(value, dict):
        return {key: fill(item, known) for key, item in value.items()}
    return value


def text_of(result: Any) -> str:
    """The text a method's answer carries: a message, a composition, a result's message, the first of a list."""
    if isinstance(result, list):
        return text_of(result[0]) if result else ""
    if isinstance(result, Model):
        for name in ("text", "message"):
            value = getattr(result, name, None)
            if isinstance(value, str):
                return value
            if isinstance(value, Model):
                return text_of(value)
    return ""


def run_steps(steps: list[Step], call: Any, known: dict[str, str] | None = None) -> list[StepResult]:
    """Run until the end or the first failure; `call(method, params)` returns a method's models."""
    known = dict(known or {})
    results = []
    for step in steps:
        try:
            answer = call(step.method, fill(step.params, known))
        except (AmoorionError, ValueError) as error:
            results.append(StepResult(method=step.method, ok=False, error=str(error)))
            break
        failed = [item.error or "failed" for item in (answer if isinstance(answer, list) else [answer]) if getattr(item, "ok", True) is False]
        known["last"] = text_of(answer)
        results.append(StepResult(method=step.method, ok=not failed, result=_plain(answer), error="; ".join(failed) or None))
        if failed:
            break
    return results


def _plain(answer: Any) -> Any:
    if isinstance(answer, list):
        return [item.model_dump(mode="json") for item in answer]
    return answer.model_dump(mode="json")


def matches(rule: Rule, message: Message) -> bool:
    if rule.platform and message.platform != rule.platform:
        return False
    return not rule.contains or rule.contains.casefold() in message.text.casefold()


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


def handled(inbox: Inbox, rule: str, message: Message) -> bool:
    connection = _connect(inbox)
    try:
        row = connection.execute("SELECT 1 FROM handled WHERE rule = ? AND platform = ? AND id = ?", (rule, message.platform, message.id)).fetchone()
    finally:
        connection.close()
    return row is not None


def mark_handled(inbox: Inbox, rule: str, message: Message) -> None:
    connection = _connect(inbox)
    try:
        with connection:
            connection.execute("INSERT OR IGNORE INTO handled VALUES (?, ?, ?)", (rule, message.platform, message.id))
    finally:
        connection.close()
