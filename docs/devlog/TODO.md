# TODO

What is being worked on now. Vision and the plan of all phases:
[VISION.md](VISION.md). Questions: [BRAINSTORM.md](BRAINSTORM.md). History:
[../changelog/](../changelog/).

## Phase 0: skeleton and core

- [x] BOS anatomy: AGENTS.md, CLAUDE.md, Taskfile.yml, src/, docs/, tests/, .github/
- [x] Tooling of the recent projects: uv, go-task, commitizen, lefthook,
      yamllint, pytest; CI `task check`
- [x] Settle the core questions (Q1–Q5)
- [x] `core.py`: model, view, controller, registry
- [x] Namespaces on the core: models, vault, plugins (+ dryrun), methods,
      hooks (+ generic), cli, api, mcp, daemon
- [x] `docs/structure.md`
- [x] README with all we know

## Phase 1: real vault and plugin loading

- [x] Vault backends, one module each (Q6): Bitwarden / Vaultwarden (`bw`),
      HashiCorp Vault / OpenBao (KV v2), KeePassXC file, `.env` setup
- [x] Plugins through entry points, also from separate packages (Q7);
      guide in `docs/plugins.md`
- [x] `dotenv` → `python-dotenv` (Q8)
- [x] `accounts` method: which platforms have their secrets in place
- [x] Default platforms for `publish`: none, `--to` stays required (Q9)

## Phase 2: publication platforms

- [x] uv workspace, one package per platform (Q10); `task plugin:new`
- [x] Bluesky: post (links and tags as facets), read, reply
- [x] Mastodon: post, read, reply, the server's own character limit
- [x] X (twitter): API v2, OAuth 1.0a, weighted 280 characters
- [x] Tumblr: post (Neue Post Format, tags), read
- [x] Blogger by mail: post, TLS only
- [x] Facebook Page: post, read, replies as comments
- [ ] Every platform tried against a real account (needs the author's
      accounts and go-ahead, Q13; ready: `task test:live -- <platform>…`)

## Phase 3: communication platforms

- [x] Inbox of received messages, SQLite; `read` and hooks fill it (Q11)
- [x] Discord: a bot (post, read, reply) and a channel webhook (post), Q12
- [x] Telegram: a bot in one chat (Bot API)
- [x] Matrix: one room (client-server API)
- [x] A live test for every platform, run only when named (`task test:live`)
- [ ] Listening live (Discord gateway, Telegram updates, Matrix sync) as
      daemon services filling the inbox

## Phase 4: documentation, examples, releases

- [x] Sphinx docs from the Markdown in `docs/` (MyST), API reference from
      the code; Read the Docs config; `task docs:build` in `task check`
- [x] Jupyter notebooks in `examples/`, run by the tests, shown in the docs
- [x] marimo builds of the examples (`task examples:build`, gitignored)
- [x] Release on push to `master`: commitizen bump of every package, tag, GitHub release
- [x] On a release: packages attached to it and published to PyPI
      (workflows ready; PyPI and GitHub set up by the author, Q15)

Phases 5–6 (linking, deployment): see [VISION.md](VISION.md).
