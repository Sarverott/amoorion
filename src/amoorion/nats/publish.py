"""What a method that changes something returned goes out; a failure is only logged.

Publishing never makes a method fail: the post went out, whatever NATS says.
"""

import asyncio
import json
import logging
import threading
from typing import Any

import nats

from amoorion.nats.base import enabled, options, out_subject
from amoorion.vault import Vault, open_vault

log = logging.getLogger(__name__)
TIMEOUT = 5.0


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
