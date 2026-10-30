## v0.4.11 (2026-10-30)

**Packages:** amoorion 0.4.11

### Feat

- **app**: Amoorion and Plugins, the author's way of using amoorion from Python

## v0.4.10 (2026-10-30)

**Packages:** amoorion 0.4.10

### Refactor

- **examples**: the notebooks become old.<NAME>.ipynb, making room for the author's new list; the changelog of phase 5

## v0.4.9 (2026-10-30)

**Packages:** amoorion 0.4.9, amoorion-blogger 0.4.2, amoorion-email 0.4.8

### Feat

- **email**: an e-mail client: send by SMTP, read by IMAP, reply; Blogger sends through the same code

## v0.4.8 (2026-10-30)

**Packages:** amoorion 0.4.8

### Feat

- **nats**: results of methods that change something published, and a daemon service keeping what comes in in the inbox; off unless AMOORION_NATS names a server

## v0.4.7 (2026-10-30)

**Packages:** amoorion 0.4.7, amoorion-ntfy 0.4.6

### Feat

- **ntfy**: plugin (post, read) and a notification target: the method notify sends to the platforms of AMOORION_NOTIFY, and everything the hooks receive goes there

## v0.4.6 (2026-10-30)

**Packages:** amoorion 0.4.6

### Feat

- **hooks**: GitHub (signed), GitLab (token) and Discord interactions (Ed25519), each a module of hooks/; vault:new makes their entry

## v0.4.5 (2026-10-30)

**Packages:** amoorion 0.4.5


## v0.4.4 (2026-10-30)

**Packages:** amoorion 0.4.4, amoorion-blogger 0.4.1, amoorion-bluesky 0.4.2, amoorion-discord 0.4.2, amoorion-facebook 0.4.2, amoorion-mastodon 0.4.2, amoorion-matrix 0.4.2, amoorion-telegram 0.4.2, amoorion-tumblr 0.4.2, amoorion-x 0.4.2

### Feat

- **vault**: task vault:new makes an empty entry per platform from schema.vault.json, with what each field is in its notes
- **plugins**: schema.vault.json in every package says what its vault entry holds, like the scopes of OpenAPI; Plugin.schema() reads it

## v0.4.3 (2026-10-30)

**Packages:** amoorion 0.4.3

### Feat

- **vault**: task vault:new and vault:status for KeePassXC, the vault for now: the file of AMOORION_VAULT_PATH, never overwritten; example.env links to it
- **vault**: KeePassXC is a dependency of amoorion, not an extra: pykeepass always there, ~ in the path of the file

### Fix

- **tests**: no test reads the vault of the user's .env; vault.sh trusts .env over what it inherits

### Refactor

- **tasks**: the root Taskfile splits into a tree: each directory keeps the tasks of its own context, every name stays

## v0.4.2 (2026-10-27)

**Packages:** amoorion 0.4.2


## v0.4.1 (2026-10-27)

**Packages:** amoorion 0.4.1, amoorion-bluesky 0.4.1, amoorion-discord 0.4.1, amoorion-facebook 0.4.1, amoorion-mastodon 0.4.1, amoorion-matrix 0.4.1, amoorion-telegram 0.4.1, amoorion-tumblr 0.4.1, amoorion-x 0.4.1

### Feat

- **dev**: the state shows every package with its version now and in the next release, and what kind the next release is (Z, Y or X)
- **vault**: the Bitwarden vault through bw from tools/ (npm); task vault:login logs in, unlocks and writes the session into .env (Q13), vault:lock empties it, vault:status shows it
- **matrix**: delete by redacting the event; read skips redacted events; its profile is the room
- **telegram**: delete a message in its chat; its profile is chat<id>
- **discord**: the bot deletes messages in its channel, the webhook deletes what it posted; profiles channel-<id> and webhook-<id>
- **facebook**: delete a post or comment of the page; its profile is the page id
- **tumblr**: delete a post; its profile is the blog
- **x**: delete a post; its profile is the username
- **mastodon**: delete a status; its profile is acct@server
- **bluesky**: delete its own posts (com.atproto.repo.deleteRecord); its profile is the handle
- **dataset**: the posts of every profile on every platform as JSON files with an index, dataset/<platform>/<profile>/ (Q14); snapshot reads them, read keeps what it saw, delete keeps a copy before deleting

### Fix

- **dataset**: the dataset package itself into git: dataset/ in .gitignore had kept src/amoorion/dataset/ out
- **live**: a platform skipped for missing secrets tells the vault's reason; a locked vault points to task vault:login

### Refactor

- **plugins**: every plugin names its capabilities, so a new capability is never claimed by accident

## v0.4.0 (2026-10-27)

**Packages:** amoorion 0.4.0, amoorion-blogger 0.4.0, amoorion-bluesky 0.4.0, amoorion-discord 0.4.0, amoorion-facebook 0.4.0, amoorion-mastodon 0.4.0, amoorion-matrix 0.4.0, amoorion-telegram 0.4.0, amoorion-tumblr 0.4.0, amoorion-x 0.4.0

### Feat

- **site**: the web page gets a 404 page, robots.txt and llms.txt

## v0.3.5 (2026-10-27)

**Packages:** amoorion 0.3.5


## v0.3.4 (2026-10-27)

**Packages:** amoorion 0.3.4

### Feat

- **site**: the web page is the presentation page of amoorion-website (built by vite for /amoorion/) with the marimo examples, project and releases pages in its style, and manifest files

## v0.3.3 (2026-10-27)

**Packages:** amoorion 0.3.3

### Fix

- **dev**: a final that only renews the changelog commits as "bump: changelog of X", not "X → X"

## v0.3.2 (2026-10-27)

**Packages:** amoorion 0.3.2

### Feat

- **dev**: a version per package (Q15): Z bumps amoorion and the packages changed since the last release, Y (a phase) and X (the last phase) all; packages --released lists what a release bumped

### Fix

- **commits**: the flow's merges of release pull requests ("Release v…") pass commitizen's check

## v0.3.1 (2026-10-27)

### Fix

- **gh-pages**: keep the page in the github-pages branch before asking for Pages

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
