"""The daemon's service: what arrives on `<prefix>.in.>` is kept in the inbox."""

import asyncio
import json
from typing import Any, ClassVar

import nats

from amoorion.core import Controller
from amoorion.inbox import Inbox
from amoorion.models import Account, Message
from amoorion.nats.base import in_subject, options
from amoorion.vault import Vault, open_vault


def to_message(
    subject: str,
    data: bytes,
) -> Message:

    platform = "nats:" + subject.removeprefix(in_subject()[:-1])

    try:
        body = json.loads(data)
    except ValueError:
        body = None

    if isinstance(body, dict) and isinstance(body.get("text"), str):
        author = body.get("author")

        account = (
            Account(
                platform=platform,
                handle=author,
            )
            if isinstance(author, str)
            else None
        )

        return Message(
            platform=platform,
            text=body["text"],
            author=account,
        )

    return Message(
        platform=platform,
        text=data.decode(errors="replace"),
    )


class NatsService(Controller):
    """A daemon service: keeps what arrives on `<prefix>.in.>` in the inbox."""

    name: ClassVar[str] = "nats"
    description: ClassVar[str] = "NATS subscriber filling the inbox"

    def __init__(
        self,
        server: str,
        vault: Vault | None = None,
        inbox: Inbox | None = None,
    ) -> None:

        super().__init__()

        self.server, self.vault, self.inbox = (
            server,
            vault or open_vault(),
            inbox or Inbox(),
        )

        self._stop = asyncio.Event()

    async def _received(
        self,
        message: Any,
    ) -> None:

        self.inbox.keep(
            [
                to_message(
                    message.subject,
                    message.data,
                )
            ]
        )

    async def run(self) -> None:

        client = await nats.connect(
            self.server,
            **options(self.vault),
        )

        try:
            await client.subscribe(
                in_subject(),
                cb=self._received,
            )

            await self._stop.wait()
        finally:
            await client.drain()

    async def stop(self) -> None:

        self._stop.set()
