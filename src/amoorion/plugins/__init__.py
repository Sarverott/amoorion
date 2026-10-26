"""Per-platform plugins: one per publication or communication platform."""

from amoorion.plugins.base import PLUGINS, Capability, Plugin, Unsupported, open_plugin

# Built-in plugins register themselves on import.
from amoorion.plugins import dryrun  # noqa: E402,F401

__all__ = ["PLUGINS", "Capability", "Plugin", "Unsupported", "open_plugin"]
