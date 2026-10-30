"""NATS: results of methods published, a subject listened to by the daemon.

Off unless `.env` names the server; the address is a link, not a secret:

    AMOORION_NATS=nats://host:4222
    AMOORION_NATS_PREFIX=amoorion   optional, the first part of every subject

The optional secret `nats/token` is the server's token. Subjects:

- `<prefix>.methods.<name>`: what a method that changes something returned, as JSON.
- `<prefix>.in.>`: listened to by the daemon's service; each message is kept in
  the inbox as `nats:<rest of the subject>`, the body being JSON
  `{"text": …, "author": …}` or plain text.

Publishing never makes a method fail: the post went out, whatever NATS says.
"""

import asyncio
import json
import logging
import os
import threading
from typing import Any, ClassVar

import nats

from amoorion.core import AmoorionError, Controller
from amoorion.inbox import Inbox
from amoorion.models import Account, Message
from amoorion.vault import Vault, open_vault

log = logging.getLogger(__name__)
TIMEOUT = 5.0


def enabled() -> str | None:
    return os.environ.get("AMOORION_NATS") or None


def prefix() -> str:
    return os.environ.get("AMOORION_NATS_PREFIX", "amoorion")


def out_subject(method: str) -> str:
    return f"{prefix()}.methods.{method}"


def in_subject() -> str:
    return f"{prefix()}.in.>"


def options(vault: Vault) -> dict[str, Any]:
    try:
        return {"token": vault.get("nats/token")}
    except AmoorionError:
        return {}


async def _publish(server: str, subject: str, body: bytes, extra: dict[str, Any]) -> None:
    client = await nats.connect(server, connect_timeout=TIMEOUT, max_reconnect_attempts=0, **extra)
    try:
        await client.publish(subject, body)
        await client.flush(timeout=TIMEOUT)
    finally:
        await client.close()


def announce(method: str, result: Any, vault: Vault | None = None) -> None:
    """Publish a method's result, if NATS is on; a failure is only logged."""
    server = enabled()
    if not server:
        return
    try:
        models = result if isinstance(result, list) else [result]
        body = json.dumps([model.model_dump(mode="json") for model in models]).encode()
        extra = options(vault or open_vault())
        # Its own thread: a method may be running inside a front-end's event loop.
        failed: list[BaseException] = []

        def send() -> None:
            try:
                asyncio.run(_publish(server, out_subject(method), body, extra))
            except Exception as error:
                failed.append(error)

        thread = threading.Thread(target=send, daemon=True)
        thread.start()
        thread.join(TIMEOUT * 3)
        if failed or thread.is_alive():
            log.warning("NATS: result of %s not published: %s", method, failed[0] if failed else "timeout")
    except Exception as error:
        log.warning("NATS: result of %s not published: %s", method, error)


def to_message(subject: str, data: bytes) -> Message:
    platform = "nats:" + subject.removeprefix(in_subject()[:-1])
    try:
        body = json.loads(data)
    except ValueError:
        body = None
    if isinstance(body, dict) and isinstance(body.get("text"), str):
        author = body.get("author")
        account = Account(platform=platform, handle=author) if isinstance(author, str) else None
        return Message(platform=platform, text=body["text"], author=account)
    return Message(platform=platform, text=data.decode(errors="replace"))


class NatsService(Controller):
    """A daemon service: keeps what arrives on `<prefix>.in.>` in the inbox."""

    name: ClassVar[str] = "nats"
    description: ClassVar[str] = "NATS subscriber filling the inbox"

    def __init__(self, server: str, vault: Vault | None = None, inbox: Inbox | None = None) -> None:
        super().__init__()
        self.server, self.vault, self.inbox = server, vault or open_vault(), inbox or Inbox()
        self._stop = asyncio.Event()

    async def _received(self, message: Any) -> None:
        self.inbox.keep([to_message(message.subject, message.data)])

    async def run(self) -> None:
        client = await nats.connect(self.server, **options(self.vault))
        try:
            await client.subscribe(in_subject(), cb=self._received)
            await self._stop.wait()
        finally:
            await client.drain()

    async def stop(self) -> None:
        self._stop.set()
