"""Reply: answer one message on its platform."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.models import Message
from amoorion.plugins import open_plugin


class ReplyParams(Model):
    platform: str
    to: str = Field(
        description="id of the message to answer, as read or publish gave it"
    )
    text: str = Field(min_length=1)


@METHODS.register
class Reply(Method):
    name: ClassVar[str] = "reply"
    description: ClassVar[str] = "Answer one message on its platform"
    Params: ClassVar[type[Model]] = ReplyParams

    def run(
        self,
        params: ReplyParams,
    ) -> Message:

        to = Message(
            platform=params.platform,
            text="",
            id=params.to,
        )

        return open_plugin(
            params.platform,
            self.vault,
        ).reply(
            to,
            params.text,
        )
