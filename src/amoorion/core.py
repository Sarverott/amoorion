"""Core mechanics every namespace of amoorion builds on.

Model, view, controller: a model holds data, a view presents models to one
audience (terminal, JSON for the API and MCP), a controller does the work and
hands what it made to its view. Each namespace (`amoorion.<namespace>.base`)
specializes these three.
"""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


# model class
class Model(BaseModel):
    """Data amoorion knows about: a message, an account, a result."""

    model_config = ConfigDict(extra="forbid")


# view class
class View:
    """Presents models to one audience."""

    def render(
        self,
        model: Model | list[Model],
    ) -> Any:
        """Turn a result into what this view gives out."""

        raise NotImplementedError


class JsonView(View):
    """Plain JSON-compatible data, for the API, MCP and machine output."""

    def render(
        self,
        model: Model | list[Model],
    ) -> Any:
        """Plain JSON-compatible data: dicts, or a list of them."""

        if isinstance(model, list):
            return [item.model_dump(mode="json") for item in model]

        return model.model_dump(mode="json")


# controller class
class Controller:
    """Does the work of one element and answers through its view.

    `name` identifies the element in its registry (a plugin's platform, a
    method's command), `description` is shown to people and agents.
    """

    name: ClassVar[str] = ""
    description: ClassVar[str] = ""

    def __init__(
        self,
        view: View | None = None,
    ) -> None:
        """Answer through the given view, by default as plain data."""

        self.view = view or JsonView()

    def respond(
        self,
        model: Model | list[Model],
    ) -> Any:
        """A result through this controller's view."""

        return self.view.render(model)


class AmoorionError(Exception):
    """Base of every error amoorion raises on purpose."""


class Registry[T: type[Controller]]:
    """Controllers of one kind, by name."""

    def __init__(
        self,
        kind: str,
    ) -> None:
        """An empty registry; `kind` names its items in the error for an unknown name."""

        self.kind = kind

        self._items: dict[str, T] = {}

    def register(
        self,
        item: T,
    ) -> T:
        """Add a controller class; usable as a decorator."""

        if not item.name:
            raise AmoorionError(f"{self.kind} {item.__qualname__} has no name")

        if item.name in self._items and self._items[item.name] is not item:
            raise AmoorionError(
                f"{self.kind} {item.name!r} is registered twice"
            )

        self._items[item.name] = item

        return item

    def get(
        self,
        name: str,
    ) -> T:
        """The item of that name; a clear error otherwise."""

        try:
            return self._items[name]
        except KeyError:
            raise AmoorionError(f"no {self.kind} named {name!r}") from None

    def names(self) -> list[str]:
        """All names, sorted: lists stay in the same order everywhere."""

        return sorted(self._items)

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """Whether a name is registered."""

        return name in self._items
