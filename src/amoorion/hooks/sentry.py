"""sentry hook: webhooks of a Sentry internal integration.

The integration's client secret is `hooks/sentry-secret`; Sentry signs the raw body
with it (`Sentry-Hook-Signature`, HMAC-SHA256 in hex). `Sentry-Hook-Resource` says
what it is about.
"""

import hashlib
import hmac
from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.hooks.base import HOOKS, Forbidden, Hook
from amoorion.models import Message


@HOOKS.register
class SentryHook(Hook):
    name: ClassVar[str] = "sentry"
    description: ClassVar[str] = (
        "Sentry webhooks, signed (Sentry-Hook-Signature)"
    )
    secrets: ClassVar[dict[str, str]] = {
        "secret": "The integration's client secret"
    }

    def verify(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:

        expected = hmac.new(
            self.secret("secret").encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            headers.get("sentry-hook-signature", "").encode(), expected.encode()
        ):
            raise Forbidden("wrong or missing Sentry-Hook-Signature")

    def receive(
        self,
        payload: Any,
    ) -> Message | None:

        resource = self.headers.get(
            "sentry-hook-resource",
            "",
        )

        if not isinstance(payload, dict) or not resource:
            raise AmoorionError(
                "sentry hook expects a JSON object and Sentry-Hook-Resource"
            )

        if resource == "installation":
            return None

        data = payload.get("data") or {}

        item = (
            data.get(resource) or data.get("event") or data.get("issue") or {}
        )

        title = (
            item.get(
                "title",
                "",
            )
            if isinstance(item, dict)
            else ""
        )

        url = (
            (item.get("permalink") or item.get("web_url"))
            if isinstance(item, dict)
            else None
        )

        return Message(
            platform=f"hook:{self.name}",
            text=f"sentry: {resource} {payload.get('action', '')}: {title}".strip().rstrip(
                ":"
            ),
            id=self.headers.get("request-id"),
            url=url,
        )
