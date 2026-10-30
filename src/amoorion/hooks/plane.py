"""plane hook: webhooks of a Plane workspace.

The webhook's secret is `hooks/plane-secret`; Plane signs the raw body with it
(`X-Plane-Signature`, HMAC-SHA256 in hex). Its examples carry no address of the work
item, so the message has no link.
"""

import hashlib
import hmac
from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.hooks.base import HOOKS, Forbidden, Hook
from amoorion.models import Message


@HOOKS.register
class PlaneHook(Hook):
    name: ClassVar[str] = "plane"
    description: ClassVar[str] = "Plane webhooks, signed (X-Plane-Signature)"
    secrets: ClassVar[dict[str, str]] = {"secret": "The webhook's secret"}

    def verify(self, body: bytes, headers: Mapping[str, str]) -> None:
        expected = hmac.new(self.secret("secret").encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(headers.get("x-plane-signature", "").encode(), expected.encode()):
            raise Forbidden("wrong or missing X-Plane-Signature")

    def receive(self, payload: Any) -> Message:
        if not isinstance(payload, dict):
            raise AmoorionError("plane hook expects a JSON object")
        event = self.headers.get("x-plane-event") or payload.get("event", "?")
        name = (payload.get("data") or {}).get("name", "")
        return Message(
            platform=f"hook:{self.name}",
            text=f"plane: {event}: {name}".strip().rstrip(":"),
            # Stable across a delivery's retries, unlike X-Plane-Delivery.
            id=payload.get("event_id") or self.headers.get("x-plane-delivery"),
        )
