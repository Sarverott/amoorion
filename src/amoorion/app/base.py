"""`Amoorion`: one setup (vault, dataset, inbox, flags, plugins in use) as a Python object.

    amo = Amoorion("/path/to/env", "/path/to/dataset", flags={"mode": "cli"})
    amo.use(Plugins["x"], Plugins["bluesky"])
    amo.publish(text="hello")          # every method is callable by its name
    amo.save("state.yaml")             # where things are, and hashes to detect changes

`Amoorion()` without an env file is a sandbox of its own: secrets only from
AMOORION_SECRET_* variables, an inbox and a dataset in a temporary directory, nothing
of `.env` or of the real setup. An env file gives the object its real link to the
vault, inbox and dataset. Neither touches the environment of the process, so two
objects can hold two identities. AMOORION_NOTIFY and AMOORION_NATS stay settings of
the process.
"""

import atexit
import os
import shutil
import tempfile
import weakref
from pathlib import Path
from typing import Any, Self

from dotenv import dotenv_values

from amoorion.app.frontends import FrontEnds
from amoorion.app.states import States
from amoorion.app.workflows import Workflows
from amoorion.core import AmoorionError
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.methods import METHODS, Method
from amoorion.plugins import load_plugins
from amoorion.vault import Vault, VaultLink, open_vault


def scratch_values(scratch: Path) -> dict[str, str]:
    """A sandbox's setup: no real secrets, an inbox and a dataset in the temporary directory `scratch`."""

    return {
        "AMOORION_VAULT": "env",
        "AMOORION_INBOX": str(scratch / "inbox.sqlite3"),
        "AMOORION_DATASET": str(scratch / "dataset"),
    }


class Amoorion(FrontEnds, States, Workflows):
    """The heart of the project: one setup of amoorion as one object.

    It holds where the secrets, the inbox and the dataset are, the flags, and the
    platforms in use. Every method is callable by its name (`amo.publish(text="hi")`),
    and the CLI, API and MCP server can be started from it, with this same setup.
    """

    def __init__(
        self,
        env: str | Path | None = None,
        dataset: str | Path | None = None,
        flags: dict[str, Any] | None = None,
    ) -> None:
        """Open a setup: `env` is its env file, none means a sandbox of its own.

        `dataset` overrides where the env file keeps the dataset; `flags` are free values
        of the caller, saved along with the state.
        """

        self.flags: dict[str, Any] = dict(flags or {})

        self.used: list[str] = []

        self._hashes: dict[str, str] = {}

        self._workflows: dict[str, Any] = {}

        self._dataset_path = Path(dataset).expanduser() if dataset else None

        self._open(Path(env).expanduser() if env else None)

    @staticmethod
    def init() -> Path:
        """Put the whole process in a sandbox, for what doesn't go through an object: the CLI, `Inbox()`, `Plugins`.

        Returns its temporary directory, removed when the process ends. Examples start with it.
        """

        scratch = Path(tempfile.mkdtemp(prefix="amoorion-"))

        atexit.register(
            shutil.rmtree,
            scratch,
            ignore_errors=True,
        )

        os.environ |= scratch_values(scratch)

        return scratch

    def _scratch(self) -> dict[str, str]:
        """This object's own sandbox, gone with it."""

        scratch = Path(tempfile.mkdtemp(prefix="amoorion-"))

        weakref.finalize(
            self,
            shutil.rmtree,
            scratch,
            ignore_errors=True,
        )

        return scratch_values(scratch)

    def _open(
        self,
        env: Path | None,
    ) -> None:
        """Read the env file (or make the sandbox); the vault itself opens when first needed."""

        self.env = env

        if env is not None and not env.is_file():
            raise AmoorionError(f"no env file at {env}")

        self._values: dict[str, str | None] = (
            dotenv_values(env) if env else self._scratch()
        )

        self._vault: Vault | None = None

    def _path(
        self,
        variable: str,
    ) -> Path | None:
        """A path from this setup's values, with `~` expanded; `None` when it isn't set."""

        value = self._values.get(variable)

        return Path(value).expanduser() if value else None

    @property
    def link(self) -> VaultLink:
        """Where this setup's secrets are: the vault's kind, address, token and path."""

        values = self._values

        return VaultLink(
            kind=values.get("AMOORION_VAULT") or "env",
            addr=values.get("AMOORION_VAULT_ADDR"),
            token=values.get("AMOORION_VAULT_TOKEN"),
            path=values.get("AMOORION_VAULT_PATH"),
        )

    @property
    def vault(self) -> Vault:
        """The vault, opened once on first use: opening may ask a service or read a file."""

        if self._vault is None:
            self._vault = open_vault(self.link)

        return self._vault

    @property
    def store(self) -> Inbox:
        """The inbox itself; `inbox()` is the method that lists it."""

        return Inbox(self._path("AMOORION_INBOX"))

    @property
    def dataset(self) -> Dataset:
        """The dataset; the path given to the constructor wins over the env file's."""

        return Dataset(self._dataset_path or self._path("AMOORION_DATASET"))

    def use(
        self,
        *plugs: str,
    ) -> Self:
        """The platforms this object works on: `publish` goes to them unless told otherwise."""

        for plug in plugs:
            name = str(plug)

            load_plugins().get(
                name
            )  # a wrong name fails here, not at the first post

            if name not in self.used:
                self.used.append(name)

        return self

    def method(
        self,
        name: str,
    ) -> Method:
        """One method, bound to this setup's vault, inbox and dataset."""

        return METHODS.get(name)(
            self.vault,
            inbox=self.store,
            dataset=self.dataset,
        )

    def call(
        self,
        name: str,
        **params: Any,
    ) -> Any:
        """Run one method with this object's setup; answers in plain JSON-compatible data."""

        fields = METHODS.get(name).Params.model_fields

        # What `use` chose fills in what the call left out: where to publish…
        if name == "publish" and "to" not in params and self.used:
            params["to"] = list(self.used)

        # …and the platform to work on, if there is only one to choose from.
        if (
            "platform" in fields
            and fields["platform"].is_required()
            and "platform" not in params
            and len(self.used) == 1
        ):
            params["platform"] = self.used[0]

        return self.method(name)(**params)

    def __getattr__(
        self,
        name: str,
    ) -> Any:
        """`amo.publish(...)`: any method by its name. Only called for names not found otherwise."""

        if name.startswith("_") or name not in METHODS:
            raise AttributeError(name)

        def call(**params: Any) -> Any:

            return self.call(
                name,
                **params,
            )

        call.__doc__ = METHODS.get(name).description

        return call

    def __repr__(self) -> str:
        """What it is at a glance; no secrets, the vault only by its kind."""

        return f"<Amoorion vault={self.link.kind} plugins={self.used} flags={self.flags}>"
