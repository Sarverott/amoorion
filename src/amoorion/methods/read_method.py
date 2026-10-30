"""Read: the latest messages of one platform."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method, profile_of
from amoorion.models import Message
from amoorion.plugins import open_plugin


class ReadParams(Model):
    platform: str
    limit: int = Field(20, ge=1, le=200)


@METHODS.register
class Read(Method):
    name: ClassVar[str] = "read"
    description: ClassVar[str] = "Read the latest messages of one platform (and keep them in the inbox and the dataset)"
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = ReadParams

    def run(self, params: ReadParams) -> list[Message]:
        plugin = open_plugin(params.platform, self.vault)
        messages = self.inbox.keep(plugin.read(params.limit))
        self.dataset.record(plugin.name, profile_of(plugin), messages)
        return messages
