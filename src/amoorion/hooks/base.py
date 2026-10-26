"""Hooks: a payload from a service (GitHub, GitLab, Discord…) becomes a Message.

Every hook checks first that the call is genuine (`verify`), then turns the
payload into a message (`receive`). The API serves them at
`POST /hooks/<name>`. A hook without its secret in the vault refuses
everything.
"""

import hmac
from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError, Controller, Registry, View
from amoorion.models import Account, Message
from amoorion.vault import Vault


class Forbidden(AmoorionError):
    """The call didn't prove it comes from the service."""


class Hook(Controller):
    def __init__(self, vault: Vault, view: View | None = None) -> None:
        super().__init__(view)
        self.vault = vault

    def secret(self, key: str) -> str:
        return self.vault.get(f"hooks/{self.name}-{key}")

    def verify(self, body: bytes, headers: Mapping[str, str]) -> None:
        raise NotImplementedError

    def receive(self, payload: Any) -> Message:
        raise NotImplementedError

    def handle(self, body: bytes, headers: Mapping[str, str], payload: Any) -> Message:
        try:
            self.verify(body, headers)
        except Forbidden:
            raise
        except AmoorionError as error:  # e.g. the secret is missing
            raise Forbidden(f"hook {self.name} can't verify calls: {error}") from None
        return self.receive(payload)


HOOKS: Registry[type[Hook]] = Registry("hook")


@HOOKS.register
class GenericHook(Hook):
    """Any service that can send `{"text": …, "author": …}` with a shared token.

    The token is the secret `hooks/generic-token`, sent in `X-Amoorion-Token`.
    """

    name: ClassVar[str] = "generic"
    description: ClassVar[str] = "JSON {text, author} with a shared token header"

    def verify(self, body: bytes, headers: Mapping[str, str]) -> None:
        sent = headers.get("x-amoorion-token", "")
        if not hmac.compare_digest(sent.encode(), self.secret("token").encode()):
            raise Forbidden("wrong or missing X-Amoorion-Token")

    def receive(self, payload: Any) -> Message:
        if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
            raise AmoorionError('generic hook expects JSON {"text": "…"}')
        author = payload.get("author")
        return Message(
            platform=f"hook:{self.name}",
            text=payload["text"],
            author=Account(platform=f"hook:{self.name}", handle=author) if isinstance(author, str) else None,
        )
