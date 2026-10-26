"""Methods: what amoorion can do, independent of who asks.

A method has `Params` (a model, so every front-end can build its own
arguments, request body or tool schema from it) and `run`, which returns
models. Front-ends never talk to plugins directly.
"""

from typing import Any, ClassVar

from pydantic import Field

from amoorion.core import Controller, Model, Registry, View
from amoorion.models import Message, Post, Result
from amoorion.plugins import PLUGINS, Capability, open_plugin
from amoorion.vault import Vault, open_vault


class NoParams(Model):
    pass


class Method(Controller):
    Params: ClassVar[type[Model]] = NoParams
    # True when the method changes nothing anywhere (agents may call it freely).
    read_only: ClassVar[bool] = False

    def __init__(self, vault: Vault | None = None, view: View | None = None) -> None:
        super().__init__(view)
        self._vault = vault

    @property
    def vault(self) -> Vault:
        if self._vault is None:
            self._vault = open_vault()
        return self._vault

    def run(self, params: Model) -> Model | list[Model]:
        raise NotImplementedError

    def __call__(self, **params: Any) -> Any:
        return self.respond(self.run(self.Params(**params)))


METHODS: Registry[type[Method]] = Registry("method")


class PluginInfo(Model):
    name: str
    description: str
    capabilities: list[Capability]


@METHODS.register
class Plugins(Method):
    name: ClassVar[str] = "plugins"
    description: ClassVar[str] = "List the platform plugins and what they can do"
    read_only: ClassVar[bool] = True

    def run(self, params: Model) -> list[PluginInfo]:
        return [
            PluginInfo(name=plugin.name, description=plugin.description, capabilities=sorted(plugin.capabilities))
            for plugin in map(PLUGINS.get, PLUGINS.names())
        ]


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


class ReadParams(Model):
    platform: str
    limit: int = Field(20, ge=1, le=200)


@METHODS.register
class Read(Method):
    name: ClassVar[str] = "read"
    description: ClassVar[str] = "Read the latest messages of one platform"
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = ReadParams

    def run(self, params: ReadParams) -> list[Message]:
        return open_plugin(params.platform, self.vault).read(params.limit)
