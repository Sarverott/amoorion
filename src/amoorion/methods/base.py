"""Methods: what amoorion can do, independent of who asks.

A method has `Params` (a model, so every front-end can build its own
arguments, request body or tool schema from it) and `run`, which returns
models. Front-ends never talk to plugins directly. This file is what all
methods share; each method is a file of its own, `<name>_method.py`.
"""

from functools import wraps
from typing import Any, ClassVar

from amoorion.core import AmoorionError, Controller, Model, Registry, View
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.nats import announce
from amoorion.plugins import Plugin
from amoorion.vault import Vault, open_vault


class NoParams(Model):
    """For a method that takes nothing."""

    pass


class Method(Controller):
    """One operation of amoorion, the same for every front-end.

    A subclass names itself, declares `Params` and implements `run`; registered in
    `METHODS`, it appears in the CLI, the API, the MCP server and `Amoorion`.
    """

    Params: ClassVar[type[Model]] = NoParams
    # True when the method changes nothing on any platform (agents may call it freely);
    # keeping what it read in the local inbox doesn't count.
    read_only: ClassVar[bool] = False

    def __init_subclass__(
        cls,
        **kwargs: Any,
    ) -> None:
        """What a method that changes something returned also goes out on NATS, whoever asked."""

        super().__init_subclass__(**kwargs)

        if cls.read_only or "run" not in cls.__dict__:
            return

        run = cls.run

        @wraps(run)
        def announced(
            self: "Method",
            params: Model,
        ) -> Any:

            result = run(
                self,
                params,
            )

            announce(
                cls.name,
                result,
                self._vault,
            )

            return result

        cls.run = announced  # type: ignore[method-assign]

    def __init__(
        self,
        vault: Vault | None = None,
        view: View | None = None,
        inbox: Inbox | None = None,
        dataset: Dataset | None = None,
    ) -> None:
        """Whatever isn't given opens from the environment on first use."""

        super().__init__(view)

        self._vault = vault

        self._inbox = inbox

        self._dataset = dataset

    @property
    def vault(self) -> Vault:
        """The vault given, or the environment's when first needed."""

        if self._vault is None:
            self._vault = open_vault()

        return self._vault

    @property
    def inbox(self) -> Inbox:
        """The inbox given, or the environment's when first needed."""

        if self._inbox is None:
            self._inbox = Inbox()

        return self._inbox

    @property
    def dataset(self) -> Dataset:
        """The dataset given, or the environment's when first needed."""

        if self._dataset is None:
            self._dataset = Dataset()

        return self._dataset

    def run(
        self,
        params: Model,
    ) -> Model | list[Model]:
        """Do the work; takes validated parameters, answers models."""

        raise NotImplementedError

    def __call__(
        self,
        **params: Any,
    ) -> Any:
        """Validate the parameters, run, and answer through the view."""

        return self.respond(self.run(self.Params(**params)))


METHODS: Registry[type[Method]] = Registry("method")


def profile_of(plugin: Plugin) -> str:
    """The plugin's profile; "default" when the platform can't tell it now."""

    try:
        return plugin.profile() or "default"
    except AmoorionError:
        return "default"
