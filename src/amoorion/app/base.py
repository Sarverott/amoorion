"""`Amoorion`: one setup (vault, dataset, inbox, flags, plugins in use) as a Python object.

    amo = Amoorion("/path/to/env", "/path/to/dataset", flags={"mode": "cli"})
    amo.use(Plugins["x"], Plugins["bluesky"])
    amo.publish(text="hello")          # every method is callable by its name
    amo.save("state.yaml")             # where things are, and hashes to detect changes

An env file gives this object its link to the vault, inbox and dataset, without
touching the environment of the process, so two objects can hold two identities.
AMOORION_NOTIFY and AMOORION_NATS stay settings of the process.
"""

from pathlib import Path
from typing import Any, Self

from dotenv import dotenv_values

from amoorion.app.frontends import FrontEnds
from amoorion.app.states import States
from amoorion.core import AmoorionError
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.methods import METHODS, Method
from amoorion.plugins import load_plugins
from amoorion.vault import Vault, VaultLink, open_vault


class Amoorion(FrontEnds, States):
    def __init__(self, env: str | Path | None = None, dataset: str | Path | None = None, flags: dict[str, Any] | None = None) -> None:
        self.flags: dict[str, Any] = dict(flags or {})
        self.used: list[str] = []
        self._hashes: dict[str, str] = {}
        self._dataset_path = Path(dataset).expanduser() if dataset else None
        self._open(Path(env).expanduser() if env else None)

    def _open(self, env: Path | None) -> None:
        self.env = env
        self._values: dict[str, str | None] = {}
        if env is not None:
            if not env.is_file():
                raise AmoorionError(f"no env file at {env}")
            self._values = dotenv_values(env)
        self._vault: Vault | None = None

    def _path(self, variable: str) -> Path | None:
        value = self._values.get(variable)
        return Path(value).expanduser() if value else None

    @property
    def link(self) -> VaultLink:
        if self.env is None:
            return VaultLink.from_env()
        values = self._values
        return VaultLink(
            kind=values.get("AMOORION_VAULT") or "env",
            addr=values.get("AMOORION_VAULT_ADDR"),
            token=values.get("AMOORION_VAULT_TOKEN"),
            path=values.get("AMOORION_VAULT_PATH"),
        )

    @property
    def vault(self) -> Vault:
        if self._vault is None:
            self._vault = open_vault(self.link)
        return self._vault

    @property
    def store(self) -> Inbox:
        """The inbox itself; `inbox()` is the method that lists it."""
        return Inbox(self._path("AMOORION_INBOX"))

    @property
    def dataset(self) -> Dataset:
        return Dataset(self._dataset_path or self._path("AMOORION_DATASET"))

    def use(self, *plugs: str) -> Self:
        """The platforms this object works on: `publish` goes to them unless told otherwise."""
        for plug in plugs:
            name = str(plug)
            load_plugins().get(name)  # a wrong name fails here, not at the first post
            if name not in self.used:
                self.used.append(name)
        return self

    def method(self, name: str) -> Method:
        return METHODS.get(name)(self.vault, inbox=self.store, dataset=self.dataset)

    def call(self, name: str, **params: Any) -> Any:
        """Run one method with this object's setup; answers in plain JSON-compatible data."""
        fields = METHODS.get(name).Params.model_fields
        if name == "publish" and "to" not in params and self.used:
            params["to"] = list(self.used)
        if "platform" in fields and fields["platform"].is_required() and "platform" not in params and len(self.used) == 1:
            params["platform"] = self.used[0]
        return self.method(name)(**params)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_") or name not in METHODS:
            raise AttributeError(name)

        def call(**params: Any) -> Any:
            return self.call(name, **params)

        call.__doc__ = METHODS.get(name).description
        return call

    def __repr__(self) -> str:
        return f"<Amoorion vault={self.link.kind} plugins={self.used} flags={self.flags}>"
