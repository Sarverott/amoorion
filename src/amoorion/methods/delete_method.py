"""Delete: remove one message from its platform, a copy kept first."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import AmoorionError, Model
from amoorion.methods.base import METHODS, Method, profile_of
from amoorion.models import Message, Result
from amoorion.plugins import Capability, Plugin, open_plugin


class DeleteParams(Model):
    """Which message on which platform."""

    platform: str
    id: str = Field(
        description="id of the message to delete, as read or publish gave it"
    )


@METHODS.register
class Delete(Method):
    """Removes a message from its platform, and marks its copy in the dataset as deleted."""

    name: ClassVar[str] = "delete"
    description: ClassVar[str] = (
        "Delete one message on its platform, keeping a copy in the dataset first"
    )
    Params: ClassVar[type[Model]] = DeleteParams

    def _known(
        self,
        plugin: Plugin,
        profile: str,
        id: str,
    ) -> Message:
        """What is known of the message: from the dataset, else from a read, else only its id."""

        found = self.dataset.find(
            plugin.name,
            profile,
            id,
        )

        if found is None and Capability.READ in plugin.capabilities:
            try:
                found = next(
                    (
                        message
                        for message in plugin.read(100)
                        if message.id == id
                    ),
                    None,
                )
            except AmoorionError:
                found = None

        return found or Message(platform=plugin.name, text="", id=id)

    def run(
        self,
        params: DeleteParams,
    ) -> Result:
        """A failure comes back as a `Result` with the reason, not as an exception."""

        plugin = open_plugin(
            params.platform,
            self.vault,
        )

        if Capability.DELETE not in plugin.capabilities:
            return Result(
                platform=plugin.name,
                ok=False,
                error=f"{plugin.name} can't delete",
            )

        profile = profile_of(plugin)

        message = self._known(
            plugin,
            profile,
            params.id,
        )

        self.dataset.keep_deleted(
            plugin.name,
            profile,
            message,
        )

        try:
            plugin.delete(message)
        except AmoorionError as error:
            return Result(
                platform=plugin.name,
                ok=False,
                message=message,
                error=str(error),
            )

        self.dataset.deleted(
            plugin.name,
            profile,
            message,
        )

        return Result(
            platform=plugin.name,
            ok=True,
            message=message,
        )
