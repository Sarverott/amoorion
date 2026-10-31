"""Accounts: which platforms have their secrets."""

from typing import ClassVar

from amoorion.core import AmoorionError, Model
from amoorion.methods.base import METHODS, Method
from amoorion.plugins import load_plugins


class AccountStatus(Model):
    """Whether a platform is ready: its missing secrets by name, never by value."""

    platform: str
    ready: bool
    missing: list[str] = []
    error: str | None = None


@METHODS.register
class Accounts(Method):
    """Tells which platforms can work right now. Asks the vault, not the platforms."""

    name: ClassVar[str] = "accounts"
    description: ClassVar[str] = (
        "Which platforms have their secrets in the vault (values never shown)"
    )
    read_only: ClassVar[bool] = True

    def run(
        self,
        params: Model,
    ) -> list[AccountStatus]:
        """Try every secret of every plugin; what can't be read counts as missing."""

        statuses = []

        plugins = load_plugins()

        for plugin in map(plugins.get, plugins.names()):
            missing, error = [], None

            for key in plugin.secrets:
                try:
                    self.vault.get(f"{plugin.name}/{key}")
                except AmoorionError as failure:
                    missing.append(key)

                    error = error or str(failure)

            statuses.append(
                AccountStatus(
                    platform=plugin.name,
                    ready=not missing,
                    missing=missing,
                    error=error,
                )
            )

        return statuses
