"""Search: find messages of the inbox by their text."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.models import Message


class SearchParams(Model):
    text: str = Field(min_length=1)
    platform: str | None = Field(None, description="only this platform (a hook is hook:<name>)")
    limit: int = Field(20, ge=1, le=1000)


@METHODS.register
class Search(Method):
    name: ClassVar[str] = "search"
    description: ClassVar[str] = "Find messages of the inbox by their text, newest first"
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = SearchParams

    def run(self, params: SearchParams) -> list[Message]:
        return self.inbox.search(params.text, params.platform, params.limit)
