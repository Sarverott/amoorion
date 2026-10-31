"""`Plugins`: the installed platforms, at rest: nothing is logged in to and no vault is kept.

A `Plug` is a platform's name (a `str`, so `list(Plugins)` is the names) that also
knows the platform's description, version and flags.
"""

import weakref
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError, version
from typing import NamedTuple, Self

from amoorion.core import AmoorionError
from amoorion.plugins import Capability, Plugin, load_plugins
from amoorion.vault import Vault, open_vault


class PlugInfo(NamedTuple):
    """What `dict(Plugins)` gives per platform."""

    description: str
    version: str
    flags: dict[str, bool]


class Plug(str):
    """One installed platform, at rest: its name, and a weak link to its class."""

    def __new__(
        cls,
        plugin: type[Plugin],
    ) -> Self:
        """The plug is the plugin's name as a string, holding the plugin class weakly."""

        plug = super().__new__(
            cls,
            plugin.name,
        )

        plug._plugin = weakref.ref(plugin)

        return plug

    @property
    def plugin(self) -> type[Plugin]:
        """The plugin class; an error if it has been unloaded since."""

        plugin = self._plugin()

        if plugin is None:
            raise AmoorionError(f"plugin {str(self)!r} is gone")

        return plugin

    @property
    def name(self) -> str:
        """The platform's name, what the string itself is."""

        return str(self)

    @property
    def description(self) -> str:
        """One line on what the platform is."""

        return self.plugin.description

    @property
    def version(self) -> str:
        """The version of the package that brought the plugin; `unknown` when not installed as one."""

        try:
            return version(
                self.plugin.__module__.partition(".")[0].replace(
                    "_",
                    "-",
                )
            )
        except PackageNotFoundError:
            return "unknown"

    def has_secrets(
        self,
        vault: Vault | None = None,
    ) -> bool:
        """All its secrets are in the vault; values are never shown. No vault to ask: False."""

        try:
            vault = vault or open_vault()

            for key in self.plugin.secrets:
                vault.get(f"{self.name}/{key}")
        except AmoorionError:
            return False

        return True

    @property
    def infoflags(self) -> dict[str, bool]:
        """What it has, as flags: `creds` (its secrets are set) and `can_<capability>`."""

        can = {
            f"can_{capability}": capability in self.plugin.capabilities
            for capability in Capability
        }

        return {"creds": self.has_secrets()} | can

    @property
    def info(self) -> PlugInfo:
        """Description, version and flags together."""

        return PlugInfo(
            self.description,
            self.version,
            self.infoflags,
        )

    def __repr__(self) -> str:
        """The name, version and capabilities, for a notebook or a shell."""

        return f"<Plug {self.name} {self.version}: {', '.join(sorted(self.plugin.capabilities))}>"


class _InfoKey(str):
    """A key of `dict(Plugins)`: asked by it, the collection answers with the PlugInfo."""


class Plugs:
    """The installed platforms: `Plugins["x"]`, `list(Plugins)`, `dict(Plugins)`, `for p in Plugins`."""

    def __init__(self) -> None:
        """No plug is kept alive by this: they live only as long as somebody uses them."""

        self._resting: weakref.WeakValueDictionary[str, Plug] = (
            weakref.WeakValueDictionary()
        )

    def _plug(
        self,
        name: str,
    ) -> Plug:
        """The plug of a name: the same object while in use, a new one if the plugin was reloaded."""

        plugin = load_plugins().get(name)

        plug = self._resting.get(name)

        if plug is None or plug.plugin is not plugin:
            plug = self._resting[name] = Plug(plugin)

        return plug

    def __getitem__(
        self,
        name: str,
    ) -> Plug | PlugInfo:
        """`Plugins["x"]` is the plug; the keys of `dict(Plugins)` get its information instead."""

        return (
            self._plug(name).info
            if isinstance(name, _InfoKey)
            else self._plug(name)
        )

    def __iter__(self) -> Iterator[Plug]:
        """A plug for every installed platform."""

        return iter([self._plug(name) for name in load_plugins().names()])

    def __len__(self) -> int:
        """How many platforms are installed."""

        return len(load_plugins().names())

    def __contains__(
        self,
        name: object,
    ) -> bool:
        """Whether a platform of that name is installed."""

        return name in load_plugins()

    def keys(self) -> list[str]:
        """Makes `dict(Plugins)` work: name -> PlugInfo, while `Plugins[name]` stays the Plug."""

        return [_InfoKey(name) for name in load_plugins().names()]

    def __repr__(self) -> str:
        """The names of the installed platforms."""

        return f"<Plugins {', '.join(load_plugins().names())}>"


Plugins = Plugs()
