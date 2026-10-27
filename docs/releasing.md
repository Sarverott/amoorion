# Releasing

Every package of the workspace has the same version, and every loop
`master` → `development` → `master` is a release. The version tells where a
loop is:

| Version | Where | Meaning |
| ------- | ----- | ------- |
| `0.2.0` with the tag `v0.2.0` | `master` | released |
| `0.2.1a0` | `development` | the next release is being made (pre-release) |
| `0.3.0` without a tag | `development`, the open pull request | ready: what the commits since `v0.2.0` ask for |

The docs show the same version as the package: `amoorion.__version__` is
read from the installed package's metadata.

## The loop

1. **Pull master into development** (locally, on `development`):

   ```sh
   uv run task flow:pull
   ```

   It runs `git pull origin master`. lefthook's `post-merge` hook then sees
   a released version (`v0.2.0` is tagged) and marks the next pre-release,
   `0.2.1a0`, in its own commit `bump: version 0.2.0 → 0.2.1a0` (no
   changelog). A version that is not released yet is left as it is.
2. **Work on development** and push it to origin as usual.
3. **On every push to development**, the `flow` workflow
   (`.github/workflows/flow.yml`):
   - does nothing if development has only merges and `bump:` commits that
     master hasn't got (the pre-release mark alone is no release);
   - otherwise runs `amoorion-dev version final`: the version becomes the one
     the commits since the last release tag ask for (breaking or `feat` →
     minor while `0.x`, a phase of TODO.md completed since → at least
     minor, anything else → patch), all packages and `uv.lock`
     follow, and `CHANGELOG.md` gets its section; committed as
     `bump: version 0.2.1a0 → 0.3.0` and pushed back to development (pull
     it before you go on);
   - opens the pull request `development` → `master` titled
     `Release v0.3.0`, or retitles the open one; later pushes update it
     (the version follows what the new commits ask for);
   - **a completed phase releases by itself:** when the last item of a
     phase in TODO.md was ticked since the last release, the flow runs
     `task check` and merges the pull request itself
     (`release.automerge_completed_phase` in `.github/flow.toml`; set it
     to `false` to always merge by hand). A phase that was complete at the
     last release already doesn't count again.
4. **Merge the pull request** (or the flow did). The `release` workflow on
   `master` runs `task check` and tags `v0.3.0` as the bot. The GitHub
   release is titled `amoorion v0.3.0`, with `— phase 4 done: …` when it
   completes a phase. Its notes are **what changed** (the version's
   `CHANGELOG.md` section, the commits) and **the story** (what was
   appended to `docs/changelog/` since the last release: the author's
   orders word for word, the decisions, what was done). Then it starts:
   - `publish`: one job per package, each running the local action
     `.github/actions/publish-package`: build, attach to the release (the
     git package), upload to PyPI with the secret `PYPI_TOKEN` of the
     `pypi` environment;
   - `gh-pages`: the project's web page (`amoorion-dev site`: the README,
     the platforms, the releases, and the examples built by marimo), kept
     in the `github-pages` branch (committed by the bot onto the release's
     commit, force-pushed) and deployed to GitHub Pages.

   Nothing is committed on `master`, so it never moves ahead of
   development.
5. Back to 1.

Every workflow can also be started by hand (Actions → the workflow → Run
workflow): `publish` for a tag and optionally some packages, `gh-pages`
for a tag, `release`, `flow` and `check` on their branch. A release made
by hand on GitHub publishes and builds the page too. Files already on PyPI
are skipped, so starting `publish` again for a tag goes on where it
stopped. PyPI lets an account create only a few
new projects an hour (`429 Too many new projects created`): the first
release of new packages waits out that limit, 15 minutes at a time.

The full BOS flow goes through `revision`, `testing` and `releasing`
between development and master; this repository takes the short way,
development → master, for now.

## Set up once, by the author

- **`pypi` environment** with the secret `PYPI_TOKEN` (a PyPI API token
  that may create the projects `amoorion` and `amoorion-<platform>`);
  optionally required reviewers, so every upload waits for a click.
- **Settings → Actions → General → Workflow permissions:** "Allow GitHub
  Actions to create and approve pull requests", or `flow` can't open the
  pull request.
- **`master` protection**, if any, must let GitHub Actions push tags
  (and merge the release pull request, for phase releases).
- **GitHub Pages** (Settings → Pages → Source: GitHub Actions), for
  `gh-pages` to deploy; the `github-pages` environment comes with it.
- **Read the Docs** builds the docs from `.readthedocs.yaml`; after a
  change of `uv.lock`, `task docs:requirements` refreshes
  `docs/requirements.txt` (`task check` fails until it does).
