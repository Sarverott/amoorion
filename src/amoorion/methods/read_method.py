"""Read: the latest messages of one platform."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method, profile_of
from amoorion.models import Message
from amoorion.plugins import open_plugin


class ReadParams(Model):
    """From which platform, and how many."""

    platform: str
    limit: int = Field(
        20,
        ge=1,
        le=200,
    )


@METHODS.register
class Read(Method):
    """Fetches the latest messages, and keeps them in the inbox and the dataset."""

    name: ClassVar[str] = "read"
    description: ClassVar[str] = (
        "Read the latest messages of one platform (and keep them in the inbox and the dataset)"
    )
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = ReadParams

    def run(
        self,
        params: ReadParams,
    ) -> list[Message]:
        """Read, then keep; `keep` also tells which messages are known already."""

        plugin = open_plugin(
            params.platform,
            self.vault,
        )

        messages = self.inbox.keep(plugin.read(params.limit))

        self.dataset.record(
            plugin.name,
            profile_of(plugin),
            messages,
        )

        return messages
