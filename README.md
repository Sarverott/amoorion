# amoorion

<p align="center">
  <img src="https://raw.githubusercontent.com/Sarverott/amoorion/master/resources/images/Amoorion%20rose-gold%20gothic%20wordmark.png" alt="amoorion" width="600">
</p>

<p align="center">
  <b>One heart for all your conversations.</b><br>
  Universal tool for administration of chatting and communication platforms
</p>

<p align="center">
  <a href="https://sarverott.github.io/amoorion">web page</a> ·
  <a href="https://amoorion.readthedocs.io">documentation</a> ·
  <a href="https://pypi.org/project/amoorion/">PyPI</a> ·
  <a href="https://github.com/Sarverott/amoorion">GitHub</a>
</p>

[![check](https://github.com/Sarverott/amoorion/actions/workflows/check.yml/badge.svg)](https://github.com/Sarverott/amoorion/actions/workflows/check.yml) [![release](https://github.com/Sarverott/amoorion/actions/workflows/release.yml/badge.svg)](https://github.com/Sarverott/amoorion/actions/workflows/release.yml) [![publish](https://github.com/Sarverott/amoorion/actions/workflows/publish.yml/badge.svg)](https://github.com/Sarverott/amoorion/actions/workflows/publish.yml) [![gh-pages](https://github.com/Sarverott/amoorion/actions/workflows/gh-pages.yml/badge.svg)](https://github.com/Sarverott/amoorion/actions/workflows/gh-pages.yml)

---
<!--
## **EARLY STAGE OF PROJECT**

The core works end to end, with plugins for Bluesky, Mastodon, X, Tumblr,
Blogger, Facebook, Discord (bot or webhook), Telegram and Matrix, tested
only against fakes of their APIs so far, not yet against real accounts. `dryrun` sends nothing, for trying.
Plan: [docs/devlog/VISION.md](docs/devlog/VISION.md).

---

## What it will do

Write once, post everywhere, read and answer from one place, and link it
with the services around it.

#### Publication platforms
- twitter (x.com) posting by api
- bluesky posting
- tumblr posting by api
- blogger posting by mail
- facebook posting
- mastodon posting

#### Communication platforms
- discord
- telegram
- matrix
- ~whatsapp~
- ~signal~

#### Additional functionality
- email client
- ~rss feed receiver~
- ~phone manage by adb~
- webhooks - standard linkings with services like gitlab, github, discord etc.
- ntfy notifications
- nats.io

-->

## Getting started

#### documentation: https://amoorion.readthedocs.io

```sh
pip install amoorion amoorion-bluesky        # the core and the platforms you use
amoorion                                     # asks step by step what to do
amoorion publish --text "hello" --to dryrun  # dryrun sends nothing: try it first
```

## What it does

<img src="https://raw.githubusercontent.com/Sarverott/amoorion/master/resources/images/Amoorion%E2%80%99s%20Cupid%20Bot%20Sends%20Heart%20Messages-2-mini.png" alt="Amoorion's cupid bot" width="220" align="right">

- **Publish:** write once, post to every platform you name.
- **Read & reply:** read what came in, in one inbox, and answer from there.
- **Keep:** every profile's posts as JSON files in `dataset/`; `delete`
  keeps a copy of what it removes.
- **Connect:** link the platforms with each other and with the services
  around them (webhooks, ntfy, NATS, e-mail: phase 5 of the plan).

| Platform | Package | Post | Read | Reply | Delete |
| -------- | ------- | :--: | :--: | :---: | :----: |
| Bluesky | `amoorion-bluesky` | ✓ | ✓ | ✓ | ✓ |
| Mastodon | `amoorion-mastodon` | ✓ | ✓ | ✓ | ✓ |
| X (twitter) | `amoorion-x` | ✓ | ✓ | ✓ | ✓ |
| Tumblr | `amoorion-tumblr` | ✓ | ✓ | | ✓ |
| Blogger (by mail) | `amoorion-blogger` | ✓ | | | |
| Facebook Page | `amoorion-facebook` | ✓ | ✓ | ✓ (comment) | ✓ |
| Discord bot / webhook | `amoorion-discord` | ✓ | ✓ (bot) | ✓ (bot) | ✓ |
| Telegram bot | `amoorion-telegram` | ✓ | ✓ | ✓ | ✓ |
| Matrix room | `amoorion-matrix` | ✓ | ✓ | ✓ | ✓ (redact) |

**Early stage:** every platform is tested against fakes of its API; trying
them against real accounts is under way.

## How it is built

One core (model, view, controller) and namespaces on it: **plugins** (one
per platform), **methods** (what amoorion can do), and the faces that expose
the methods: **CLI**, **HTTP API**, **MCP** server for AI agents, and a
**daemon** for long-running services. Secrets come only from a **vault**
(Bitwarden / Vaultwarden, HashiCorp Vault / OpenBao, or a KeePassXC file);
`.env` holds just the link to it. Each platform is its own package in
`packages/` (a uv workspace). Details: [docs/structure.md](docs/structure.md), writing a plugin:
[docs/plugins.md](docs/plugins.md).

## Usage

```sh
uv sync
cp example.env .env                          # the link to the vault

uv run amoorion                              # asks step by step what to do (or: amoorion -i)
uv run amoorion plugins                      # platforms and what they can do
uv run amoorion accounts                     # which have their secrets in the vault
uv run amoorion publish --text "hello" --to dryrun bluesky
uv run amoorion --json read --platform bluesky
uv run amoorion reply --platform bluesky --to "at://…" --text "thanks"
uv run amoorion inbox                        # everything read or received so far
uv run amoorion snapshot --platform bluesky  # its posts into dataset/bluesky/<profile>/ (JSON, indexed)
uv run amoorion delete --platform bluesky --id "at://…"   # keeps a copy in the dataset first
uv run task help                             # help of every command

uv run amoorion api                          # HTTP API on 127.0.0.1:8000
uv run amoorion mcp                          # MCP server (stdio) for agents
uv run amoorion daemon                       # long-running services
```

The API needs the secret `api/token` in the vault (sent as `Authorization:
Bearer`), and every hook its own secret; without them they refuse calls.
Where each backend keeps a secret: [docs/structure.md](docs/structure.md#vault).
Each platform's secrets are listed in its package's README, e.g.
[packages/amoorion-bluesky](packages/amoorion-bluesky/README.md).

Run locally first; a Dockerfile and compose come next (phase 6 of the plan).

## Development

```sh
uv run task init               # tools, git hooks, .env, then check
uv run task vault:tools        # the Bitwarden CLI, by npm into tools/
uv run task vault:login        # log in and unlock; the session goes into .env
uv run task vault:status       # bw's state, and which platforms have their secrets
uv run task check              # tests, YAML, commit messages, docs (= CI)
uv run task docs:build         # the docs site into docs/_build/html
uv run task plugin:new -- <platform> <Class> "<description>"   # a new platform
uv run task test:connect       # read-only: log in to every platform with its secrets, read a few posts
uv run task test:live          # a real test post on each (or: -- bluesky mastodon), read, replied, deleted
```

Examples of usage: Jupyter notebooks in [examples/](examples/)
(`uv run task examples:build` makes marimo notebooks and pages of them). The docs
(this README, the guides, the plan and an API reference generated from the
code) are built by Sphinx from [docs/](docs/) for Read the Docs.
Plan and open questions: [docs/devlog/](docs/devlog/). Guide for agents and
contributors: [AGENTS.md](AGENTS.md).

## Reference

- https://pl.wikipedia.org/wiki/(1221)_Amor
- https://github.com/sarverott/amoorion/
- https://amoorion.readthedocs.io
- https://pypi.org/project/amoorion/
- https://sarverott.github.io/amoorion
- https://sarverott.tumblr.com/post/831595954743459840/github-sarverottamoorion-universal-tool-for
- https://x.com/sarverott/status/2114859609823301649

## License

Free, under the MIT License, © 2024–present Sett Sarverott:
[LICENSE](LICENSE), https://sett.mit-license.org
