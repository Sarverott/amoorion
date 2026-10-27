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
| `master` | releases only; changed by merging the release pull request, never by a push |
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
uv run task flow:pull                  # only after a release: master in, the next pre-release marked
uv run task state                      # where it stands (-- --online: also GitHub and PyPI)
git status                             # anything changed you didn't make is someone else's work
```

- **`git pull` of development** brings the work of others and the commits
  of the bot (mr. Cravley), which finalizes the version after every push
  (below).
- **`task flow:pull`**, after the release pull request was merged, brings
  master back into development: `git pull origin master`, then the
  released version becomes the next pre-release in its own commit
  (`bump: version 0.3.0 → 0.3.1a0`). lefthook's `post-merge` hook does the
  marking too; the task marks again in case hooks are off, which changes
  nothing twice. When nothing new was released, it only pulls.
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
commitizen. The type is not decoration: it decides the next version.

| Type | For | Next version (while `0.x`) |
| ---- | --- | -------------------------- |
| `feat` | something new a user can do | minor: `0.3.0` → `0.4.0` |
| `fix` | a bug fixed | patch: `0.3.0` → `0.3.1` |
| `docs`, `test`, `refactor`, `chore`, `ci`, `build`, `style`, `perf` | the rest | patch |
| `feat!:` or a `BREAKING CHANGE:` footer | something that stops working as before | minor (major from `1.0`) |
| `bump` | version commits; only the hook and the bot make them | none |

A phase of TODO.md completed since the last release raises at least the
minor too. Agents end their message with their `Co-Authored-By:` line.

## Push

```sh
uv run task check
git pull --rebase origin development   # if the bot pushed meanwhile, your push would be refused
git push origin development
```

Pushing development is safe; nothing is released by it. What follows, on
GitHub:

1. `check` runs `task check` on the push.
2. `flow` makes the version **final**: the one the commits since the last
   release ask for (table above). Every package and `uv.lock` follow,
   `CHANGELOG.md` gets the section, and the bot pushes
   `bump: version 0.3.1a0 → 0.4.0` back to development. **Pull before you
   go on** (`git pull --rebase origin development`).
3. `flow` opens the pull request development → master,
   `Release v0.4.0`, or retitles the open one. Later pushes update it; the
   version follows what the new commits ask for.
4. If the push ticked the last item of a phase, and
   `release.automerge_completed_phase` in `.github/flow.toml` is on, the
   flow runs `task check` and merges the pull request itself.

Watch it with `gh run list` or `uv run task state -- --online`.

## Versions

All packages, `amoorion` and every `amoorion-<platform>`, have one version
and are released together. Don't edit versions by hand; the loop sets them.

| Stage | Example | Where | Made by |
| ----- | ------- | ----- | ------- |
| released | `0.3.0`, tag `v0.3.0` | master; development right after the pull | the `release` workflow |
| pre-release | `0.3.1a0` | development, being made | `task flow:pull` (post-merge) |
| final | `0.4.0`, no tag | development and its pull request, ready | the `flow` workflow |

```sh
uv run task version                   # the version of every package
uv run amoorion-dev version next      # what the next release would be now
uv run amoorion-dev phases            # the phases and what is ticked
```

`amoorion.__version__` and the docs read the version from the installed
package, so they always match it.

## Release

Merging the release pull request is the release; only the author does it
(or the flow, for a completed phase). `release` tags master and makes the
GitHub release with its notes, `publish` puts every package on PyPI and
the release, `gh-pages` builds the web page. Then the loop starts again
with `task flow:pull`. Details, and what the author sets up once on
GitHub: [Releasing](releasing.md).

## Never

- push or commit to `master`, tag, release or publish by hand;
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
