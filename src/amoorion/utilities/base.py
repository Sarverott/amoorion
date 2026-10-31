"""Small helpers that aren't methods: nothing here reaches a platform by itself."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from dotenv import dotenv_values, set_key

from amoorion.workflows.base import fill
from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.vault import Vault


def read_env(path: str | Path) -> dict[str, str | None]:
    """An env file as a dict; comments and quotes dealt with."""

    return dotenv_values(path)


def write_env(
    path: str | Path,
    **values: str,
) -> Path:
    """Set values in an env file, made if missing; other lines and comments stay as they are."""

    path = Path(path).expanduser()

    path.touch()

    for name, value in values.items():
        set_key(
            path,
            name,
            value,
            quote_mode="auto",
        )

    return path


def post_from_markdown(
    source: str | Path,
    values: dict[str, str] | None = None,
) -> tuple[Post, list[str]]:
    """A Markdown text or file as a post, and the platforms its front matter names.

    ---
    title: Hello
    tags: [news]
    links: [https://example.org]
    to: [mastodon, bluesky]
    ---
    The text of the post.

    `values` fill the names of a template (a dollar and the name), after parsing: they can't change the settings.
    """

    text = source.read_text() if isinstance(source, Path) else source

    meta: dict[str, Any] = {}

    if text.startswith("---\n"):
        head, separator, body = text[4:].partition("\n---\n")

        if not separator:
            raise AmoorionError("the front matter is not closed by ---")

        meta, text = yaml.safe_load(head) or {}, body

    to = meta.pop(
        "to",
        [],
    )

    if values:
        text = fill(
            text,
            values,
        )

        meta = fill(
            meta,
            values,
        )

    return Post(text=text.strip(), **meta), [to] if isinstance(
        to, str
    ) else list(to)


def open_tunnel(
    port: int,
    vault: Vault,
    forward: Callable[..., Any] | None = None,
) -> Any:
    """Make a local port reachable from outside by ngrok, for hooks: the secret `ngrok/token`.

    Anyone with the address reaches that port, so only the API, whose methods need
    their token and whose hooks verify themselves, belongs behind it. `ngrok` is not a
    dependency: `pip install ngrok`. Returns the listener (`.url()`, `.close()`).
    """

    if forward is None:
        try:
            from ngrok import forward
        except ImportError:
            raise AmoorionError(
                "the tunnel needs the package ngrok: pip install ngrok"
            ) from None

    return forward(
        port,
        authtoken=vault.get("ngrok/token"),
    )
