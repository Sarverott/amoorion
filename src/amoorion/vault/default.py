"""env backend: the `.env` setup, secrets as environment variables.

`bluesky/password` is read from AMOORION_SECRET_BLUESKY_PASSWORD. Meant for
development and tests; real secrets belong in one of the other backends.
"""

import os
from typing import ClassVar

from amoorion.core import AmoorionError
from amoorion.vault.base import BACKENDS, Vault


@BACKENDS.register
class EnvVault(Vault):
    name: ClassVar[str] = "env"
    description: ClassVar[str] = (
        "secrets from environment variables (development only)"
    )

    @staticmethod
    def variable(name: str) -> str:

        return (
            "AMOORION_SECRET_"
            + name.replace("/", "_").replace("-", "_").upper()
        )

    def get(
        self,
        name: str,
    ) -> str:

        self.split(name)

        try:
            return os.environ[self.variable(name)]
        except KeyError:
            raise AmoorionError(
                f"secret {name!r} not found (set {self.variable(name)})"
            ) from None
