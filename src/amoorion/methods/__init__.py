"""Operations over the platforms; the CLI, API, MCP and daemon expose them."""

from amoorion.methods.accounts_method import Accounts, AccountStatus
from amoorion.methods.automate_method import Automate
from amoorion.methods.base import METHODS, Method
from amoorion.methods.compose_method import Compose
from amoorion.methods.delete_method import Delete
from amoorion.methods.inbox_method import InboxMethod
from amoorion.methods.notify_method import Notify
from amoorion.methods.plugins_method import (
    PluginInfo,
    Plugins,
    plugsFlagsToList,
)
from amoorion.methods.publish_method import Publish
from amoorion.methods.read_method import Read
from amoorion.methods.reply_method import Reply
from amoorion.methods.search_method import Search
from amoorion.methods.simulate_method import Simulate
from amoorion.methods.snapshot_method import Snapshot, SnapshotMethod
from amoorion.methods.wiki_method import Wiki
from amoorion.methods.workflow_method import Workflow

__all__ = [
    "METHODS",
    "AccountStatus",
    "Accounts",
    "Automate",
    "Compose",
    "Delete",
    "InboxMethod",
    "Method",
    "Notify",
    "PluginInfo",
    "Plugins",
    "Publish",
    "Read",
    "Reply",
    "Search",
    "Simulate",
    "Snapshot",
    "SnapshotMethod",
    "Wiki",
    "Workflow",
    "plugsFlagsToList",
]
