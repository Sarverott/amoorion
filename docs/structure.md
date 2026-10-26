# Structure

The shape of `src/amoorion/`: one core, and namespaces built on it (orders
of phase 0, Q1). Every namespace keeps its own core mechanics in
`<namespace>/base.py`; the ones that can run on their own also have
`<namespace>/__main__.py` (`python -m amoorion.<namespace>`).

```
src/amoorion/
├── __init__.py      version, `main` (the `amoorion` command → cli)
├── core.py          Model, View, JsonView, Controller, Registry, AmoorionError
├── models/          data shared by all: Account, Post, Message, Result
├── vault/           link to the secrets vault (.env); one module per backend
├── plugins/         plugin interface, HttpPlugin, entry point loading; dryrun/
├── methods/         operations: accounts, inbox, plugins, publish, read, reply
├── inbox/           received messages of every platform, SQLite (Q11)
├── hooks/           incoming webhooks → messages
├── cli/             command line: methods as subcommands, servers   (__main__)
├── api/             HTTP API: methods and hooks over HTTP            (__main__)
├── mcp/             MCP server: methods as tools for AI agents       (__main__)
└── daemon/          long-running services in one process            (__main__)

packages/            one package per platform, a uv workspace (Q10)
└── amoorion-<platform>/   pyproject.toml (entry point), src/amoorion_<platform>/, tests/
```

| Package | Platform | Can | Through |
| ------- | -------- | --- | ------- |
| `amoorion-bluesky` | Bluesky | post, read, reply | AT Protocol (XRPC), app password |
| `amoorion-mastodon` | Mastodon | post, read, reply | REST API, access token |
| `amoorion-x` | X (twitter) | post, read, reply | API v2, OAuth 1.0a |
| `amoorion-tumblr` | Tumblr | post, read | API v2 (Neue Post Format), OAuth 1.0a |
| `amoorion-blogger` | Blogger | post | e-mail to the blog's secret address (SMTP, TLS) |
| `amoorion-facebook` | Facebook Page | post, read, reply (comments) | Graph API, Page token |
| `amoorion-discord` | Discord | `discord`: post, read, reply; `discord-webhook`: post | bot token (REST API); channel webhook (Q12) |
| `amoorion-telegram` | Telegram | post, read, reply | Bot API, bot token |
| `amoorion-matrix` | Matrix | post, read, reply | client-server API, access token |

Every package's README lists its secrets. Each is tested against a fake of
its API; `tests/live/` tries each against its real account, only when asked
(`task test:live -- <platform>…`, Q13).

## How they depend on each other

```mermaid
flowchart TD
    core[core.py<br/>Model · View · Controller · Registry]
    models --> core
    vault --> core
    plugins --> models & vault
    methods --> plugins & inbox
    inbox --> models
    hooks --> models & vault
    cli --> methods
    api --> methods & hooks & inbox
    mcp --> methods
    daemon --> api
```

Front-ends (`cli`, `api`, `mcp`, `daemon`) never talk to plugins directly:
everything a person or an agent can do is a **method**. A new operation is
written once in `methods/` and shows up as a CLI subcommand, an API route
and an MCP tool.

## Core: model, view, controller

| Class | In `core.py` | Specialized as |
| ----- | ------------ | -------------- |
| `Model` | pydantic model, unknown fields refused | `models.*`, method params, `VaultLink`, `PluginInfo` |
| `View` | `render(model or list)` | `JsonView` (API, MCP, `--json`), `cli.RichView` (tables) |
| `Controller` | `name`, `description`, a view, `respond()` | `Plugin`, `Method`, `Hook`, `Vault`, `Service`, `Daemon` |
| `Registry` | controllers of one kind by name | `PLUGINS`, `METHODS`, `HOOKS`, vault `BACKENDS` |

## Namespaces

### `models/`

`Account` (platform, handle), `Post` (what to publish: text, title, links,
tags), `Message` (something said on a platform: post, chat line, hook event),
`Result` (one platform's outcome of a method).

### `vault/`

Secrets never live in the repository or in `.env` (Q3). `.env` holds only the
link: `AMOORION_VAULT` (backend), `AMOORION_VAULT_ADDR`,
`AMOORION_VAULT_TOKEN`, `AMOORION_VAULT_PATH`; see `example.env`. Secrets are
named `<platform>/<key>`; every backend keeps one entry per platform with a
field per key. One module per backend (Q6):

| Module | Kind | Where `bluesky/password` is |
| ------ | ---- | --------------------------- |
| `bw_cli.py` | `bitwarden` | item `amoorion/bluesky`, login password (other keys: custom fields) |
| `http_vault.py` | `http` | KV v2 `secret/amoorion/bluesky`, key `password` |
| `kpxc_db_file.py` | `keepassxc` | entry `bluesky` in group `amoorion`, password |
| `default.py` | `env` | variable `AMOORION_SECRET_BLUESKY_PASSWORD` (development) |

### `plugins/`

`Plugin` declares `capabilities` (`post`, `read`, `reply`) and the vault keys
it needs (`secrets`), and implements the calls; anything else raises
`Unsupported`. `HttpPlugin` adds JSON-over-HTTP calls with the platform's
own error reasons. Plugins are found through the entry point group
`amoorion.plugins`, loaded on first use; one that fails to load is listed
with its error. The platforms are packages in `packages/` (above); only
`dryrun` is built in. How to write one: [plugins.md](plugins.md).

### `methods/`

`Method` has `Params` (a model) and `run(params)` returning models.
`read_only` marks methods that change nothing. Built in: `accounts` (which
platforms have their secrets; values never shown), `plugins`, `publish` (one
post to many platforms, one `Result` each, a failing platform doesn't stop
the others), `read` (keeps what it read in the inbox), `reply`, `inbox`.

### `inbox/`

What amoorion received, of every platform, kept once by platform and id in
a SQLite file (`AMOORION_INBOX` in `.env`, default
`$XDG_DATA_HOME/amoorion/inbox.sqlite3`). `read` and the hooks put messages
in; the `inbox` method lists them, newest first, optionally of one platform
(hooks are `hook:<name>`). Rules acting on them come in phase 4 (Q11).

### `hooks/`

`Hook.verify(body, headers)` first, then `receive(payload) → Message`. A hook
whose secret is missing from the vault refuses everything. Built in:
`generic` (`{"text", "author"}` with `X-Amoorion-Token` = secret
`hooks/generic-token`).

### `cli/`

`amoorion <method> --<param> …`, `--json` for machine output; `amoorion api`,
`amoorion mcp`, `amoorion daemon` start the servers.

### `api/`

FastAPI: `GET /`, `POST /methods/<name>` (body = params; `Authorization:
Bearer` = secret `api/token`, without it method calls are off),
`POST /hooks/<name>` (the message goes to the inbox). Binds `127.0.0.1:8000` by default.

### `mcp/`

MCP server (stdio, or streamable HTTP): every method is a tool, read-only
methods carry `readOnlyHint`.

### `daemon/`

`Service` (`run`, `stop`) and `Daemon` running them side by side; when one
ends or fails, the others stop. Services now: the API. Later: platform
listeners (bots) and NATS subscribers.
