"""Link to the vault that holds platform secrets.

`.env` (or the environment) holds only what establishes the link:

    AMOORION_VAULT=<kind>        which backend (see BACKENDS)
    AMOORION_VAULT_ADDR=<url>    where it is, when the backend needs it
    AMOORION_VAULT_TOKEN=<token> how to log in, when the backend needs it

Secrets are named `<platform>/<key>`, e.g. `bluesky/password`. Which real
vault comes first is open (BRAINSTORM Q6); until then only the `env` backend
exists, meant for development.
"""

import os
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

from amoorion.core import AmoorionError, Controller, Model, Registry


class VaultLink(Model):
    """Settings that establish the link to a vault."""

    kind: str = "env"
    addr: str | None = None
    token: str | None = None

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "VaultLink":
        load_dotenv(env_file or Path.cwd() / ".env", override=False)
        return cls(
            kind=os.environ.get("AMOORION_VAULT", "env"),
            addr=os.environ.get("AMOORION_VAULT_ADDR"),
            token=os.environ.get("AMOORION_VAULT_TOKEN"),
        )


class Vault(Controller):
    """A backend that hands out secrets by name."""

    def __init__(self, link: VaultLink) -> None:
        super().__init__()
        self.link = link

    def get(self, name: str) -> str:
        raise NotImplementedError


BACKENDS: Registry[type[Vault]] = Registry("vault backend")


@BACKENDS.register
class EnvVault(Vault):
    """Development backend: `bluesky/password` is read from AMOORION_SECRET_BLUESKY_PASSWORD."""

    name: ClassVar[str] = "env"
    description: ClassVar[str] = "secrets from environment variables (development only)"

    @staticmethod
    def variable(name: str) -> str:
        return "AMOORION_SECRET_" + name.replace("/", "_").replace("-", "_").upper()

    def get(self, name: str) -> str:
        try:
            return os.environ[self.variable(name)]
        except KeyError:
            raise AmoorionError(f"secret {name!r} not found (set {self.variable(name)})") from None


def open_vault(link: VaultLink | None = None) -> Vault:
    link = link or VaultLink.from_env()
    return BACKENDS.get(link.kind)(link)
