# amoorion — agent & contributor guide

Universal tool for administration of chatting and communication platforms.
This file is for AI agents (Claude Code, Codex, Gemini CLI, Copilot, Cursor,
Aider…) and humans alike. Keep it current when something changes.

It complements the workshop-wide `__WORKSHOP/AGENTS.md` (BOS rules). Where
they differ, this file wins for this repository.

## What this is

One tool to post to publication platforms (X, Bluesky, Tumblr, Blogger,
Facebook), talk through communication platforms (Discord, Telegram, Matrix)
and link them with the rest (e-mail, webhooks, ntfy, NATS). **Early stage:**
the core works end to end; Bluesky is the first platform, tested only against a fake server.

Read first:

1. [docs/devlog/VISION.md](docs/devlog/VISION.md): the idea
2. [docs/devlog/TODO.md](docs/devlog/TODO.md): what is being worked on now
3. [docs/devlog/BRAINSTORM.md](docs/devlog/BRAINSTORM.md): open questions `Q<n>`
4. [docs/changelog/](docs/changelog/): how it got here, answered orders and decisions
5. [docs/structure.md](docs/structure.md): the shape of `src/amoorion/`
6. [docs/plugins.md](docs/plugins.md): how to write a platform plugin

The author's answers come in [docs/devlog/ORDERS.md](docs/devlog/ORDERS.md)
(empty between batches).

## Tooling and checks

```sh
uv sync                  # tools from PyPI: task, commitizen, lefthook, yamllint, pytest
uv run task setup        # + lefthook git hooks
uv run task check        # tests, YAML, commits (= CI)
uv run task test         # pytest only
uv run task help         # help of the CLI and every subcommand
uv run amoorion          # run the CLI
```

- **Gate every commit** on `uv run task check`.
- **Commits:** conventional commits, checked by commitizen in the lefthook
  `commit-msg` hook and in `task check`. Commits up to `743498f` predate it.

## Layout

```
src/amoorion/core.py   Model, View, Controller, Registry: the base of every namespace
src/amoorion/<ns>/     models, vault, plugins, methods, hooks, cli, api, mcp, daemon;
                       core mechanics in <ns>/base.py (see docs/structure.md)
example.env            the link to the vault; copy to .env
tests/                 pytest tests
docs/devlog/           VISION, TODO, BRAINSTORM, ORDERS
docs/changelog/        phase-<n>.md, append-only
docs/.agents/          agent notes (see below)
.github/               community files, workflows (check = task check)
```

## Rules for agents

1. **Follow the plan.** Work on the next unchecked item in TODO.md, or what
   the user asks. Tick it off when done and verified. **The changelog is
   append-only:** sections in `docs/changelog/` are never rewritten; each
   new one starts with `UNIXUSAT=<ms since epoch> · commit <hash>`. An
   answered batch of ORDERS.md and the answered `Q<n>` of BRAINSTORM.md
   (with its **Decision:**) move word for word into
   `docs/changelog/phase-<n>.md`, leaving ORDERS.md empty. Work that belongs
   to another repository is not done here: write it into
   `~/__WORKSHOP/forge/NOTES-for-repositories.md`.
2. **Don't settle open questions in code.** If a change depends on a `Q<n>`,
   ask, or pick the *Lean:* option only when told to.
3. **Secrets only from the vault.** `.env` holds only the link to it; never
   commit tokens or passwords.
4. **Everything is a method.** A new operation goes into `methods/`, not
   into one front-end; CLI, API and MCP pick it up (add new subcommands to
   `SUBCOMMANDS` in Taskfile.yml; a test checks it). Platforms are plugins,
   tested against fakes of their APIs, never real accounts.
5. **Ask first** before tagging a release, publishing a package or posting
   to any real platform account. Pushing `development` is allowed.
6. **Branches:** BOS flow `master` → `development` → `revision` → `testing`
   → `releasing` → `master` via PR. Work on `development`.
7. **Commits:** one per finished step, gated on `task check`, conventional
   message ending in the agent's `Co-Authored-By:` line. Push when reaching a
   point that needs the author's answer, then ask.

## `docs/.agents/` — agent notes

The author reads this directory **read-only**:

- `docs/.agents/NOTES.md`: findings, decisions taken with the user. Newest
  on top, dated.

## BOS context

- This repo: `__WORKSHOP/forge/sarverott/github-repos/amoorion` (scope `sarverott`).
- Glossary of BOS terms: `__WORKSHOP/forge/blacksmith-organization-system/bos-skillset/docs/glossary/`.
- Loose notes of the author go to `__WORKSHOP/craftbook/scrapnotes/`, not here.
