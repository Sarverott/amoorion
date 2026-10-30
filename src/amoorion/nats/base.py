"""NATS: results of methods published, a subject listened to by the daemon.

Off unless `.env` names the server; the address is a link, not a secret:

    AMOORION_NATS=nats://host:4222
    AMOORION_NATS_PREFIX=amoorion   optional, the first part of every subject

The optional secret `nats/token` is the server's token. Subjects:

- `<prefix>.methods.<name>`: what a method that changes something returned, as JSON
  (publish.py).
- `<prefix>.in.>`: listened to by the daemon's service; each message is kept in
  the inbox as `nats:<rest of the subject>`, the body being JSON
  `{"text": …, "author": …}` or plain text (service.py).
"""

import os
from typing import Any

from amoorion.core import AmoorionError
from amoorion.vault import Vault


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
