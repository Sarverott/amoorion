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
- [ ] Default platforms for `publish` (Q9)

## Phase 2: publication platforms

- [x] Bluesky: post (links and tags as facets), read, reply; tested
      against a fake PDS, **not yet against a real account**
- [ ] X (twitter)
- [ ] Tumblr
- [ ] Blogger by mail
- [ ] Facebook

Phases 3–5 (communication, linking, deployment): see [VISION.md](VISION.md).
