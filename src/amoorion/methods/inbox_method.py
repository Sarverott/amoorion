"""Inbox: the messages received so far."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.models import Message


class InboxParams(Model):
    """Which messages of the inbox, and how many."""

    platform: str | None = Field(
        None,
        description="only this platform (a hook is hook:<name>)",
    )
    limit: int = Field(
        20,
        ge=1,
        le=1000,
    )


@METHODS.register
class InboxMethod(Method):
    """Lists what is already kept; asks no platform, so it works offline."""

    name: ClassVar[str] = "inbox"
    description: ClassVar[str] = (
        "Messages received so far, of every platform and hook, newest first"
    )
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = InboxParams

    def run(
        self,
        params: InboxParams,
    ) -> list[Message]:
        """The newest messages kept."""

        return self.inbox.list(
            params.platform,
            params.limit,
        )
