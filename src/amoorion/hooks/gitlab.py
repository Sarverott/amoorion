"""gitlab hook: webhooks of a project or group.

The webhook's secret token is `hooks/gitlab-token`; GitLab sends it as it is
(`X-Gitlab-Token`).
"""

import hmac
from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.hooks.base import HOOKS, Forbidden, Hook
from amoorion.models import Account, Message


def describe(payload: dict[str, Any]) -> tuple[str, str | None]:
    """What happened in a line, and its link."""

    kind = payload.get("object_kind") or payload.get("event_name") or "event"

    project = payload.get(
        "project",
        {},
    )

    name = project.get(
        "path_with_namespace",
        "?",
    )

    if kind in ("push", "tag_push"):
        commits = payload.get(
            "commits",
            [],
        )

        last = (
            commits[-1]
            .get(
                "message",
                "",
            )
            .strip()
            if commits
            else ""
        )

        return (
            f"{name}: {len(commits)} commits to {payload.get('ref', '?')}: {last}".strip(),
            project.get("web_url"),
        )

    attributes = payload.get(
        "object_attributes",
        {},
    )

    title = attributes.get("title") or attributes.get("note") or ""

    action = attributes.get("action") or attributes.get("status") or ""

    return f"{name}: {kind.replace('_', ' ')} {action}: {title}".strip(
        " :"
    ), attributes.get("url") or project.get("web_url")


@HOOKS.register
class GitLabHook(Hook):
    """Events of a GitLab project as messages."""

    name: ClassVar[str] = "gitlab"
    description: ClassVar[str] = (
        "GitLab webhooks, with a secret token (X-Gitlab-Token)"
    )
    secrets: ClassVar[dict[str, str]] = {"token": "The webhook's secret token"}

    def verify(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:
        """Compare the secret token, which GitLab sends as it is, in constant time."""

        if not hmac.compare_digest(
            headers.get("x-gitlab-token", "").encode(),
            self.secret("token").encode(),
        ):
            raise Forbidden("wrong or missing X-Gitlab-Token")

    def receive(
        self,
        payload: Any,
    ) -> Message | None:
        """One sentence on the event, by its user."""

        if not isinstance(payload, dict):
            raise AmoorionError("gitlab hook expects a JSON object")

        text, url = describe(payload)

        user = payload.get("user_username") or payload.get("user", {}).get(
            "username"
        )

        return Message(
            platform=f"hook:{self.name}",
            text=text,
            id=self.headers.get("x-gitlab-event-uuid"),
            url=url,
            author=Account(
                platform=f"hook:{self.name}",
                handle=user,
            )
            if user
            else None,
        )
