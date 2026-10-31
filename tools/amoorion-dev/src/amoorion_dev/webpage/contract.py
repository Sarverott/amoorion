"""What the site promises other programs, amoorion-website first: the shape of manifest.json,
and where amoorion's own facts come from. Imported only when building the site, as it loads amoorion."""

from typing import Any

from pydantic import BaseModel


class Platform(BaseModel):
    """One platform plugin and what it can do."""

    name: str
    description: str
    capabilities: list[str]


class Manifest(BaseModel):
    """manifest.json: what a release holds. `pages` is empty until the whole site is built."""

    name: str
    version: str
    repository: str
    docs: str
    openapi: str
    packages: dict[str, str]
    platforms: list[Platform]
    pages: list[str]
    examples: list[str]


def openapi() -> dict[str, Any]:
    """The OpenAPI document of the HTTP API, made in a sandbox: no server, no secrets."""

    from amoorion import Amoorion

    from amoorion.api import create_app

    amo = Amoorion()

    return create_app(
        amo.vault,
        amo.store,
        amo.dataset,
    ).openapi()


def platforms() -> list[Platform]:
    """Every platform plugin. A plugin failing to load stops the build: the site would lie by leaving it out."""

    from amoorion import Amoorion

    found = Amoorion().plugins()

    failed = [plugin["name"] for plugin in found if plugin["error"]]

    if failed:
        raise RuntimeError(f"plugins failed to load: {', '.join(failed)}")

    return [
        Platform(
            name=plugin["name"],
            description=plugin["description"],
            capabilities=plugin["capabilities"],
        )
        for plugin in found
    ]
