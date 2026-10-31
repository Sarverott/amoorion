# Agent notes

Newest on top.

## 2026-10-31: the author's reading of the examples

- The author's `CALL()>"read"-"platform">"nowhere"[output]` can't work: Python applies `-` and `[]`
  to the strings first. Hence `/`, `-`, `+`, `>>`; `>>` binds last, so nothing needs parentheses.
- Their drafts' `except Exception():` would raise a TypeError when something fails; the examples
  don't use it, as `@step` catches failures itself.
- No general method running any command: methods reach MCP and the API. One method per program.
  `bw_cli` stays below the methods, which need the vault. GitPython still starts the `git` program.
- The menus were driven in a pseudo-terminal once, and by a pipe in the tests; never by a person.
- `resources/scopes/*.sheme.*` are still empty, unread: their purpose was assumed to be input and
  output schemas of workflows, nothing built on that. Example 20 has no per-platform graphics or video,
  no identity labels, no `HOOKS.listen`; it reacts to a message put in the inbox by hand.
- `docs/_build` can hold a stale docstring: delete it if the LaTeX check names what the source no longer has.

## 2026-10-30: `Amoorion()` is a sandbox

- The author's note in `app/base.py`: no args = default config. Taken as a sandbox that ignores
  `.env` and AMOORION_VAULT/INBOX/DATASET, so a script calling `Amoorion()` can't reach real
  accounts; the real setup is `Amoorion(".env")`. CLI, API and MCP started by command are unchanged.
- Examples that also use `Inbox()`, `Dataset()`, the CLI or `Plugins` flags keep their block: those
  still read the process's environment.
- The schemas are `.sql` files beside their code (the author's move); checked in the built wheel.

## 2026-10-30: cut into short files

- Moves only, checked by the same tests. No real platform was tried, as before.
- The directory `site/` is ignored by git (the built page), so the package is `amoorion_dev.webpage`.
  `tests/test_tracked.py` caught it.
- A method is registered by its import in `methods/__init__.py`: a new `<name>_method.py` without
  that import silently doesn't exist.
- Left long on purpose, one purpose each: `cli/guide.py`, the plugin classes, `tests/`.

## 2026-10-30: the author's examples

- `compose` has only met fake servers: Ollama is installed here but holds no model and
  none was pulled. Claude's and others' OpenAI-compatible endpoints are from memory, untried.
- `sentry` and `plane` follow their webhook docs as read today; no real delivery seen.
  Plane's docs contradict themselves on some `event` values, so the header is preferred.
- A rule publishing to where it reads can match its own post again; documented, not prevented.
- An env file given to `Amoorion` doesn't carry AMOORION_NOTIFY or AMOORION_NATS, nor `env`
  vault secrets: those stay process-wide.
- `task examples:build` isn't in `task check`, but the release's page needs it: run it
  before pushing notebook changes, a failing cell would break the page job.

## 2026-10-30: the lesson of the missing dataset package

- **What happened:** `dataset/` in `.gitignore` also hid `src/amoorion/dataset/`.
  Every test passed here, on files git had never seen; on GitHub all checks
  failed, and PR #11 merged that into master. Commits 5b09217..2605b27 lack
  the package.
- **Decided with the author:** the broken commits stay in history; from now
  on whatever is broken or lacking gets fixed first.
- **The lesson:** a green check here proves the working directory, not the
  repository. What counts is what a clean clone has, so CI's result counts,
  not only mine. `tests/test_tracked.py` now fails on any ignored source file.
- **It happened again the same day I wrote this:** I chained `task check ;
  git commit`, and 090031f went in over a failing gate. Fixed in fd23ad4,
  never pushed alone. Chain with `&&`.
- **A second find on the way:** `VaultLink.from_env` puts the real `.env`
  into `os.environ`, so tests could inherit the vault link and its master
  password. `conftest.py` now blocks that for non-live tests.

## 2026-10-27: orders Q13–Q15, the third inquiry, a release per push

- Read Q13's "initializing our credentials been placed in .env - place them
  there" as: the vault's access (the bw session) goes into `.env`, the
  platforms' secrets stay in the vault (rule 3). If the author meant the
  platforms' secrets in `.env` (the `env` backend), that is one line of
  `.env` away, but against AGENTS.md rule 3; to confirm.
- `X` = when phase `release.major_after_phase` (6, the last of VISION.md)
  and all before it are complete; TODO.md lists phases only up to 4, so it
  can't happen early.
- On `Y` all packages get `amoorion`'s version, so diverged patch versions
  meet again at every phase.
- Untried: the merge back after a failed publish or page (it runs on
  `!cancelled()`), a release while another is still publishing (the
  `release` concurrency group queues it), `task vault:login` against the
  real Bitwarden server (tried against a fake `bw`), every plugin's
  `delete` against a real platform.
- `git pull --rebase` leaves release tags behind; the local tools then
  count from an old release. Documented pulls use `--tags`.
- Tests wrote `read`'s messages into the user's real inbox (no isolation);
  a root `conftest.py` now points the inbox and the dataset at `tmp_path`
  for every test but the live ones.
- The `publish` and `gh-pages` badges of the README show the last run of
  those workflows started on their own (v0.3.1, failed); called from
  `release` now, their runs count as `release`'s. Left as the author made
  them.
- The website repository's issues are in `~/__WORKSHOP/forge/NOTES-for-repositories.md`.

## 2026-10-27: after v0.3.0, a contributors guide

- v0.3.0 was released by merging PR #3. The tag, the GitHub release and
  the notes worked. `publish`: amoorion, -blogger, -bluesky and -discord
  went up at once; the six new projects were still queued about 35 minutes
  later, presumably waiting out the 429 limit (logs of running jobs are
  not readable from here).
- `gh-pages` failed at `configure-pages`: Pages is not enabled. That step
  came before the branch step, so the page was kept nowhere. It is now
  after it (dcc5db5). The `github-pages` branch on origin points at the
  merge commit 9df8d0a; I didn't make that, and I left it.
- development held 0.3.0 after the pull of master: the post-merge mark
  hadn't run (the hooks are installed; I don't know how the pull was
  made). I ran `amoorion-dev version mark` by hand: 0.3.1a0.
- The author's empty Taskfiles in `examples/`, `scripts/`, `tests/` and
  `tools/` (includes commented out) were committed as they are; I read them
  as a split in progress and left it for them to say.
- `docs/contributing.md` holds the commands of a session for people;
  GUIDE.md stays the strict version for agents and points to it.
- `CLEO.md` started, at the author's invitation, after rs-tech-infra's.

## 2026-10-27: tools, phase releases, split publishing, web page, guided CLI

- The author's inquiry ("github pages should contain builded examples")
  landed in INQUIRIES.md while working and went into the plan commit
  d369985 through `git add -A`; carried out with the web page.
- `scripts/version.py` → `amoorion-dev version`; its tests moved to
  `tools/amoorion-dev/tests/`. `amoorion-dev` is a workspace member, in
  the dev group and the docs' dependencies, never in `packages`.
- Phase release rule: complete now and not complete at the last release
  tag. Phase 4 was complete at v0.2.1 (6/6), reopened with 7 items and
  closed again, so it does not auto-release; the author decides PR #3.
- `gh-pages.yml` deploys with actions/deploy-pages; Pages is not enabled
  on the repository yet (API 404), so it fails until the author enables
  it (Source: GitHub Actions).
- Workflows untried on GitHub: the split publish, the phase merge, the
  release notes in a real release, gh-pages. Tried locally: notes for
  v0.2.1, the site with examples, all amoorion-dev commands.
- PyPI after v0.2.1: 4 projects with wheels only; the rest comes with the
  next publish (waiting out the 429 limit).
- Killing a hung process with `pkill -f <pattern>` ended my own shell
  twice (the pattern was in its command line): look the PID up first.

## 2026-10-27: release loop after the first release

- The author merged development into master (PR #1): `release` bumped to
  0.2.0, tagged, made the GitHub release, `publish` attached the packages;
  PyPI failed with `invalid-publisher` (no trusted publisher). Now the
  `PYPI_TOKEN` secret of the `pypi` environment; v0.2.0 is not on PyPI.
- Docs vs package versions differed: `__version__` was hard-coded "0.1.0".
  Now `importlib.metadata.version("amoorion")`.
- Read gitrecon (`forge/redscope-technologies/gitrecon`: `.github/bos/flow.py`,
  `bos.config.json`): every loop step dispatches the next with `gh workflow
  run`, PRs skipped when they'd carry only merges and `bump:` commits. Taken
  over: those two ideas; not the full revision/testing/releasing chain.
- commitizen counts the next version from the tag of the *current*
  version; a pre-release has none, so it counted every commit ever (any fix
  → 0.3.0). `scripts/version.py` counts from the last release tag itself and
  uses cz only to write the files (`bump <version> --files-only`) and render
  the section (`changelog --dry-run --start-rev v<last>`).
  `update_changelog_on_bump` is gone: it wrote sections for pre-releases.
- The unmarking happens in the flow workflow, not in a pre-push hook: a
  commit made in pre-push is not part of that push.
- v0.2.1 publish: PyPI answered `429 Too many new projects created` after
  four new projects (amoorion, -blogger, -bluesky, -discord; wheels only).
  The pypi job now uploads per package with `uv publish --check-url`
  (skips what is there) and waits 15 min on a 429, up to 12 times.
- Repository setting `can_approve_pull_request_reviews` is false: the flow
  workflow can't open the PR until the author allows it.

## 2026-10-26: the first inquiry (docs, examples, releases)

- The author's docs member asked for Python >=3.13; the workspace is pinned
  to 3.12, so `uv lock` failed. Now >=3.12; Read the Docs builds on 3.13.
  `.readthedocs.yaml` reindented for yamllint; its `docs/requirements.txt`
  is exported from uv.lock (`task docs:requirements`), with `-e ./…` lines
  that pip resolves from the checkout root, as Read the Docs runs it.
- The first docs build hung: autosummary imports every module, and
  `amoorion/api/__main__.py` started the server on import. All `__main__`
  modules are guarded now.
- docs/conf.py rewrites relative links that leave docs/ (README → LICENSE,
  packages/…) to GitHub at `READTHEDOCS_GIT_IDENTIFIER` (else `master`);
  notebooks are copied from examples/ into docs/examples/ at build time.
- Notebooks were written by a throwaway generator and saved with outputs;
  `tests/test_examples.py` runs them. marimo (group `examples`) converts
  and exports them in `task examples:build`; cell order held, since marimo
  keeps notebook order among independent cells.
- Release: `GITHUB_TOKEN` pushes and releases start no workflow, so
  `release.yml` starts `publish.yml` by `workflow_dispatch` (the one event
  that token may trigger). PyPI trusted publishing doesn't accept reusable
  workflows, which is why publish is its own top-level workflow. cz exits
  3 / 21 when nothing is to release; `--no-raise 3,21` (a global option,
  before `bump`). Lock-step versions through `version_files`, `uv lock` as
  pre-bump hook; tried in a throwaway clone (0.1.0 → 0.2.0, one commit).
- Not tried for real: the workflows on GitHub (no push to master was made)
  and the Read the Docs build.

## 2026-10-26: orders of phase 3 carried out

- Inbox (Q11): `amoorion.inbox`, SQLite at `AMOORION_INBOX` (default
  `$XDG_DATA_HOME/amoorion/inbox.sqlite3`); kept once by (platform, id),
  hook messages without an id get one. `read` keeps what it read and stays
  `read_only` (it changes nothing on platforms). A root `conftest.py`
  points every test's inbox into its tmp dir.
- `HttpPlugin.hidden()`: secrets that are part of URLs (Telegram's bot
  token, a Discord webhook's token) are replaced by `***` in errors, also
  in `requests` connection errors, which quote the URL.
- Discord (Q12): one package, two entry points, `discord` (bot, REST only,
  no gateway yet) and `discord-webhook`. `allowed_mentions: {parse: []}`
  always, so `@everyone` in a post pings nobody. Reading others' messages
  needs the Message Content intent.
- Telegram reads with `getUpdates` without an offset: nothing is confirmed,
  updates stay readable 24 h; it fails while a webhook is set, and never
  shows the bot's own messages (the live test skips reading there).
- Matrix: plain `m.text` events, own transaction ids; encrypted rooms not
  supported. Aliases `#…` resolved through the room directory.
- Live tests (the order "prepare tests for each platform"):
  `tests/live/test_live.py`, one per installed platform but dryrun,
  deselected by default (`-m "not live"` in addopts) and skipped unless
  named in `AMOORION_LIVE`; not run by the agent (needs Q13's go-ahead).
  `tests/test_live_harness.py` runs the same test on dryrun.

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
