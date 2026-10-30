"""Operations over the platforms; the CLI, API, MCP and daemon expose them."""

from amoorion.methods.base import (
    METHODS,
    AccountStatus,
    Accounts,
    Delete,
    InboxMethod,
    Method,
    PluginInfo,
    Plugins,
    Publish,
    Read,
    Reply,
    Snapshot,
    SnapshotMethod,
    plugsFlagsToList,
)

__all__ = [
    "METHODS",
    "AccountStatus",
    "Accounts",
    "Delete",
    "InboxMethod",
    "Method",
    "PluginInfo",
    "Plugins",
    "Publish",
    "Read",
    "Reply",
    "Snapshot",
    "SnapshotMethod",
    "plugsFlagsToList",
]
