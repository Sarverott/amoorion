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

- [x] Vault backends, one module each (Q6): Bitwarden / Vaultwarden (`bw`),
      HashiCorp Vault / OpenBao (KV v2), KeePassXC file, `.env` setup
- [x] Plugins through entry points, also from separate packages (Q7);
      guide in `docs/plugins.md`
- [x] `dotenv` → `python-dotenv` (Q8)
- [x] `accounts` method: which platforms have their secrets in place
- [x] Default platforms for `publish`: none, `--to` stays required (Q9)

## Phase 2: publication platforms

- [x] uv workspace, one package per platform (Q10); `task plugin:new`
- [x] Bluesky: post (links and tags as facets), read, reply
- [x] Mastodon: post, read, reply, the server's own character limit
- [x] X (twitter): API v2, OAuth 1.0a, weighted 280 characters
- [x] Tumblr: post (Neue Post Format, tags), read
- [x] Blogger by mail: post, TLS only
- [x] Facebook Page: post, read, replies as comments
- [x] The vault reached by `bw` from `tools/` (npm); a task initializes
      its session into `.env` (Q13)
- [x] `dataset/` (gitignored): every profile's posts read into JSON files
      with an index, `dataset/<platform>/<profile>/` (Q14)
- [x] `delete` capability and method, storing what it deletes in the
      dataset first (Q14)
- [x] One command for the live tests of all platforms (Q13)
- [ ] Every platform tried against a real account (needs the author's
      accounts and go-ahead, Q13; ready: `task test:live -- <platform>…`)

## Phase 3: communication platforms

- [x] Inbox of received messages, SQLite; `read` and hooks fill it (Q11)
- [x] Discord: a bot (post, read, reply) and a channel webhook (post), Q12
- [x] Telegram: a bot in one chat (Bot API)
- [x] Matrix: one room (client-server API)
- [x] A live test for every platform, run only when named (`task test:live`)
- [ ] Listening live (Discord gateway, Telegram updates, Matrix sync) as
      daemon services filling the inbox

## Phase 4: documentation, examples, releases

- [x] Sphinx docs from the Markdown in `docs/` (MyST), API reference from
      the code; Read the Docs config; `task docs:build` in `task check`
- [x] Jupyter notebooks in `examples/`, run by the tests, shown in the docs
- [x] marimo builds of the examples (`task examples:build`, gitignored)
- [x] Release on push to `master`: commitizen bump of every package, tag, GitHub release
- [x] On a release: packages attached to it and published to PyPI
      (PyPI by the `PYPI_TOKEN` of the `pypi` environment)
- [x] The loop: pulling master marks the next pre-release (lefthook),
      a push to development makes it final and opens the pull request to
      master, its merge tags and releases; `__version__` from the package
- [x] Development tools (`amoorion-dev`, rich): state of development, the
      versions, release notes, phases; the state as a page of the docs'
      development section, which holds the devlog
- [x] Release notes: the commits (CHANGELOG.md) and the story of
      `docs/changelog/` since the last release
- [x] A completed phase releases by itself (the flow merges its pull
      request), switchable in `.github/flow.toml`
- [x] Publishing split: every package by a local action, one job each;
      every workflow can also be started by hand
- [x] Project web page built at every release, with the examples built
      by marimo, kept in the `github-pages` branch and served by GitHub
      Pages
- [x] An easy CLI: `amoorion` alone asks what to do, step by step (rich)
- [x] A map and a working guide for agents in `docs/.agents/`
- [x] A contributors guide in the docs' Development section: pulling the
      current state, pushing changes, versioning, what the loop does with them
- [x] Versions per package (Q15): only changed packages bumped, `amoorion`
      always; every push a `Z` release merged by itself, a phase `Y`, all
      phases `X`; a `Z` release publishes only the bumped packages
- [x] After all workflows of a release: master merged back into development
- [x] The web page: `amoorion-website` built, with the marimo examples and
      manifest files, in the `github-pages` branch (served from it)
- [x] The docs styled after the web page and `resources/`; the README
      presenting the project
- [x] `llms.txt` (sphinx-llm), Markdown for agents, agent skills,
      `robots.txt`, a 404 page

## Phase 5: linking

- [x] `check` no longer runs on pull requests to master: the flow's own
      pull request waited for an approval nobody gives, and the flow checks
      before merging
- [x] Webhooks: GitHub (`X-Hub-Signature-256`), GitLab (`X-Gitlab-Token`),
      Discord; each a hook in `hooks/`
- [x] ntfy: plugin (post) and notification target
- [x] NATS: publish methods' results, subscribe as a daemon service
- [x] E-mail client: send (also Blogger by mail) and read
- [x] The notebooks of `examples/` renamed `old.<NAME>.ipynb`
- [x] `Amoorion` and `Plugins`, the author's way of using amoorion from Python:
      `use`, `load`, `save`, flags, changes detected by hashes
- [ ] Workflows and rules acting on what arrives; searching the inbox
- [ ] `compose` through any OpenAI-compatible server (Ollama, LiteLLM,
      llama.cpp, OpenAI, Claude, Hugging Face); a society simulated locally
- [ ] Hooks for Sentry and Plane; small utilities (Wikipedia, ngrok, markdown posts)
- [ ] The nineteen notebooks and five advanced use cases filled and run by the
      tests; Gradio and Streamlit apps for Hugging Face Spaces
- [ ] Every link of the author's inquiry considered, the verdicts in the docs
- [ ] New examples from the author's list, with what they present implemented

Phase 6 (deployment): see [VISION.md](VISION.md).
