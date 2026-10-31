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

From the author's answers to Q13 and Q14:

6. **Real accounts:** the platforms' secrets in the Bitwarden vault, `bw`
   from `tools/` (npm), its session initialized into `.env` by a task;
   one command for the live tests of all platforms; the real APIs tried.
7. **The dataset:** `dataset/` (gitignored) keeps the read state of all
   posts of every profile on every platform as JSON files with an index,
   `dataset/<platform>/<profile>/`.
8. **Deleting:** a `delete` capability and method, which stores what it
   deletes in the dataset first.

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
5. **Development tools** (from the author's order of 2026-10-27):
   `amoorion-dev`, a rich CLI over the state of development (branch,
   version, the open pull request, last release, phases, open questions,
   pending orders), the versions of the release loop, release notes made
   of the commits and the story in `docs/changelog/`, and the project web
   page. The state is a page of the docs' development section.
6. **Phases release themselves:** when the last item of a phase is
   ticked, the flow merges the release pull request after the checks.
7. **The web page** of the project, built at every release into the
   `github-pages` branch and served by GitHub Pages.
8. **An easy CLI** for people: `amoorion` without arguments asks for the
   method and its parameters.
9. **Versions per package** (Q15): a package is bumped only when it
   changed, `amoorion` at every release; every step is a `Z` release,
   merged by itself; a completed phase is `Y` for all packages, `X` comes
   when phases 0–6 are done. A `Z` release publishes only what was bumped.
   After all workflows of a release, master goes back into development.
10. **The presentation page** (the author's inquiry): the web page from the
    source of `amoorion-website` (built), with the marimo examples and
    manifest files, in the `github-pages` branch; the Sphinx docs styled
    after it (the graphics of `resources/`), and a README that presents
    the project.
11. **For machines:** `llms.txt` (sphinx-llm), Markdown for agents, agent
    skills, `robots.txt` and a 404 page on Read the Docs.

### Phase 5: linking

1. Webhooks: GitHub (`X-Hub-Signature-256`), GitLab (`X-Gitlab-Token`),
   Discord; each a hook in `hooks/`.
2. ntfy: plugin (post) and notification target.
3. NATS: publish methods' results, subscribe as a daemon service.
4. E-mail client: send (also Blogger by mail) and read.
5. The author's examples: a Python object to use amoorion by (`Amoorion`,
   `Plugins`), and what the notebooks present made real. The projects the author
   linked are references, not orders: each is considered, adopted through what
   amoorion already speaks (HTTP, MCP, hooks) before adding a dependency.
6. The author's reading of the examples (their words: `docs/changelog/phase-5.md`):
   workflows written as Python (`@amo.workflow`, `@step`, `EXECUTE`) next to rules in
   YAML files, with logs and a JSON artifact out of each; `automate` gone, what it did
   now part of `workflow`; MCP tools and resources in the official style; a CLI of arrow
   menus; every outside program a method; examples that show data as tables and plots.

Moved on by the same reading: dataset backends (torrent, IPFS, FTP, S3, Hugging Face,
Google Drive, SSHFS, zip, git) and a vector database to phase 8; the model of holders,
submodels and flags, the graph of who follows whom, and methods for media programs
(ffmpeg, yt-download, GIMP, ADB, browsers, Blender, OBS) to phase 9; Scalar and
gRPC to phase 7, Cosmos SDK with phase 7's carrier of trust; the web app (mobile web app first,
browser extension second, Obsidian plugin last, a view injected by Playwright for the inbox) to phase 7; the society as a simulation of lives
(biblical names, born and dead, tarot, narrator, emotional drivers) to a phase of its own, once
the author gives their sets of names.

### Phase 6: deployment

In the order of Q4:

1. Local: `uv run amoorion …`, `task` procedures for each server.
2. `Dockerfile`: one image, the daemon as its default command.
3. `compose.yaml`: the daemon with its vault link from `.env`.
4. Ready for a zone: health endpoint, logs to stdout, reverse proxy notes,
   no zone-specific settings in the code.

### Phase 7: distribution and access

1. Container images on Docker Hub by a workflow; the image and the Python
   packages also as packages on GitHub.
2. Delegated access: TOTP, HOTP, OAuth, WebAuthn (`pywarp`), elliptic curves and
   segwit; `paramiko`, `pyotp`, QR codes. A carrier of trust probably needs
   setternet, whose integration is phase 9.
3. Phones as user simulations: pure Python ADB, `scrcpy`, remote ADB, a GSM
   gateway for SMS and calls; perhaps QPython brought back, a phone as a suite
   for agents.
4. Dependabot, and the other security, vulnerability and dependency matters on
   GitHub.
5. Releases announced on every platform amoorion supports, by its own plugins.

### Phase 8: Google, mirrors, self-sufficiency

1. Colab and Google's services: Calendar, Sheets, Docs, Slides, Forms, Drive,
   YouTube, Translate, Ads, Keep, Analytics, Contacts, Maps, AI Studio, Gemini,
   BigQuery.
2. Mirrors on GitLab, Bitbucket, Gitea and sr.ht, with their pipelines.
3. Issues handled by the development scripts with an agent in charge: hooks,
   listeners, self-sufficiency.

### Phase 9: integrations and the Almanah

1. Setternet and the other integrations (see phase 7).
2. An "Almanah" in `docs/.agents/`: problems, obstacles and accidents, past or
   anticipated, with their solutions, how to devise such solutions, the logic
   behind them, and how likely they are to happen again.
