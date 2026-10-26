"""What every platform plugin is: a controller speaking to one platform.

A plugin declares its `capabilities` and implements the matching calls;
the rest raise `Unsupported`. Its secrets come from the vault, named
`<platform>/<key>`. Built-in plugins live in `amoorion/plugins/<platform>/`
and register in PLUGINS; loading outside packages is open (BRAINSTORM Q7).
"""

from enum import StrEnum
from typing import ClassVar

from amoorion.core import AmoorionError, Controller, Registry, View
from amoorion.models import Message, Post
from amoorion.vault import Vault, open_vault


class Capability(StrEnum):
    POST = "post"
    READ = "read"
    REPLY = "reply"


class Unsupported(AmoorionError):
    """The platform can't do what was asked."""


class Plugin(Controller):
    capabilities: ClassVar[frozenset[Capability]] = frozenset()

    def __init__(self, vault: Vault, view: View | None = None) -> None:
        super().__init__(view)
        self.vault = vault

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


PLUGINS: Registry[type[Plugin]] = Registry("plugin")


def open_plugin(name: str, vault: Vault | None = None) -> Plugin:
    return PLUGINS.get(name)(vault or open_vault())
