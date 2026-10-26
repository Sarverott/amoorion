# Writing a plugin

A plugin connects amoorion to one platform. Every plugin shares one
interface, `amoorion.plugins.Plugin`, and is found through the Python entry
point group `amoorion.plugins` (decision Q7), whether it lives in this
repository or in a separate package.

## The interface

```python
from typing import ClassVar

from amoorion.models import Message, Post
from amoorion.plugins import Capability, Plugin


class Mastodon(Plugin):
    name: ClassVar[str] = "mastodon"                # = the entry point name
    description: ClassVar[str] = "Mastodon through its REST API"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST, Capability.READ})
    secrets: ClassVar[tuple[str, ...]] = ("token", "uri")  # read as mastodon/token, mastodon/uri

    def post(self, post: Post) -> Message: ...
    def read(self, limit: int = 20) -> list[Message]: ...
    # reply(to, text) is left out: Capability.REPLY isn't declared, so it raises Unsupported
```

- `self.secret("token")` reads `mastodon/token` from the vault; never take
  secrets from anywhere else.
- Raise `amoorion.core.AmoorionError` (or `Unsupported`) with a message a
  person can act on; the `publish` method turns it into that platform's
  failed `Result` and goes on with the others.
- Return `Message` with `id` and `url` when the platform gives them.

## Registering it

In the package's `pyproject.toml`:

```toml
[project.entry-points."amoorion.plugins"]
mastodon = "amoorion_mastodon:Mastodon"
```

Install the package next to amoorion (`uv add amoorion-mastodon`, or
`uv pip install -e ../amoorion-mastodon` while developing) and
`amoorion plugins` lists it. A plugin that fails to load is listed with its
error; amoorion keeps working.

Built-in plugins live in `src/amoorion/plugins/<platform>/` and are declared
in this repository's `pyproject.toml` the same way.

## Testing

Test against a fake of the platform's API (a local HTTP server, see
`tests/test_vault_http.py`), never against real accounts.
