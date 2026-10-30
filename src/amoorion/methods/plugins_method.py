"""Plugins: what is installed and what each can do."""

from typing import ClassVar

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.plugins import FAILED, Capability, load_plugins


class PluginInfo(Model):
    name: str
    description: str
    capabilities: list[Capability]
    error: str | None = None


@METHODS.register
class Plugins(Method):
    name: ClassVar[str] = "plugins"
    description: ClassVar[str] = "List the platform plugins and what they can do"
    read_only: ClassVar[bool] = True

    def run(self, params: Model) -> list[PluginInfo]:
        plugins = load_plugins()
        return [
            PluginInfo(name=plugin.name, description=plugin.description, capabilities=sorted(plugin.capabilities))
            for plugin in map(plugins.get, plugins.names())
        ] + [
            PluginInfo(name=name, description="failed to load", capabilities=[], error=error)
            for name, error in sorted(FAILED.items())
        ]


def plugsFlagsToList(flags: dict[str, bool]) -> list[str]:  # noqa: N802 - the author's name for it
    """The names of the flags that are on, e.g. of `Plugins["x"].infoflags`."""
    return [name for name, on in flags.items() if on]
