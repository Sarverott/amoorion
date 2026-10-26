# Agent notes

Newest on top.

## 2026-10-26: orders of phase 2 carried out

- The author's `init` task had `deps: [setup, check, init:env]`: deps run
  in parallel, and `cp example.env .env` would overwrite a filled-in `.env`.
  Now sequential cmds, and `init:env` has `status: test -f .env`.
- Bug found while writing X: `amoorion.plugins` loaded entry points on
  import; a plugin package imported first was loaded half-imported, failed
  silently into FAILED. Plugins now load on first use (`load_plugins()`),
  regression test in `tests/test_plugins.py`.
- Assumptions to check against the real APIs (Q13):
  - Facebook: token sent as `Authorization: Bearer` (never in URLs);
    default Graph version `v24.0`, overridable by `facebook/uri`.
  - X: reading timelines needs a paid access tier; posting works on free.
  - X weights and Bluesky graphemes are approximations; the servers decide.
  - Tumblr returns the new post's id as `id` or `id_string`; both handled.
- Blogger keeps its own SMTP secrets (`blogger/smtp-*`); the e-mail client
  of phase 4 may want shared `mail/*` keys later.
- pytest runs with `--import-mode=importlib` so packages' test modules may
  share names.

## 2026-10-26: orders of phase 1 carried out

- The author's `help` task called `task: run -- -h`, which Task reads as a
  task name; it now passes `CLI_ARGS`. Their `test` / `test:quiet` split kept.
- Vault backends are tested against fakes only: a fake `bw` script, a local
  server shaped like Vault's KV v2, and a real `.kdbx` made by pykeepass.
  `bw` flags used: `--nointeraction`, `status`, `list items --search`;
  not yet run against a real `bw` (it isn't installed here).
- Plugins and vault backends: only plugins use entry points (as ordered);
  vault backends stay a plain registry.
- Bluesky counts graphemes approximately (no `regex` dependency); the PDS
  is the final judge and its error message is passed on.
- `example.env` now starts from `bitwarden`; with no `.env` at all the
  backend is still `env`, so a fresh checkout exposes nothing.

## 2026-10-26: orders of phase 0 carried out

- Added the namespace `vault/` beside the author's directories: the vault
  link of Q3 needed a home of its own; say if it should live elsewhere.
- Q2's answer ends in "with": asked again as Q7. Built-in plugins register
  in `PLUGINS`; no entry-point loading until Q7 is answered.
- The `mcp` SDK is 2.x: `FastMCP` is now `mcp.server.mcpserver.MCPServer`.
  A tool returning a list gives one content block per item. Errors raised
  in a tool reach the agent only as `ToolError` (otherwise just "Error
  executing tool <name>"), so `mcp/base.py` converts `AmoorionError`.
- The API and hooks refuse calls while their secrets are missing from the
  vault, so a fresh install exposes nothing that posts.
- `dryrun` remembers posts per process only; the `read` CLI command in a new
  process shows nothing, by design.

## 2026-10-26: initialization

- BOS rules read from `__WORKSHOP/AGENTS.md` and `bos-skillset/skills/bos-workshop/SKILL.md`.
- Spelling of the development branch differs: workshop AGENTS.md says
  `development`, the BOS skill and glossary say `developement`; the recent
  projects use `development` locally. Used `development` here.
- Pattern taken from the recent projects: uv + `go-task-bin` + commitizen +
  lefthook + yamllint, Taskfile with `setup` / `check`, `docs/devlog/`
  (VISION, TODO, BRAINSTORM, ORDERS), append-only `docs/changelog/`.
- Commits before `743498f` (inclusive) predate commitizen.
- The author allowed pushing `development` (2026-10-26).
