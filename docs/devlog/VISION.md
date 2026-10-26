# VISION

One tool for administering presence on chatting, communication and
publication platforms: write once, post everywhere, read and answer from one
place, and connect it all with the services around it. Free (MIT); its first
area of use is the RedScope zone, but it is not tied to it.

- **Publication:** post to X (twitter), Bluesky, Mastodon, Tumblr, Blogger
  (by mail), Facebook.
- **Communication:** Discord, Telegram, Matrix.
- **Linking:** e-mail client, webhooks (GitLab, GitHub, Discord…), ntfy
  notifications, NATS.

Left out for now (struck through in the README): WhatsApp, Signal, RSS feed
receiver, phone management by adb.

## Principles (from the decisions of phase 0)

- **One core, many faces.** `core.py` (model, view, controller) under every
  namespace; each operation is a *method*, reachable from the CLI, the HTTP
  API, MCP (AI agents) and the daemon alike. Shape: [../structure.md](../structure.md).
- **One plugin per platform**, each its own package of the uv workspace,
  declaring what it can do (post, read, reply).
- **Secrets only from a vault.** `.env` holds the link to it, nothing more.
- **Local first**, then a container, then compose, then ready for a zone.

## Plan of work

Each phase ends with `task check` green, docs true, and a changelog entry.
The checklist of the current phase is in [TODO.md](TODO.md).

### Phase 0: skeleton and core (done)

BOS anatomy, tooling, decisions Q1–Q5; core and all namespaces with a
`dryrun` platform, the `generic` hook, the env vault backend, CLI, API, MCP
and daemon working end to end.

### Phase 1: real vault and plugin loading

Depends on Q6, Q7.

1. First real vault backend (Q6), with a test double of its API.
2. Plugin loading from outside packages if decided (Q7).
3. `accounts` method: which platforms have their secrets in place, without
   showing them.
4. Configuration of defaults (which platforms `publish` goes to when `--to`
   is left out).

### Phase 2: publication platforms (done, against fakes)

One plugin package each (Q10), plus Mastodon (third orders), behind `post` (and `read` where the platform allows), with
tests against recorded or faked HTTP; never against real accounts in CI.

1. Bluesky (AT Protocol, app password)
2. X / twitter (API v2, OAuth)
3. Tumblr (API, OAuth)
4. Blogger (posting by mail: needs the e-mail sender of phase 5 or plain SMTP)
5. Facebook (Graph API, page token)

Per platform: limits (length, media) checked before sending; `Post` split or
shortened by a rule the author confirms.

### Phase 3: communication platforms (done, against fakes)

1. Discord: post and read through a bot, or post through a channel
   webhook (Q12); as a daemon service listening to channels.
2. Telegram: bot API, same shape.
3. Matrix: client-server API, same shape.

Messages coming in are kept in the inbox (Q11); rules acting on them
(forward, notify) come in phase 5, once ntfy and NATS exist as targets.

### Phase 4: documentation, examples, releases

From the author's first inquiry: make what is done here clear to users,
and release it.

1. **Docs on Read the Docs**, built by Sphinx from the Markdown in `docs/`
   (MyST): the README, structure, plugins guide, plan and changelog as
   pages, and an API reference generated from the code, so pages can link
   to classes and functions. `task docs:build` builds it with warnings as
   errors, and `task check` runs it, so the docs stay true.
   `docs/requirements.txt` for Read the Docs is exported from `uv.lock`.
2. **Examples** in `examples/` as Jupyter notebooks: first steps with
   `dryrun`, the vault and accounts, the inbox and hooks over the API,
   writing a plugin. They run in the tests (they post nowhere) and are
   shown in the docs.
3. **marimo builds** of the examples: `task examples:build` converts each
   notebook to marimo and exports it as a page into `examples/build/`,
   ignored by `examples/.gitignore`.
4. **Releases:** a push to `master` (a merged pull request too) bumps the
   version by commitizen from the conventional commits, tags it, writes
   `CHANGELOG.md` and creates a GitHub release. A created release builds
   every package, attaches them to the release (the git package) and
   publishes them to PyPI.

### Phase 5: linking

1. Webhooks: GitHub (`X-Hub-Signature-256`), GitLab (`X-Gitlab-Token`),
   Discord; each a hook in `hooks/`.
2. ntfy: plugin (post) and notification target.
3. NATS: publish methods' results, subscribe as a daemon service.
4. E-mail client: send (also Blogger by mail) and read.

### Phase 6: deployment

In the order of Q4:

1. Local: `uv run amoorion …`, `task` procedures for each server.
2. `Dockerfile`: one image, the daemon as its default command.
3. `compose.yaml`: the daemon with its vault link from `.env`.
4. Ready for a zone: health endpoint, logs to stdout, reverse proxy notes,
   no zone-specific settings in the code.
