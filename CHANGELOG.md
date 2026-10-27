## v0.3.0 (2026-10-27)

### Feat

- **cli**: amoorion alone asks step by step: the method, its parameters, platforms by what they can do, a confirmation before changing anything; results show messages as text
- **tools**: amoorion-dev, the development tools: state of development, versions of the loop, phases, release notes, web page; settings in .github/flow.toml

### Fix

- **publish**: PyPI gets one package at a time, skipping files already there, and waits out its limit on new projects (429 stopped v0.2.1 after four)

## v0.2.1 (2026-10-26)

### Fix

- __version__ comes from the installed package; it stayed 0.1.0 while the package was 0.2.0, so the docs showed another version

## v0.2.0 (2026-10-26)

### Feat

- **plugins**: Matrix plugin package: posts, reads and replies in one room (client-server API)
- **plugins**: Telegram plugin package: a bot posts, reads and replies in one chat (Bot API)
- **plugins**: Discord plugin package: a bot (post, read, reply) and a channel webhook (post), Q12
- **plugins**: HttpPlugin hides secrets that are part of URLs from its errors
- **inbox**: received messages kept in SQLite; read and hooks fill it, the inbox method lists it (Q11)
- **plugins**: Facebook plugin package: Page posts, read, replies as comments (Graph API)
- **plugins**: Blogger plugin package: posting by mail, TLS only
- **plugins**: Tumblr plugin package: post in the Neue Post Format with tags, read
- **plugins**: X (twitter) plugin package: API v2 with OAuth 1.0a, weighted 280 characters
- **plugins**: Mastodon plugin package: post, read, reply, the server's own character limit
- **methods**: reply method, answering one message by its id
- **plugins**: Bluesky plugin over the AT Protocol: post with link and tag facets, read, reply
- **methods**: accounts method, which platforms have their secrets in the vault
- **plugins**: plugins found through the amoorion.plugins entry points, dryrun included (Q7)
- **vault**: KeePassXC database file backend, pykeepass as the keepassxc extra (Q6)
- **vault**: HashiCorp Vault / OpenBao backend, KV v2 over HTTP (Q6)
- **vault**: Bitwarden / Vaultwarden backend through the bw CLI (Q6, first)
- **daemon**: services run side by side, one ending stops the rest; the API as first service
- **mcp**: the methods as MCP tools, read-only ones marked so
- **api**: FastAPI over the methods (bearer token from the vault) and the hooks
- **hooks**: webhook base verifying calls before reading them; token-guarded generic hook
- **cli**: subcommands built from the methods, rich tables or --json, server subcommands
- **methods**: plugins, publish and read methods with typed params for every front-end
- **plugins**: plugin base with capabilities and vault secrets; dryrun platform for development
- **vault**: link to the secrets vault from .env, development env backend (backend choice is Q6)
- **models**: accounts, posts, messages and results shared by every namespace
- **core**: model, view and controller bases with a registry, from the author's sketch
- the author's namespace sketch (core.py), runtime dependencies and orders on Q1-Q5
- uv package skeleton with the amoorion CLI entry point

### Fix

- **docs**: the requirements check compares only the pins, as uv versions word markers differently (CI failed on it)
- importing a __main__ module starts nothing (the API reference imports every module)
- **plugins**: load plugins on first use, not when amoorion.plugins is imported

### Refactor

- **plugins**: HttpPlugin shares the HTTP calls and error reasons of the platform plugins
- **plugins**: uv workspace; Bluesky moved into its own package, packages/amoorion-bluesky (Q10)
- **vault**: one module per backend, the .env setup in default.py; path in the link
