"""Link to the vault that holds platform secrets.

`.env` (or the environment) holds only what establishes the link:

    AMOORION_VAULT=<kind>        which backend: env, bitwarden, http, keepassxc
    AMOORION_VAULT_ADDR=<url>    where the server is, when there is one
    AMOORION_VAULT_TOKEN=<token> what unlocks it (session, token, master password)
    AMOORION_VAULT_PATH=<path>   where amoorion's entries are inside it

Secrets are named `<platform>/<key>`, e.g. `bluesky/password`. Every backend
keeps one entry per platform, `<prefix>/<platform>` (prefix `amoorion`
unless the backend's path says otherwise), with one field per key.
Each backend lives in its own module and registers in BACKENDS.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from amoorion.core import AmoorionError, Controller, Model, Registry

PREFIX = "amoorion"


class VaultLink(Model):
    """Settings that establish the link to a vault."""

    kind: str = "env"
    addr: str | None = None
    token: str | None = None
    path: str | None = None

    @classmethod
    def from_env(
        cls,
        env_file: Path | None = None,
    ) -> "VaultLink":

        load_dotenv(
            env_file or Path.cwd() / ".env",
            override=False,
        )

        return cls(
            kind=os.environ.get(
                "AMOORION_VAULT",
                "env",
            ),
            addr=os.environ.get("AMOORION_VAULT_ADDR"),
            token=os.environ.get("AMOORION_VAULT_TOKEN"),
            path=os.environ.get("AMOORION_VAULT_PATH"),
        )


class Vault(Controller):
    """A backend that hands out secrets by name."""

    def __init__(
        self,
        link: VaultLink,
    ) -> None:

        super().__init__()

        self.link = link

    @staticmethod
    def split(name: str) -> tuple[str, str]:
        """`bluesky/password` -> (`bluesky`, `password`)."""

        platform, _, key = name.partition("/")

        if not platform or not key:
            raise AmoorionError(f"secret name {name!r} is not <platform>/<key>")

        return platform, key

    def get(
        self,
        name: str,
    ) -> str:

        raise NotImplementedError


BACKENDS: Registry[type[Vault]] = Registry("vault backend")


def open_vault(link: VaultLink | None = None) -> Vault:

    link = link or VaultLink.from_env()

    return BACKENDS.get(link.kind)(link)
