"""What every platform plugin is: a controller speaking to one platform.

A plugin declares its `capabilities` and implements the matching calls;
the rest raise `Unsupported`. Its secrets come from the vault, named
`<platform>/<key>`. Every plugin, built in or from a separate package, is found
through the Python entry point group `amoorion.plugins` (name = platform,
value = `module:PluginClass`) and loaded into PLUGINS by `load_plugins()`.
A plugin that fails to load is kept in FAILED instead of stopping amoorion.
"""

from enum import StrEnum
from importlib.metadata import entry_points
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


ENTRY_POINTS = "amoorion.plugins"

PLUGINS: Registry[type[Plugin]] = Registry("plugin")
# platform -> why its plugin didn't load
FAILED: dict[str, str] = {}


def load_plugins() -> None:
    for entry_point in entry_points(group=ENTRY_POINTS):
        if entry_point.name in PLUGINS:
            continue
        try:
            plugin = entry_point.load()
            if not (isinstance(plugin, type) and issubclass(plugin, Plugin)):
                raise AmoorionError(f"{entry_point.value} is not a Plugin")
            if plugin.name != entry_point.name:
                raise AmoorionError(f"{entry_point.value} is named {plugin.name!r}, not {entry_point.name!r}")
            PLUGINS.register(plugin)
            FAILED.pop(entry_point.name, None)
        except Exception as error:  # an outside package must not break amoorion
            FAILED[entry_point.name] = f"{type(error).__name__}: {error}"


def open_plugin(name: str, vault: Vault | None = None) -> Plugin:
    return PLUGINS.get(name)(vault or open_vault())
