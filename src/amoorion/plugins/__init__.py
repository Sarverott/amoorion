"""Per-platform plugins: one per publication or communication platform."""

from amoorion.plugins.base import (
    ENTRY_POINTS,
    FAILED,
    PLUGINS,
    Capability,
    Plugin,
    Unsupported,
    load_plugins,
    open_plugin,
)

from amoorion.plugins.http import HttpPlugin  # noqa: E402

load_plugins()

__all__ = ["ENTRY_POINTS", "FAILED", "PLUGINS", "Capability", "HttpPlugin", "Plugin", "Unsupported", "load_plugins", "open_plugin"]
