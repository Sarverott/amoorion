"""discord hook: the Interactions Endpoint of a Discord application.

The application's public key is `hooks/discord-public-key` (Developer Portal,
General Information); Discord signs every call with Ed25519. Its PING is
answered and not kept; a command is kept and answered privately.
"""

from collections.abc import Mapping
from typing import Any, ClassVar

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from amoorion.core import AmoorionError
from amoorion.hooks.base import HOOKS, Forbidden, Hook
from amoorion.models import Account, Message

PING, PONG, CHANNEL_MESSAGE, EPHEMERAL = 1, 1, 4, 64


def command_text(data: dict[str, Any]) -> str:

    options = " ".join(
        f"{option.get('name')}={option.get('value')}"
        for option in data.get("options", [])
    )

    return f"/{data.get('name', '?')} {options}".strip()


@HOOKS.register
class DiscordHook(Hook):
    name: ClassVar[str] = "discord"
    description: ClassVar[str] = "Discord interactions, signed (Ed25519)"
    secrets: ClassVar[dict[str, str]] = {
        "public-key": "The application's public key (General Information)"
    }

    def verify(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:

        try:
            key = Ed25519PublicKey.from_public_bytes(
                bytes.fromhex(self.secret("public-key"))
            )

            signature = bytes.fromhex(
                headers.get(
                    "x-signature-ed25519",
                    "",
                )
            )

            key.verify(
                signature,
                headers.get("x-signature-timestamp", "").encode() + body,
            )
        except (ValueError, InvalidSignature):
            raise Forbidden("wrong or missing Discord signature") from None

    def receive(
        self,
        payload: Any,
    ) -> Message | None:

        if not isinstance(payload, dict) or "type" not in payload:
            raise AmoorionError("discord hook expects an interaction")

        if payload["type"] == PING:
            return None

        user = (
            payload.get("member", {}).get("user") or payload.get("user") or {}
        )

        return Message(
            platform=f"hook:{self.name}",
            text=command_text(payload.get("data") or {}),
            id=payload.get("id"),
            author=Account(
                platform=f"hook:{self.name}",
                handle=user["username"],
            )
            if user.get("username")
            else None,
        )

    def answer(
        self,
        payload: Any,
    ) -> dict[str, Any]:

        if payload["type"] == PING:
            return {"type": PONG}

        return {
            "type": CHANNEL_MESSAGE,
            "data": {
                "content": "Received.",
                "flags": EPHEMERAL,
            },
        }
