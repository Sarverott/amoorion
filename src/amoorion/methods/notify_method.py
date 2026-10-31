"""Notify: tell the platforms of AMOORION_NOTIFY."""

import os
from typing import ClassVar

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.methods.publish_method import Publish, PublishParams
from amoorion.models import Post, Result


class NotifyParams(Post):
    """The same as a post."""

    pass


@METHODS.register
class Notify(Method):
    """A post to wherever the user wants to hear from amoorion, set in AMOORION_NOTIFY."""

    name: ClassVar[str] = "notify"
    description: ClassVar[str] = (
        "Send a notification to the platforms of AMOORION_NOTIFY; one result per platform"
    )
    Params: ClassVar[type[Model]] = NotifyParams

    def run(
        self,
        params: NotifyParams,
    ) -> list[Result]:
        """Publish to those platforms; none set means nothing is sent and no error."""

        targets = [
            name.strip()
            for name in os.environ.get("AMOORION_NOTIFY", "").split(",")
            if name.strip()
        ]

        if not targets:
            return []

        return Publish(self.vault).run(
            PublishParams(
                to=targets,
                **params.model_dump(),
            )
        )
