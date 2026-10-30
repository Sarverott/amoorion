"""Compose: ask a language model to write something."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.utilities.llm import Composition, complete


class ComposeParams(Model):
    prompt: str = Field(min_length=1)
    system: str | None = Field(None, description="how the model should behave")
    model: str | None = Field(None, description="else llm/model of the vault")


@METHODS.register
class Compose(Method):
    name: ClassVar[str] = "compose"
    description: ClassVar[str] = "Ask a language model (llm/url of the vault, any OpenAI-compatible server) to write something"
    Params: ClassVar[type[Model]] = ComposeParams

    def run(self, params: ComposeParams) -> Composition:
        return complete(params.prompt, self.vault, params.system, params.model)
