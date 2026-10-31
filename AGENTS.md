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
the core works end to end with platform plugins for Bluesky, Mastodon, X,
Tumblr, Blogger, Facebook, Discord, Telegram and Matrix, tested only against
fakes of their APIs, and an inbox of received messages.

Read first:

0. [docs/.agents/GUIDE.md](docs/.agents/GUIDE.md): how an iteration goes
   (begin, take in, work, finish, never), and
   [docs/.agents/MAP.md](docs/.agents/MAP.md): every place, the release
   loop, workflows and tools; `uv run task state` for where it stands now
1. [docs/devlog/VISION.md](docs/devlog/VISION.md): the idea
2. [docs/devlog/TODO.md](docs/devlog/TODO.md): what is being worked on now
3. [docs/devlog/BRAINSTORM.md](docs/devlog/BRAINSTORM.md): open questions `Q<n>`
4. [docs/changelog/](docs/changelog/): how it got here, answered orders and decisions
5. [docs/structure.md](docs/structure.md): the shape of `src/amoorion/`
6. [docs/plugins.md](docs/plugins.md): how to write a platform plugin
7. [docs/contributing.md](docs/contributing.md): pulling, pushing,
   versions, for people and agents

The author's answers come in [docs/devlog/ORDERS.md](docs/devlog/ORDERS.md),
the work they ask for in their own words in
[docs/devlog/INQUIRIES.md](docs/devlog/INQUIRIES.md) (both empty between
batches).

## Tooling and checks

```sh
uv run task init         # fresh checkout: tools, lefthook hooks, .env, check
uv run task setup        # tools (uv sync) and lefthook git hooks
uv run task check        # tests, YAML, commits, docs and marimo builds (= CI)
uv run task test         # pytest only
uv run task format       # the code in its open shape (amoorion-dev shape, then ruff)
uv run task flow:pull    # on development: pull master in, mark the next pre-release
uv run task version      # the version of every package (released together)
uv run task vault:new     # KeePassXC (the vault for now): makes the file of AMOORION_VAULT_PATH and an empty entry per platform
uv run task vault:status  # the vault's state and which platforms have their secrets
uv run task vault:tools   # Bitwarden: bw by npm into tools/; vault:login (the author, interactive) puts its session into .env
uv run task test:connect [-- <platform>…]   # read-only: log in, profile, read a few (every platform with secrets)
uv run task test:live [-- <platform>…]      # post, read, reply, delete for real (the author's go-ahead, Q13)
uv run task help         # help of the CLI and every subcommand
uv run task examples:refresh  # run the notebooks and save their outputs into them
uv run task examples:build   # marimo builds of examples/ into examples/build/ (gitignored)
uv run task docs:build   # docs into docs/_build/html (Sphinx, warnings are errors)
uv run task docs:requirements   # docs/requirements.txt for Read the Docs, after a uv.lock change
uv run task plugin:new -- <platform> <Class> "<description>"   # start a plugin package
uv run amoorion          # run the CLI
```

- **Gate every commit** on `uv run task check`.
- **Shape of the code:** one thing per line, a blank line between statements,
  room for comments. Don't fight it by hand: `task format` writes it, `task
  check` refuses anything else.
- **Commits:** conventional commits, checked by commitizen in the lefthook
  `commit-msg` hook and in `task check`. Commits up to `743498f` predate it.

## Layout

```
src/amoorion/core.py   Model, View, Controller, Registry: the base of every namespace
src/amoorion/<ns>/     models, vault, plugins, methods, inbox, hooks, cli, api, mcp, daemon, app;
                       core mechanics in <ns>/base.py (see docs/structure.md)
packages/amoorion-<p>/  one package per platform (uv workspace); its README lists its secrets
scripts/new-plugin.sh  starts such a package (task plugin:new)
example.env            the link to the vault; copy to .env
tests/                 pytest tests (also run every notebook of examples/)
examples/              Jupyter notebooks of usage (dryrun and fakes only); advanced-usecases/ (run.py each,
                       run by the tests), spaces/ (Gradio and Streamlit apps for Hugging Face)
docs/                  the docs site (Sphinx + MyST, conf.py, Taskfile.yml); API pages generated
docs/devlog/           VISION, TODO, BRAINSTORM, ORDERS, INQUIRIES
docs/changelog/        phase-<n>.md, append-only
docs/.agents/          agent notes (see below)
skills/                agent skills for using amoorion (SKILL.md), served by the docs
resources/             the author's graphics (logo, mockup), used by the docs and the web page
.github/               community files, workflows: check (= task check), flow, release, publish
tools/amoorion-dev/     development tools: state, versions, phases, release notes, web page (task state)
```

## Rules for agents

1. **Follow the plan.** Work on the next unchecked item in TODO.md, or what
   the user asks. Tick it off when done and verified. **The changelog is
   append-only:** sections in `docs/changelog/` are never rewritten; each
   new one starts with `UNIXUSAT=<ms since epoch> · commit <hash>`. An
   answered batch of ORDERS.md and the answered `Q<n>` of BRAINSTORM.md
   (with its **Decision:**) move word for word into
   `docs/changelog/phase-<n>.md`, leaving ORDERS.md empty. An inquiry of
   INQUIRIES.md is first drawn into a plan (VISION.md, TODO.md), then moves
   word for word into the changelog the same way, leaving INQUIRIES.md
   empty. Work that belongs
   to another repository is not done here: write it into
   `~/__WORKSHOP/forge/NOTES-for-repositories.md`.
2. **Don't settle open questions in code.** If a change depends on a `Q<n>`,
   ask, or pick the *Lean:* option only when told to.
3. **Secrets only from the vault.** `.env` holds only the link to it; never
   commit tokens or passwords.
4. **Everything is a method.** A new operation is a new
   `methods/<name>_method.py` imported in `methods/__init__.py`, not part of
   one front-end; CLI, API and MCP pick it up (add new subcommands to
   `SUBCOMMANDS` in Taskfile.yml; a test checks it). Platforms are plugin
   packages in `packages/`, tested against fakes of their APIs, never real
   accounts.
5. **Ask first** before tagging a release or publishing a package by
   hand, or posting to any real platform account. Pushing `development`
   is allowed and is a release (Q15): the flow finalizes the versions,
   opens the release pull request to `master` and merges it; the release
   publishes the bumped packages and merges master back
   ([docs/releasing.md](docs/releasing.md)). Agents never push `master`;
   after a push they wait for the release and pull before the next step.
6. **Branches:** BOS flow `master` → `development` → `revision` → `testing`
   → `releasing` → `master` via PR. Work on `development`.
7. **Commits:** one per finished step, gated on `task check`, conventional
   message ending in the agent's `Co-Authored-By:` line. Push when reaching a
   point that needs the author's answer, then ask.

## `docs/.agents/` — agent notes

The author reads this directory **read-only**:

- `docs/.agents/GUIDE.md`: the working guide, strict steps of an iteration.
- `docs/.agents/MAP.md`: the map; updated with every structural change.
- `docs/.agents/NOTES.md`: findings, decisions taken with the user. Newest
  on top, dated.
- `docs/.agents/CLEO.md`: Cleo's own view of the project:
  conclusions and wishes; newest sections at the end.

Both GUIDE and MAP are also pages of the docs (Development → For agents).

## BOS context

- This repo: `__WORKSHOP/forge/sarverott/github-repos/amoorion` (scope `sarverott`).
- Glossary of BOS terms: `__WORKSHOP/forge/blacksmith-organization-system/bos-skillset/docs/glossary/`.
- Loose notes of the author go to `__WORKSHOP/craftbook/scrapnotes/`, not here.
