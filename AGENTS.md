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
only the skeleton exists.

Read first:

1. [docs/devlog/VISION.md](docs/devlog/VISION.md): the idea
2. [docs/devlog/TODO.md](docs/devlog/TODO.md): what is being worked on now
3. [docs/devlog/BRAINSTORM.md](docs/devlog/BRAINSTORM.md): open questions `Q<n>`
4. [docs/changelog/](docs/changelog/): how it got here, answered orders and decisions

The author's answers come in [docs/devlog/ORDERS.md](docs/devlog/ORDERS.md)
(empty between batches).

## Tooling and checks

```sh
uv sync                  # tools from PyPI: task, commitizen, lefthook, yamllint, pytest
uv run task setup        # + lefthook git hooks
uv run task check        # tests, YAML, commits (= CI)
uv run task test         # pytest only
uv run amoorion          # run the CLI
```

- **Gate every commit** on `uv run task check`.
- **Commits:** conventional commits, checked by commitizen in the lefthook
  `commit-msg` hook and in `task check`. Commits up to `743498f` predate it.

## Layout

```
src/amoorion/          the package (CLI entry point: amoorion:main)
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
3. **No secrets in the repository.** Platform tokens and passwords come from
   the environment or `.BOS/setup/`, never from committed files.
4. **Ask first** before anything outward-facing: pushing, tagging a release,
   publishing a package, posting to any real platform account.
5. **Branches:** BOS flow `master` → `development` → `revision` → `testing`
   → `releasing` → `master` via PR. Work on `development`.
6. **Commits:** one per finished step, conventional message ending in the
   agent's `Co-Authored-By:` line. Pushing needs the author's go-ahead.

## `docs/.agents/` — agent notes

The author reads this directory **read-only**:

- `docs/.agents/NOTES.md`: findings, decisions taken with the user. Newest
  on top, dated.

## BOS context

- This repo: `__WORKSHOP/forge/sarverott/github-repos/amoorion` (scope `sarverott`).
- Glossary of BOS terms: `__WORKSHOP/forge/blacksmith-organization-system/bos-skillset/docs/glossary/`.
- Loose notes of the author go to `__WORKSHOP/craftbook/scrapnotes/`, not here.
