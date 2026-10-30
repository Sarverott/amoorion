"""Methods: what amoorion can do, independent of who asks.

A method has `Params` (a model, so every front-end can build its own
arguments, request body or tool schema from it) and `run`, which returns
models. Front-ends never talk to plugins directly.
"""

import os
from functools import wraps
from typing import Any, ClassVar

from pydantic import Field

from amoorion.core import AmoorionError, Controller, Model, Registry, View
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.models import Message, Post, Result
from amoorion.nats import announce
from amoorion.plugins import FAILED, Capability, Plugin, load_plugins, open_plugin
from amoorion.vault import Vault, open_vault


class NoParams(Model):
    pass


class Method(Controller):
    Params: ClassVar[type[Model]] = NoParams
    # True when the method changes nothing on any platform (agents may call it freely);
    # keeping what it read in the local inbox doesn't count.
    read_only: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """What a method that changes something returned also goes out on NATS, whoever asked."""
        super().__init_subclass__(**kwargs)
        if cls.read_only or "run" not in cls.__dict__:
            return
        run = cls.run

        @wraps(run)
        def announced(self: "Method", params: Model) -> Any:
            result = run(self, params)
            announce(cls.name, result, self._vault)
            return result

        cls.run = announced  # type: ignore[method-assign]

    def __init__(
        self, vault: Vault | None = None, view: View | None = None, inbox: Inbox | None = None, dataset: Dataset | None = None
    ) -> None:
        super().__init__(view)
        self._vault = vault
        self._inbox = inbox
        self._dataset = dataset

    @property
    def vault(self) -> Vault:
        if self._vault is None:
            self._vault = open_vault()
        return self._vault

    @property
    def inbox(self) -> Inbox:
        if self._inbox is None:
            self._inbox = Inbox()
        return self._inbox

    @property
    def dataset(self) -> Dataset:
        if self._dataset is None:
            self._dataset = Dataset()
        return self._dataset

    def run(self, params: Model) -> Model | list[Model]:
        raise NotImplementedError

    def __call__(self, **params: Any) -> Any:
        return self.respond(self.run(self.Params(**params)))


METHODS: Registry[type[Method]] = Registry("method")


def profile_of(plugin: Plugin) -> str:
    """The plugin's profile; "default" when the platform can't tell it now."""
    try:
        return plugin.profile() or "default"
    except AmoorionError:
        return "default"


class PluginInfo(Model):
    name: str
    description: str
    capabilities: list[Capability]
    error: str | None = None


@METHODS.register
class Plugins(Method):
    name: ClassVar[str] = "plugins"
    description: ClassVar[str] = "List the platform plugins and what they can do"
    read_only: ClassVar[bool] = True

    def run(self, params: Model) -> list[PluginInfo]:
        plugins = load_plugins()
        return [
            PluginInfo(name=plugin.name, description=plugin.description, capabilities=sorted(plugin.capabilities))
            for plugin in map(plugins.get, plugins.names())
        ] + [
            PluginInfo(name=name, description="failed to load", capabilities=[], error=error)
            for name, error in sorted(FAILED.items())
        ]


def plugsFlagsToList(flags: dict[str, bool]) -> list[str]:  # noqa: N802 - the author's name for it
    """The names of the flags that are on, e.g. of `Plugins["x"].infoflags`."""
    return [name for name, on in flags.items() if on]


class AccountStatus(Model):
    platform: str
    ready: bool
    missing: list[str] = []
    error: str | None = None


@METHODS.register
class Accounts(Method):
    name: ClassVar[str] = "accounts"
    description: ClassVar[str] = "Which platforms have their secrets in the vault (values never shown)"
    read_only: ClassVar[bool] = True

    def run(self, params: Model) -> list[AccountStatus]:
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
            statuses.append(AccountStatus(platform=plugin.name, ready=not missing, missing=missing, error=error))
        return statuses


class PublishParams(Post):
    to: list[str] = Field(min_length=1, description="platforms to publish on")


@METHODS.register
class Publish(Method):
    name: ClassVar[str] = "publish"
    description: ClassVar[str] = "Publish one post on several platforms; one result per platform"
    Params: ClassVar[type[Model]] = PublishParams

    def run(self, params: PublishParams) -> list[Result]:
        post = Post.model_validate(params.model_dump(exclude={"to"}))
        results = []
        for platform in params.to:
            try:
                results.append(Result(platform=platform, ok=True, message=open_plugin(platform, self.vault).post(post)))
            except Exception as error:  # one platform failing must not stop the others
                results.append(Result(platform=platform, ok=False, error=str(error)))
        return results


class NotifyParams(Post):
    pass


@METHODS.register
class Notify(Method):
    name: ClassVar[str] = "notify"
    description: ClassVar[str] = "Send a notification to the platforms of AMOORION_NOTIFY; one result per platform"
    Params: ClassVar[type[Model]] = NotifyParams

    def run(self, params: NotifyParams) -> list[Result]:
        targets = [name.strip() for name in os.environ.get("AMOORION_NOTIFY", "").split(",") if name.strip()]
        if not targets:
            return []
        return Publish(self.vault).run(PublishParams(to=targets, **params.model_dump()))


class ReadParams(Model):
    platform: str
    limit: int = Field(20, ge=1, le=200)


@METHODS.register
class Read(Method):
    name: ClassVar[str] = "read"
    description: ClassVar[str] = "Read the latest messages of one platform (and keep them in the inbox and the dataset)"
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = ReadParams

    def run(self, params: ReadParams) -> list[Message]:
        plugin = open_plugin(params.platform, self.vault)
        messages = self.inbox.keep(plugin.read(params.limit))
        self.dataset.record(plugin.name, profile_of(plugin), messages)
        return messages


class SnapshotParams(Model):
    platform: str
    limit: int = Field(100, ge=1, le=200, description="at most this many posts; fewer read means all were read")


class Snapshot(Model):
    platform: str
    profile: str
    path: str
    read: int
    complete: bool
    present: int
    gone: int
    deleted: int


@METHODS.register
class SnapshotMethod(Method):
    name: ClassVar[str] = "snapshot"
    description: ClassVar[str] = "Read the posts of one platform's profile into the dataset (JSON files with an index)"
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = SnapshotParams

    def run(self, params: SnapshotParams) -> Snapshot:
        plugin = open_plugin(params.platform, self.vault)
        profile = profile_of(plugin)
        messages = plugin.read(params.limit)
        # Fewer than asked for: the platform gave all it has, so what wasn't seen is gone.
        complete = len(messages) < params.limit
        self.dataset.record(plugin.name, profile, self.inbox.keep(messages), complete=complete)
        states = [entry.state for entry in self.dataset.index(plugin.name, profile).values()]
        return Snapshot(
            platform=plugin.name,
            profile=profile,
            path=str(self.dataset.profile_dir(plugin.name, profile)),
            read=len(messages),
            complete=complete,
            present=states.count("present"),
            gone=states.count("gone"),
            deleted=states.count("deleted"),
        )


class InboxParams(Model):
    platform: str | None = Field(None, description="only this platform (a hook is hook:<name>)")
    limit: int = Field(20, ge=1, le=1000)


@METHODS.register
class InboxMethod(Method):
    name: ClassVar[str] = "inbox"
    description: ClassVar[str] = "Messages received so far, of every platform and hook, newest first"
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = InboxParams

    def run(self, params: InboxParams) -> list[Message]:
        return self.inbox.list(params.platform, params.limit)


class ReplyParams(Model):
    platform: str
    to: str = Field(description="id of the message to answer, as read or publish gave it")
    text: str = Field(min_length=1)


@METHODS.register
class Reply(Method):
    name: ClassVar[str] = "reply"
    description: ClassVar[str] = "Answer one message on its platform"
    Params: ClassVar[type[Model]] = ReplyParams

    def run(self, params: ReplyParams) -> Message:
        to = Message(platform=params.platform, text="", id=params.to)
        return open_plugin(params.platform, self.vault).reply(to, params.text)


class DeleteParams(Model):
    platform: str
    id: str = Field(description="id of the message to delete, as read or publish gave it")


@METHODS.register
class Delete(Method):
    name: ClassVar[str] = "delete"
    description: ClassVar[str] = "Delete one message on its platform, keeping a copy in the dataset first"
    Params: ClassVar[type[Model]] = DeleteParams

    def _known(self, plugin: Plugin, profile: str, id: str) -> Message:
        """What is known of the message: from the dataset, else from a read, else only its id."""
        found = self.dataset.find(plugin.name, profile, id)
        if found is None and Capability.READ in plugin.capabilities:
            try:
                found = next((message for message in plugin.read(100) if message.id == id), None)
            except AmoorionError:
                found = None
        return found or Message(platform=plugin.name, text="", id=id)

    def run(self, params: DeleteParams) -> Result:
        plugin = open_plugin(params.platform, self.vault)
        if Capability.DELETE not in plugin.capabilities:
            return Result(platform=plugin.name, ok=False, error=f"{plugin.name} can't delete")
        profile = profile_of(plugin)
        message = self._known(plugin, profile, params.id)
        self.dataset.keep_deleted(plugin.name, profile, message)
        try:
            plugin.delete(message)
        except AmoorionError as error:
            return Result(platform=plugin.name, ok=False, message=message, error=str(error))
        self.dataset.deleted(plugin.name, profile, message)
        return Result(platform=plugin.name, ok=True, message=message)
