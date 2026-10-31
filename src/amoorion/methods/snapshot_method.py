"""Snapshot: read a profile's posts into the dataset."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method, profile_of
from amoorion.plugins import open_plugin


class SnapshotParams(Model):
    platform: str
    limit: int = Field(
        100,
        ge=1,
        le=200,
        description="at most this many posts; fewer read means all were read",
    )


class Snapshot(Model):
    platform: str
    profile: str
    path: str
    read: int
    complete: bool
    present: int
    gone: int
    deleted: int


@METHODS.register
class SnapshotMethod(Method):
    name: ClassVar[str] = "snapshot"
    description: ClassVar[str] = (
        "Read the posts of one platform's profile into the dataset (JSON files with an index)"
    )
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = SnapshotParams

    def run(
        self,
        params: SnapshotParams,
    ) -> Snapshot:

        plugin = open_plugin(
            params.platform,
            self.vault,
        )

        profile = profile_of(plugin)

        messages = plugin.read(params.limit)

        # Fewer than asked for: the platform gave all it has, so what wasn't seen is gone.
        complete = len(messages) < params.limit

        self.dataset.record(
            plugin.name,
            profile,
            self.inbox.keep(messages),
            complete=complete,
        )

        states = [
            entry.state
            for entry in self.dataset.index(plugin.name, profile).values()
        ]

        return Snapshot(
            platform=plugin.name,
            profile=profile,
            path=str(
                self.dataset.profile_dir(
                    plugin.name,
                    profile,
                )
            ),
            read=len(messages),
            complete=complete,
            present=states.count("present"),
            gone=states.count("gone"),
            deleted=states.count("deleted"),
        )
