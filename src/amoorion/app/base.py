"""`Amoorion`: one setup (vault, dataset, inbox, flags, plugins in use) as a Python object.

    amo = Amoorion("/path/to/env", "/path/to/dataset", flags={"mode": "cli"})
    amo.use(Plugins["x"], Plugins["bluesky"])
    amo.publish(text="hello")          # every method is callable by its name
    amo.save("state.yaml")             # where things are, and hashes to detect changes

`Plugins` is the collection of installed platforms at rest: nothing is logged in
to and no vault is kept. A `Plug` is a platform's name (a `str`, so `list(Plugins)`
is the names) that also knows the platform's description, version and flags.

An env file gives this object its link to the vault, inbox and dataset, without
touching the environment of the process, so two objects can hold two identities.
AMOORION_NOTIFY and AMOORION_NATS stay settings of the process.
"""

import hashlib
import weakref
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, NamedTuple, Self

import yaml
from dotenv import dotenv_values

from amoorion.core import AmoorionError, JsonView
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.methods import METHODS, Method
from amoorion.plugins import Capability, Plugin, load_plugins
from amoorion.vault import Vault, VaultLink, open_vault


class PlugInfo(NamedTuple):
    """What `dict(Plugins)` gives per platform."""

    description: str
    version: str
    flags: dict[str, bool]


class Plug(str):
    """One installed platform, at rest: its name, and a weak link to its class."""

    def __new__(cls, plugin: type[Plugin]) -> Self:
        plug = super().__new__(cls, plugin.name)
        plug._plugin = weakref.ref(plugin)
        return plug

    @property
    def plugin(self) -> type[Plugin]:
        plugin = self._plugin()
        if plugin is None:
            raise AmoorionError(f"plugin {str(self)!r} is gone")
        return plugin

    @property
    def name(self) -> str:
        return str(self)

    @property
    def description(self) -> str:
        return self.plugin.description

    @property
    def version(self) -> str:
        try:
            return version(self.plugin.__module__.partition(".")[0].replace("_", "-"))
        except PackageNotFoundError:
            return "unknown"

    def has_secrets(self, vault: Vault | None = None) -> bool:
        """All its secrets are in the vault; values are never shown. No vault to ask: False."""
        try:
            vault = vault or open_vault()
            for key in self.plugin.secrets:
                vault.get(f"{self.name}/{key}")
        except AmoorionError:
            return False
        return True

    @property
    def infoflags(self) -> dict[str, bool]:
        can = {f"can_{capability}": capability in self.plugin.capabilities for capability in Capability}
        return {"creds": self.has_secrets()} | can

    @property
    def info(self) -> PlugInfo:
        return PlugInfo(self.description, self.version, self.infoflags)

    def __repr__(self) -> str:
        return f"<Plug {self.name} {self.version}: {', '.join(sorted(self.plugin.capabilities))}>"


class _InfoKey(str):
    """A key of `dict(Plugins)`: asked by it, the collection answers with the PlugInfo."""


class Plugs:
    """The installed platforms: `Plugins["x"]`, `list(Plugins)`, `dict(Plugins)`, `for p in Plugins`."""

    def __init__(self) -> None:
        self._resting: weakref.WeakValueDictionary[str, Plug] = weakref.WeakValueDictionary()

    def _plug(self, name: str) -> Plug:
        plugin = load_plugins().get(name)
        plug = self._resting.get(name)
        if plug is None or plug.plugin is not plugin:
            plug = self._resting[name] = Plug(plugin)
        return plug

    def __getitem__(self, name: str) -> Plug | PlugInfo:
        return self._plug(name).info if isinstance(name, _InfoKey) else self._plug(name)

    def __iter__(self) -> Iterator[Plug]:
        return iter([self._plug(name) for name in load_plugins().names()])

    def __len__(self) -> int:
        return len(load_plugins().names())

    def __contains__(self, name: object) -> bool:
        return name in load_plugins()

    def keys(self) -> list[str]:
        """Makes `dict(Plugins)` work: name -> PlugInfo, while `Plugins[name]` stays the Plug."""
        return [_InfoKey(name) for name in load_plugins().names()]

    def __repr__(self) -> str:
        return f"<Plugins {', '.join(load_plugins().names())}>"


Plugins = Plugs()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Amoorion:
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

    # Front-ends, on this object's setup
    def api(self) -> Any:
        from amoorion.api import create_app

        return create_app(self.vault, self.store, self.dataset)

    def mcp(self) -> Any:
        from amoorion.mcp import create_server

        return create_server(self.vault, self.store, self.dataset)

    def cli(self, *argv: str) -> int:
        from amoorion.cli import main

        return main(list(argv), self.vault, self.store, self.dataset)

    def run(self, *argv: str, host: str = "127.0.0.1", port: int = 8000) -> int:
        """Run the front-end of `flags["mode"]`: cli (default), api or mcp."""
        mode = self.flags.get("mode", "cli")
        if mode == "cli":
            return self.cli(*argv)
        if mode == "api":
            import uvicorn

            uvicorn.run(self.api(), host=host, port=port)
        elif mode == "mcp":
            self.mcp().run("stdio")
        else:
            raise AmoorionError(f"no mode named {mode!r}: cli, api or mcp")
        return 0

    # States
    def hashes(self) -> dict[str, str]:
        """What now is, as hashes. Of the link only its public parts: a hash of a password can be guessed at."""
        link = self.link
        indexes = sorted(self.dataset.path.glob("*/*/index.json")) if self.dataset.path.is_dir() else []
        inbox = self.store.path
        return {
            "vault": _sha(f"{link.kind}|{link.addr}|{link.path}".encode()),
            "dataset": _sha(b"".join(str(file.relative_to(self.dataset.path)).encode() + file.read_bytes() for file in indexes)),
            "inbox": _sha(inbox.read_bytes() if inbox.is_file() else b""),
        }

    def changes(self) -> list[str]:
        """What differs from the last `load` or `save`."""
        now = self.hashes()
        return [name for name, value in now.items() if self._hashes.get(name) != value]

    def save(self, path: str | Path) -> Self:
        """Write where things are and their hashes as YAML. No secret goes there."""
        self._hashes = self.hashes()
        state = {
            "env": str(self.env) if self.env else None,
            "dataset": str(self._dataset_path) if self._dataset_path else None,
            "flags": self.flags,
            "plugins": self.used,
            "hashes": self._hashes,
        }
        Path(path).expanduser().write_text(yaml.safe_dump(state, sort_keys=False))
        return self

    def load(self, path: str | Path) -> Self:
        """Take over what `save` wrote; `changes()` then tells what moved since."""
        state = yaml.safe_load(Path(path).expanduser().read_text()) or {}
        self._dataset_path = Path(state["dataset"]) if state.get("dataset") else None
        self._open(Path(state["env"]) if state.get("env") else None)
        self.flags = dict(state.get("flags") or {})
        self.used = []
        self.use(*(state.get("plugins") or []))
        self._hashes = dict(state.get("hashes") or {})
        return self

    def __repr__(self) -> str:
        return f"<Amoorion vault={self.link.kind} plugins={self.used} flags={self.flags}>"
