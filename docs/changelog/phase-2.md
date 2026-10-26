# Phase 2: publication platforms

Append-only.

## UNIXUSAT=1792987994803 · commit e1a14d8

The author's third orders, word for word:

````markdown
## added initializer in taskfile
also your idea presented in plugins sounds great - add mastodon plugin


### Q10
as a uv workspaces

### Q9
no defaults for `--to`````

The questions they answer, with their decisions:

### Q9: default platforms for `publish`

`publish` needs `--to`. Where do the default platforms come from when it is
left out?

- an environment setting in `.env` (`AMOORION_PUBLISH_TO=bluesky,x`), though
  `.env` was meant only for the vault link (Q3)
- a config file (`amoorion.toml` in the working directory or
  `~/.config/amoorion/`)
- every plugin that can post and whose `accounts` status is ready (never
  `dryrun`)
- no defaults: `--to` stays required

*Lean:* a config file, `amoorion.toml`, which can later hold other
non-secret settings too (routing in phase 3).

**Decision:** no defaults: `--to` stays required.

### Q10: where platform plugins live

Q7 says a plugin *can* be a separate package. Should the platforms of
phases 2–4 be

- built in, `src/amoorion/plugins/<platform>/` (as `dryrun`, and as the
  Bluesky plugin is now), or
- one package each (`amoorion-bluesky`, …), in this repository as a uv
  workspace (`packages/<platform>/`) or in repositories of their own?

*Lean:* built in until the plugin interface settles; moving one out later is
cheap, since both use the same entry point.

**Decision:** one package each, as a uv workspace in this repository.

## UNIXUSAT=1792988670459 · commit 200c81f

The orders carried out. The author's `init` task runs its steps in order
and keeps an existing `.env`. `--to` stays required (Q9). The repository
is a uv workspace: every platform is its own package in `packages/` (Q10),
Bluesky moved there; new: Mastodon (ordered), X, Tumblr, Blogger by mail,
Facebook, all on a shared `HttpPlugin` (except Blogger, SMTP), all tested
against fakes of their APIs only. `task plugin:new` starts a package.
Plugins now load on first use: imported before `amoorion.plugins`, a
plugin package was loaded half-imported and went missing. Q11–Q13 opened.
