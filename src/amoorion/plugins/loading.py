"""Finding the plugins: built in or from a separate package, through the Python entry point group.

`amoorion.plugins` (name = platform, value = `module:PluginClass`) is loaded into
PLUGINS by `load_plugins()`, on first use rather than on import: a plugin package
imports `amoorion.plugins` itself, so loading at import time would load it while it
is still half-imported. A plugin that fails to load is kept in FAILED instead of
stopping amoorion.
"""

from importlib.metadata import entry_points

from amoorion.core import AmoorionError, Registry
from amoorion.plugins.base import Plugin
from amoorion.vault import Vault, open_vault

ENTRY_POINTS = "amoorion.plugins"

PLUGINS: Registry[type[Plugin]] = Registry("plugin")
# platform -> why its plugin didn't load
FAILED: dict[str, str] = {}


def load_plugins() -> Registry[type[Plugin]]:
    """Load the plugins not loaded yet (failed ones are tried again) and return PLUGINS."""

    for entry_point in entry_points(group=ENTRY_POINTS):
        if entry_point.name in PLUGINS:
            continue

        try:
            plugin = entry_point.load()

            if not (isinstance(plugin, type) and issubclass(plugin, Plugin)):
                raise AmoorionError(f"{entry_point.value} is not a Plugin")

            if plugin.name != entry_point.name:
                raise AmoorionError(
                    f"{entry_point.value} is named {plugin.name!r}, not {entry_point.name!r}"
                )

            PLUGINS.register(plugin)

            FAILED.pop(
                entry_point.name,
                None,
            )
        except Exception as error:  # an outside package must not break amoorion
            FAILED[entry_point.name] = f"{type(error).__name__}: {error}"

    return PLUGINS


def open_plugin(
    name: str,
    vault: Vault | None = None,
) -> Plugin:

    return load_plugins().get(name)(vault or open_vault())
