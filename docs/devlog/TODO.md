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

- [ ] First real vault backend (Q6)
- [ ] Plugin loading from outside packages (Q7)
- [x] `dotenv` → `python-dotenv` (Q8)
- [x] `accounts` method: which platforms have their secrets in place
- [ ] Default platforms for `publish`

Phases 2–5 (platforms, linking, deployment): see [VISION.md](VISION.md).
