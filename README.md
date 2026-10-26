# amoorion
Universal tool for administration of chatting and communication platforms

---

## **EARLY STAGE OF PROJECT**

The core works end to end with a `dryrun` platform that sends nothing; no
real platform is connected yet. Plan: [docs/devlog/VISION.md](docs/devlog/VISION.md).

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
**daemon** for long-running services. Secrets come only from a **vault**;
`.env` holds just the link to it. Details: [docs/structure.md](docs/structure.md).

## Usage

```sh
uv sync
cp example.env .env                          # the link to the vault

uv run amoorion plugins                      # platforms and what they can do
uv run amoorion publish --text "hello" --to dryrun
uv run amoorion --json read --platform dryrun

uv run amoorion api                          # HTTP API on 127.0.0.1:8000
uv run amoorion mcp                          # MCP server (stdio) for agents
uv run amoorion daemon                       # long-running services
```

The API needs the secret `api/token` in the vault (sent as `Authorization:
Bearer`), and every hook its own secret; without them they refuse calls.
With the development `env` vault, secrets are environment variables:
`api/token` is `AMOORION_SECRET_API_TOKEN`.

Run locally first; a Dockerfile and compose come next (phase 5 of the plan).

## Development

```sh
uv sync && uv run task setup   # tools and git hooks
uv run task check              # tests, YAML, commit messages (= CI)
```

Plan and open questions: [docs/devlog/](docs/devlog/). Guide for agents and
contributors: [AGENTS.md](AGENTS.md).

## License

Free, under the MIT License, © 2024–present Sett Sarverott:
[LICENSE](LICENSE), https://sett.mit-license.org
