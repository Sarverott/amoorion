"""The params of every method in one place; each is defined next to its method."""

from amoorion.methods.automate_method import AutomateParams
from amoorion.methods.base import NoParams
from amoorion.methods.compose_method import ComposeParams
from amoorion.methods.delete_method import DeleteParams
from amoorion.methods.inbox_method import InboxParams
from amoorion.methods.notify_method import NotifyParams
from amoorion.methods.publish_method import PublishParams
from amoorion.methods.read_method import ReadParams
from amoorion.methods.reply_method import ReplyParams
from amoorion.methods.search_method import SearchParams
from amoorion.methods.simulate_method import SimulateParams
from amoorion.methods.snapshot_method import SnapshotParams
from amoorion.methods.wiki_method import WikiParams
from amoorion.methods.workflow_method import WorkflowParams

__all__ = [
    "AutomateParams",
    "ComposeParams",
    "DeleteParams",
    "InboxParams",
    "NoParams",
    "NotifyParams",
    "PublishParams",
    "ReadParams",
    "ReplyParams",
    "SearchParams",
    "SimulateParams",
    "SnapshotParams",
    "WikiParams",
    "WorkflowParams",
]
