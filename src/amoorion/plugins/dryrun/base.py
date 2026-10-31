"""dryrun plugin: keeps what was posted in memory, sends nothing anywhere."""

from datetime import UTC, datetime
from itertools import count
from typing import ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Message, Post
from amoorion.plugins.base import Capability, Plugin


class DryRun(Plugin):
    """A platform that sends nothing, to try anything without an account.

    It can do everything, and keeps its messages for as long as the process runs.
    """

    name: ClassVar[str] = "dryrun"
    description: ClassVar[str] = (
        "sends nothing; remembers posts for the running process"
    )
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)

    _messages: ClassVar[list[Message]] = []
    _ids = count(1)

    def _say(
        self,
        text: str,
        reply_to: str | None = None,
    ) -> Message:
        """Keep a new message, with the next id."""

        message = Message(
            platform=self.name,
            text=text,
            id=str(next(self._ids)),
            reply_to=reply_to,
            created_at=datetime.now(UTC),
        )

        self._messages.append(message)

        return message

    def post(
        self,
        post: Post,
    ) -> Message:
        """Keep the post; its title and text become one text, as most platforms do."""

        text = "\n\n".join(part for part in (post.title, post.text) if part)

        return self._say(text)

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:
        """The kept messages, newest first."""

        # They are kept oldest first.
        return self._messages[-limit:][::-1]

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:
        """Keep the answer, pointing at the message it answers."""

        return self._say(
            text,
            reply_to=to.id,
        )

    def delete(
        self,
        message: Message,
    ) -> None:
        """Forget a message; an unknown one is an error, as on a real platform."""

        kept = [m for m in self._messages if m.id != message.id]

        if len(kept) == len(self._messages):
            raise AmoorionError(f"dryrun has no message {message.id}")

        self._messages[:] = kept
