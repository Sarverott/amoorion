"""Wiki: the summary of a Wikipedia article."""

from typing import ClassVar
from urllib.parse import quote

import requests
from pydantic import Field

from amoorion.core import AmoorionError, Model
from amoorion.methods.base import METHODS, Method
from amoorion.models import Message


class WikiParams(Model):
    """The article, and the language of Wikipedia."""

    title: str = Field(min_length=1)
    lang: str = Field(
        "en",
        pattern=r"^[a-z-]{2,20}$",
    )


@METHODS.register
class Wiki(Method):
    """A Wikipedia summary as a message, ready for a workflow to post on."""

    name: ClassVar[str] = "wiki"
    description: ClassVar[str] = (
        "The summary of a Wikipedia article, as a message"
    )
    read_only: ClassVar[bool] = True
    Params: ClassVar[type[Model]] = WikiParams

    def run(
        self,
        params: WikiParams,
    ) -> Message:
        """Ask Wikipedia's public REST API; it wants a User-Agent saying who is asking."""

        url = f"https://{params.lang}.wikipedia.org/api/rest_v1/page/summary/{quote(params.title, safe='')}"

        try:
            # Wikipedia refuses clients that don't say who they are.
            response = requests.get(
                url,
                headers={
                    "User-Agent": "amoorion (https://amoorion.readthedocs.io)"
                },
                timeout=30,
            )
        except requests.RequestException as error:
            raise AmoorionError(
                f"Wikipedia can't be reached: {type(error).__name__}"
            ) from None

        if not response.ok:
            raise AmoorionError(
                f"Wikipedia has no {params.title!r} ({response.status_code})"
            )

        body = response.json()

        page = (
            body.get(
                "content_urls",
                {},
            )
            .get(
                "desktop",
                {},
            )
            .get("page")
        )

        return Message(
            platform="wikipedia",
            text=f"{body.get('title', params.title)}: {body.get('extract', '')}",
            url=page,
        )
