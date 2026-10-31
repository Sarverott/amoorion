"""Hooks: a payload from a service (GitHub, GitLab, Discord…) becomes a Message.

Every hook checks first that the call is genuine (`verify`), then turns the
payload into a message (`receive`). The API serves them at
`POST /hooks/<name>`. A hook without its secret in the vault refuses
everything. One module per service: generic, github, gitlab, discord, plane, sentry.

`receive` returns None when the call says nothing worth keeping (a ping);
`answer` is what the service's protocol wants back, if it wants anything.
"""

from collections.abc import Mapping
from typing import Any, ClassVar

from amoorion.core import AmoorionError, Controller, Registry, View
from amoorion.models import Message
from amoorion.vault import Vault


class Forbidden(AmoorionError):
    """The call didn't prove it comes from the service."""


class Hook(Controller):
    """One sender of webhooks: how to trust a call, and what the call means.

    A subclass says how to check a call (`verify`) and which message it is (`receive`);
    the API keeps that message in the inbox.
    """

    secrets: ClassVar[
        dict[str, str]
    ] = {}  # read as hooks/<name>-<key>: what each is

    def __init__(
        self,
        vault: Vault,
        view: View | None = None,
    ) -> None:
        """A hook working with the secrets of `vault`."""

        super().__init__(view)

        self.vault = vault

        self.headers: Mapping[str, str] = {}

    def secret(
        self,
        key: str,
    ) -> str:
        """A secret of this hook: `hooks/<name>-<key>` in the vault."""

        return self.vault.get(f"hooks/{self.name}-{key}")

    def verify(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:
        """Raise `Forbidden` unless this call really comes from the sender."""

        raise NotImplementedError

    def receive(
        self,
        payload: Any,
    ) -> Message | None:
        """The message a call carries; `None` when it is only a check by the sender."""

        raise NotImplementedError

    def answer(
        self,
        payload: Any,
    ) -> Any:
        """What to answer the sender, when it expects more than an empty success."""

        return None

    def handle(
        self,
        body: bytes,
        headers: Mapping[str, str],
        payload: Any,
    ) -> Message | None:
        """Verify a call, then read it. Trust comes first: nothing of an unverified call is read.

        A hook unable to verify (say, its secret is missing) refuses as well.
        """

        self.headers = headers

        try:
            self.verify(
                body,
                headers,
            )
        except Forbidden:
            raise
        except AmoorionError as error:  # e.g. the secret is missing
            raise Forbidden(
                f"hook {self.name} can't verify calls: {error}"
            ) from None

        return self.receive(payload)


HOOKS: Registry[type[Hook]] = Registry("hook")


def schema() -> dict[str, Any]:
    """The vault entry `hooks`, as in schema.vault.json of the plugins; each hook's keys are optional."""

    keys = {
        f"{name}-{key}": text
        for name in HOOKS.names()
        for key, text in HOOKS.get(name).secrets.items()
    }

    return {
        "description": "Incoming webhooks; a hook without its secret refuses all",
        "scopes": {},
        "optional": keys,
    }
