"""Publish: one post on several platforms."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method
from amoorion.models import Post, Result
from amoorion.plugins import open_plugin


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
