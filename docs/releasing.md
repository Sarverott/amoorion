# Releasing

Every push to development is a release (Q15): the flow makes the versions
final, opens the pull request to master and merges it, the release
workflow tags it, publishes it and builds the web page, then merges master
back into development. Every package has its own version:

| Release | When | `amoorion` | the other packages |
| ------- | ---- | ---------- | ------------------ |
| `Z`, patch | every step | bumped | bumped only if changed since the last release |
| `Y`, minor | a phase of TODO.md completed since the last release | bumped | all get `amoorion`'s new version |
| `X`, major | `release.major_after_phase` of `.github/flow.toml` completed: all phases done | bumped | all |

The tag (`v0.3.2`) is the version of `amoorion`. A `Z` release attaches
and publishes only the packages it bumped (fewer calls to PyPI); `X` and
`Y` releases all. The docs show the same version as the package:
`amoorion.__version__` is read from the installed package's metadata.

| Version of `amoorion` | Where | Meaning |
| --------------------- | ----- | ------- |
| `0.3.1` with the tag `v0.3.1` | `master`; development after the merge back | released |
| `0.3.2a0` | `development` | the next release is being made (pre-release) |
| `0.3.2` without a tag | `development`, for the moment the flow takes | final, being released |

## The loop

1. **Work on development** and push it to origin (`task check` first).
2. **On every push to development**, the `flow` workflow
   (`.github/workflows/flow.yml`):
   - does nothing if development has only merges and `bump:` commits that
     master hasn't got (the merge back and the pre-release mark are no
     release);
   - otherwise runs `amoorion-dev version final`: every package gets its
     version of the next release (the table above), `uv.lock` follows,
     and `CHANGELOG.md` gets its section, listing the bumped packages and
     the commits; committed as `bump: version 0.3.2a0 → 0.3.2` and pushed
     back to development;
   - opens the pull request `development` → `master` titled
     `Release v0.3.2`, or retitles the open one;
   - merges it after `task check`, as `release.automerge` in
     `.github/flow.toml` says: `always` (every push), `phase` (only when
     the last item of a phase was ticked since the last release; a phase
     complete at the last release already doesn't count again) or `never`
     (the author merges).
3. **The `release` workflow on `master`** runs `task check` and tags
   `v0.3.2` as the bot. The GitHub release is titled `amoorion v0.3.2`,
   with `— phase 4 done: …` when it completes a phase. Its notes are
   **what changed** (the version's `CHANGELOG.md` section) and **the
   story** (what was appended to `docs/changelog/` since the last release:
   the author's orders word for word, the decisions, what was done). Then
   it calls:
   - `publish`: one job for each package the release bumped
     (`amoorion-dev packages --released v0.3.2`), each running the local
     action `.github/actions/publish-package`: build, attach to the
     release (the git package), upload to PyPI with the secret
     `PYPI_TOKEN` of the `pypi` environment;
   - `gh-pages`: the project's web page (`amoorion-dev site`), kept in the
     `github-pages` branch (committed by the bot onto the release's
     commit, force-pushed), which GitHub Pages serves.
4. **When both have ended** (whatever they ended with), its last job
   merges master back into development on origin and marks the next
   pre-release, `0.3.3a0`. Nothing is committed on `master`, so it never
   moves ahead of development.
5. **Pull** (`git pull --rebase origin development`) and go on: back to 1.

A release merged by hand (with `release.automerge` at `phase` or `never`)
merges back the same way. `task flow:pull` does the merge back locally,
for when it didn't run.

Every workflow can also be started by hand (Actions → the workflow → Run
workflow): `publish` for a tag (empty: the packages it bumped, `all`, or
some by name), `gh-pages` for a tag, `release`, `flow` and `check` on
their branch. A release made by hand on GitHub publishes and builds the
page too. Files already on PyPI are skipped, so starting `publish` again
for a tag goes on where it stopped. PyPI lets an account create only a few
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
  (and merge the release pull request, and push development for the
  merge back).
- **GitHub Pages** (Settings → Pages → Source: Deploy from a branch,
  `github-pages`, `/`): set.
- **Read the Docs** builds the docs from `.readthedocs.yaml`; after a
  change of `uv.lock`, `task docs:requirements` refreshes
  `docs/requirements.txt` (`task check` fails until it does).
