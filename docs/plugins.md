# Writing a plugin

A plugin connects amoorion to one platform. Every plugin shares one
interface, `amoorion.plugins.Plugin`, and is found through the Python entry
point group `amoorion.plugins` (decision Q7). Each platform is its own
package in this repository's uv workspace, `packages/amoorion-<platform>/`
(decision Q10); a package from anywhere else works the same way.

Start one with:

```sh
uv run task plugin:new -- mastodon Mastodon "Mastodon plugin of amoorion: …"
```

## The interface

```python
from typing import ClassVar

from amoorion.models import Message, Post
from amoorion.plugins import Capability, HttpPlugin


class Mastodon(HttpPlugin):
    name: ClassVar[str] = "mastodon"                # = the entry point name
    description: ClassVar[str] = "Mastodon through its REST API"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST, Capability.READ})
    secrets: ClassVar[tuple[str, ...]] = ("token", "uri")  # read as mastodon/token, mastodon/uri

    def post(self, post: Post) -> Message: ...
    def read(self, limit: int = 20) -> list[Message]: ...
    # reply(to, text) is left out: Capability.REPLY isn't declared, so it raises Unsupported
```

- `HttpPlugin.request(method, url, …)` sends, and turns network failures and
  error answers into `AmoorionError` with the platform's own reason
  (override `reason` when the platform words it differently); a plugin that
  doesn't speak HTTP subclasses `Plugin` (see `amoorion-blogger`).
- `self.secret("token")` reads `mastodon/token` from the vault; never take
  secrets from anywhere else.
- Raise `amoorion.core.AmoorionError` (or `Unsupported`) with a message a
  person can act on; the `publish` method turns it into that platform's
  failed `Result` and goes on with the others.
- Return `Message` with `id` and `url` when the platform gives them.

## Registering it

In the package's `pyproject.toml` (`task plugin:new` writes it):

```toml
[project.entry-points."amoorion.plugins"]
mastodon = "amoorion_mastodon:Mastodon"
```

Workspace packages are in the root's `dev` group, so `uv sync` installs them
and `amoorion plugins` lists them. Outside the repository: install amoorion
and the plugin package side by side (`uv add amoorion amoorion-mastodon`).
A plugin that fails to load is listed with its error; amoorion keeps
working.

Only `dryrun` stays built in (`src/amoorion/plugins/dryrun/`), for trying
amoorion without accounts.

## Testing

Tests go in the package's `tests/`; `task check` runs them with the rest.
Test against a fake of the platform's API (a local HTTP server, as in every
package's tests), never against real accounts.
