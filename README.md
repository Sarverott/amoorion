# amoorion
Universal tool for administration of chatting and communication platforms

---

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
uv run task check              # tests, YAML, commit messages, docs (= CI)
uv run task docs:build         # the docs site into docs/_build/html
uv run task plugin:new -- <platform> <Class> "<description>"   # a new platform
uv run task test:live -- bluesky mastodon    # one real test post on each platform named
```

Examples of usage: Jupyter notebooks in [examples/](examples/)
(`uv run task examples:build` makes marimo notebooks and pages of them). The docs
(this README, the guides, the plan and an API reference generated from the
code) are built by Sphinx from [docs/](docs/) for Read the Docs.
Plan and open questions: [docs/devlog/](docs/devlog/). Guide for agents and
contributors: [AGENTS.md](AGENTS.md).

## License

Free, under the MIT License, © 2024–present Sett Sarverott:
[LICENSE](LICENSE), https://sett.mit-license.org
