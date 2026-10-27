# Contributors guide

How to work on amoorion, from a fresh checkout to a release: getting the
current state, making changes, pushing them, and what happens to the
version on the way. It holds for people and AI agents alike; agents also
follow the stricter [working guide](agents.md).

## Once: a checkout

```sh
git clone https://github.com/Sarverott/amoorion.git
cd amoorion
git switch development
uv run task init        # tools (uv sync), lefthook hooks, .env from example.env, task check
```

You need [uv](https://docs.astral.sh/uv/); go-task, commitizen, lefthook
and the rest come with `uv sync`. `.env` only links to the vault
(`example.env` says how); secrets never go into the repository.

The lefthook hooks matter: `commit-msg` checks every commit message, and
`post-merge` keeps the version right after pulling master (below). If you
ever skip `task init`, run `uv run task setup`.

## Branches

| Branch | What |
| ------ | ---- |
| `master` | releases only; changed by merging the release pull request (the flow does), never by a push |
| `development` | where all work goes |
| `github-pages` | the built web page, written by the `gh-pages` workflow |

The BOS flow has `revision`, `testing` and `releasing` between development
and master; amoorion takes the short way, development → master, for now.
From a fork, open pull requests to `development`.

## Pull the current state

Every session starts the same way:

```sh
git switch development
git pull --rebase origin development   # others' work and the bot's version commits
uv run task flow:pull                  # only if master isn't merged back yet
uv run task state                      # where it stands (-- --online: also GitHub and PyPI)
git status                             # anything changed you didn't make is someone else's work
```

- **`git pull` of development** brings the work of others and the commits
  of the bot (mr. Cravley), which finalizes the version after every push
  (below).
- **The merge back:** after a release, the `release` workflow merges
  master into development on origin and marks the next pre-release
  (`bump: version 0.3.1 → 0.3.2a0`), so `git pull` brings it.
  **`task flow:pull`** does the same locally (`git pull origin master`,
  then the mark; lefthook's `post-merge` hook marks too, which changes
  nothing twice), for a release merged by hand.
- **`task state`** shows the branch, the version and its stage, the next
  release, the open pull request, the phases of
  [TODO.md](devlog/TODO.md), the open questions, and whether the author
  left anything in [ORDERS.md](devlog/ORDERS.md) or
  [INQUIRIES.md](devlog/INQUIRIES.md). The same is the
  [state page](devlog/STATE.md) of these docs, made at every build.

## Make a change

One finished step at a time, each its own commit:

1. Pick the next unchecked item of [TODO.md](devlog/TODO.md), or what the
   author asked. If it depends on an open question `Q<n>` of
   [BRAINSTORM.md](devlog/BRAINSTORM.md), ask, don't decide it in code.
2. Put it where it belongs: a new operation is a method
   (`src/amoorion/methods/`), a platform is a package
   (`uv run task plugin:new -- …`), development tooling goes into
   `tools/amoorion-dev`.
3. Test it, against fakes of the platforms' APIs, never real accounts.
4. Update the docs it touches: README, `docs/*.md`, `docs/.agents/MAP.md`.
5. `uv run task check`: tests, notebooks, YAML, commit messages, the docs
   build with warnings as errors. It must pass; CI runs the same.
6. Commit, ticking the TODO item in the commit that finishes it.

### Commit messages

[Conventional commits](https://www.conventionalcommits.org/), checked by
commitizen: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`,
`build`, `style`, `perf`, with a scope where it helps (`fix(x): …`).
`bump` is for version commits, made only by the loop. Agents end their
message with their `Co-Authored-By:` line.

The type no longer decides the version (Q15): what the step finished does.

## Push

```sh
uv run task check
git pull --rebase origin development   # if the bot pushed meanwhile, your push would be refused
git push origin development
```

**Every push to development is a release.** What follows, on GitHub:

1. `check` runs `task check` on the push.
2. `flow` makes the versions **final** (below), `uv.lock` follows,
   `CHANGELOG.md` gets the section, and the bot pushes
   `bump: version 0.3.2a0 → 0.3.2` back to development.
3. `flow` opens the pull request development → master,
   `Release v0.3.2`, runs `task check` and merges it
   (`release.automerge` in `.github/flow.toml`: `always`; `phase` merges
   only a completed phase, `never` leaves it to the author).
4. `release` tags master, makes the GitHub release, publishes the bumped
   packages and builds the web page; when all of that has ended, it
   merges master back into development and marks the next pre-release.
5. **Pull before the next step:**

   ```sh
   gh run watch "$(gh run list -w release -L 1 --json databaseId -q '.[0].databaseId')"
   git pull --rebase origin development
   ```

Watch it with `gh run list` or `uv run task state -- --online`.

## Versions

Every package has its own version (Q15). Don't edit them by hand; the loop
sets them.

| Release | When | `amoorion` | the other packages |
| ------- | ---- | ---------- | ------------------ |
| `Z`, patch: `0.3.1` → `0.3.2` | every step (every push) | bumped, changed or not | bumped only if changed since the last release |
| `Y`, minor: `0.3.2` → `0.4.0` | a phase of TODO.md completed | bumped | all to the same `0.4.0` |
| `X`, major: `0.9.3` → `1.0.0` | the last phase of the plan completed (`release.major_after_phase`) | bumped | all to `1.0.0` |

A package changed when a commit since the last release (not a merge, not a
bump) touched its directory. A `Z` release attaches and publishes only the
packages it bumped; `X` and `Y` releases all of them. The release's tag is
the version of `amoorion`.

| Stage | Example | Where | Made by |
| ----- | ------- | ----- | ------- |
| released | `0.3.1`, tag `v0.3.1` | master; development after the merge back | the `release` workflow |
| pre-release | `0.3.2a0` (only `amoorion`) | development, being made | the merge back, or `task flow:pull` |
| final | `0.3.2`, no tag | development, for a moment | the `flow` workflow |

```sh
uv run task version                   # every package: its version, and in the next release
uv run amoorion-dev version next      # amoorion's next version
uv run amoorion-dev phases            # the phases and what is ticked
```

`amoorion.__version__` and the docs read the version from the installed
package, so they always match it.

## Release

Merging the release pull request is the release; the flow does it after
every push (or the author, when `release.automerge` says so). `release`
tags master and makes the GitHub release with its notes, `publish` puts
the bumped packages on PyPI and the release, `gh-pages` builds the web
page, and master is merged back into development. Details, and what the
author sets up once on GitHub: [Releasing](releasing.md).

## Never

- push or commit to `master`, tag, release or publish by hand: the loop
  does it;
- post to a real platform account, or run `task test:live`, without the
  author's go-ahead;
- commit a token or password, or overwrite `.env`;
- rewrite a section of `docs/changelog/`: it is append-only;
- settle an open `Q<n>` in code.

## Where things go

| It is | It goes to |
| ----- | ---------- |
| an answer to an open question | the author writes it into `ORDERS.md` |
| a request in the author's own words | `INQUIRIES.md`, then the plan and the changelog |
| a plan | [VISION.md](devlog/VISION.md), [TODO.md](devlog/TODO.md) |
| a question for the author | [BRAINSTORM.md](devlog/BRAINSTORM.md) as `Q<n>` |
| what was done and why | `docs/changelog/phase-<n>.md`, a new section |
| how the code is shaped | [structure](structure.md), `docs/.agents/MAP.md` |
