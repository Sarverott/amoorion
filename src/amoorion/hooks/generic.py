"""Any service that can send JSON with a shared token."""

import hmac
from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.hooks.base import HOOKS, Forbidden, Hook
from amoorion.models import Account, Message


@HOOKS.register
class GenericHook(Hook):
    """Any service that can send `{"text": …, "author": …}` with a shared token.

    The token is the secret `hooks/generic-token`, sent in `X-Amoorion-Token`.
    """

    name: ClassVar[str] = "generic"
    secrets: ClassVar[dict[str, str]] = {
        "token": "Shared token, sent in X-Amoorion-Token"
    }
    description: ClassVar[str] = (
        "JSON {text, author} with a shared token header"
    )

    def verify(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:
        """Compare the shared token, in constant time so that timing gives nothing away."""

        sent = headers.get(
            "x-amoorion-token",
            "",
        )

        if not hmac.compare_digest(
            sent.encode(), self.secret("token").encode()
        ):
            raise Forbidden("wrong or missing X-Amoorion-Token")

    def receive(
        self,
        payload: Any,
    ) -> Message:
        """A message of the JSON `{"text": …, "author": …}`."""

        if not isinstance(payload, dict) or not isinstance(
            payload.get("text"), str
        ):
            raise AmoorionError('generic hook expects JSON {"text": "…"}')

        author = payload.get("author")

        return Message(
            platform=f"hook:{self.name}",
            text=payload["text"],
            author=Account(
                platform=f"hook:{self.name}",
                handle=author,
            )
            if isinstance(author, str)
            else None,
        )
