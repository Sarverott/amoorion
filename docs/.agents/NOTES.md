# Agent notes

Newest on top.

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
