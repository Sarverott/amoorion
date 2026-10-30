"""What every platform plugin is: a controller speaking to one platform.

A plugin declares its `capabilities` and implements the matching calls;
the rest raise `Unsupported`. `profile()` names who or where it speaks
(the dataset keeps posts by it). Its secrets come from the vault, named
`<platform>/<key>`. How plugins are found: loading.py.
"""

import json
from enum import StrEnum
from importlib.resources import files
from typing import Any, ClassVar

from amoorion.core import AmoorionError, Controller, View
from amoorion.models import Message, Post
from amoorion.vault import Vault


class Capability(StrEnum):
    POST = "post"
    READ = "read"
    REPLY = "reply"
    DELETE = "delete"


class Unsupported(AmoorionError):
    """The platform can't do what was asked."""


class Plugin(Controller):
    capabilities: ClassVar[frozenset[Capability]] = frozenset()
    # Keys this plugin reads from the vault as `<platform>/<key>`.
    secrets: ClassVar[tuple[str, ...]] = ()

    def __init__(self, vault: Vault, view: View | None = None) -> None:
        super().__init__(view)
        self.vault = vault

    @classmethod
    def schema(cls) -> dict[str, Any]:
        """What this plugin's vault entry holds, from `schema.vault.json` of its package.

        Like the scopes of OpenAPI: `scopes` are the keys it needs and `optional`
        the keys it can use, each with what it is.
        """
        file = files(cls.__module__.partition(".")[0]) / "schema.vault.json"
        if file.is_file():
            return json.loads(file.read_text())["vault"][cls.name]
        return {"description": cls.description, "scopes": dict.fromkeys(cls.secrets, ""), "optional": {}}

    def secret(self, key: str) -> str:
        return self.vault.get(f"{self.name}/{key}")

    def _unsupported(self, capability: Capability) -> Unsupported:
        return Unsupported(f"{self.name} can't {capability}")

    def post(self, post: Post) -> Message:
        raise self._unsupported(Capability.POST)

    def read(self, limit: int = 20) -> list[Message]:
        raise self._unsupported(Capability.READ)

    def reply(self, to: Message, text: str) -> Message:
        raise self._unsupported(Capability.REPLY)

    def delete(self, message: Message) -> None:
        """Remove one message of this platform (amoorion's `delete` keeps a copy first)."""
        raise self._unsupported(Capability.DELETE)

    def profile(self) -> str:
        """Who or where this plugin speaks: the account, page, blog, channel or room.

        Names its directory in the dataset; never a secret. Plugins with
        one natural name override it.
        """
        return "default"
