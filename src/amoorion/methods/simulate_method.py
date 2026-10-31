"""Simulate: personas reacting to a topic, in memory only."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.models import Message
from amoorion.society import Persona, Society
from amoorion.society.base import by_model, scripted


class SimulateParams(Model):
    """A topic, who reacts to it, for how long, and whether a language model does the talking."""

    topic: str = Field(min_length=1)
    personas: list[Persona] = Field(
        min_length=1,
        max_length=100,
    )
    rounds: int = Field(
        3,
        ge=1,
        le=50,
    )
    run: str = Field(
        "default",
        pattern=r"^[A-Za-z0-9._-]+$",
        description="kept in the inbox as society:<run>",
    )
    llm: bool = Field(
        False,
        description="reactions from a language model instead of scripted lines",
    )


@METHODS.register
class Simulate(Method):
    """Personas talking about a topic, for trying out rules and workflows on a crowd."""

    name: ClassVar[str] = "simulate"
    description: ClassVar[str] = (
        "Simulate personas reacting to a topic, locally: nothing reaches any platform"
    )
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = SimulateParams

    def run(
        self,
        params: SimulateParams,
    ) -> list[Message]:
        """The feed goes into the inbox under `society:<run>`; no platform is touched."""

        think = by_model(self.vault) if params.llm else scripted

        return self.inbox.keep(
            Society(
                params.personas,
                think,
                params.run,
            ).simulate(
                params.topic,
                params.rounds,
            )
        )
