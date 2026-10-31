"""github hook: webhooks of a repository or organization.

The webhook's secret is `hooks/github-secret`; GitHub signs the body with it
(`X-Hub-Signature-256`). Set the webhook's content type to JSON.
"""

import hashlib
import hmac
from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.hooks.base import HOOKS, Forbidden, Hook
from amoorion.models import Account, Message


def describe(
    event: str,
    payload: dict[str, Any],
) -> tuple[str, str | None]:
    """What happened in a line, and its link."""

    repository = payload.get(
        "repository",
        {},
    ).get(
        "full_name",
        "?",
    )

    action = payload.get(
        "action",
        "",
    )

    if event == "push":
        commits = payload.get(
            "commits",
            [],
        )

        head = payload.get("head_commit") or {}

        text = f"{repository}: {len(commits)} commits to {payload.get('ref', '?')}: {head.get('message', '')}"

        return text.strip(), payload.get("compare")

    for key in ("pull_request", "issue", "release", "discussion"):
        if item := payload.get(key):
            title = (
                item.get("title")
                or item.get("name")
                or item.get("tag_name")
                or ""
            )

            return (
                f"{repository}: {key.replace('_', ' ')} {action}: {title}".strip(),
                item.get("html_url"),
            )

    return f"{repository}: {event} {action}".strip(), payload.get(
        "repository", {}
    ).get("html_url")


@HOOKS.register
class GitHubHook(Hook):
    name: ClassVar[str] = "github"
    description: ClassVar[str] = "GitHub webhooks, signed (X-Hub-Signature-256)"
    secrets: ClassVar[dict[str, str]] = {"secret": "The webhook's secret"}

    def verify(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:

        expected = (
            "sha256="
            + hmac.new(
                self.secret("secret").encode(), body, hashlib.sha256
            ).hexdigest()
        )

        if not hmac.compare_digest(
            headers.get("x-hub-signature-256", "").encode(), expected.encode()
        ):
            raise Forbidden("wrong or missing X-Hub-Signature-256")

    def receive(
        self,
        payload: Any,
    ) -> Message | None:

        event = self.headers.get(
            "x-github-event",
            "",
        )

        if event == "ping":
            return None

        if not isinstance(payload, dict) or not event:
            raise AmoorionError(
                "github hook expects a JSON object and X-GitHub-Event"
            )

        text, url = describe(
            event,
            payload,
        )

        sender = payload.get(
            "sender",
            {},
        ).get("login")

        return Message(
            platform=f"hook:{self.name}",
            text=text,
            id=self.headers.get("x-github-delivery"),
            url=url,
            author=Account(
                platform=f"hook:{self.name}",
                handle=sender,
            )
            if sender
            else None,
        )
