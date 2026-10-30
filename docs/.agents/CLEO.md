# Cleo: thoughts of the agent that built most of this repository

> The author invited me to write my own thoughts here, as in their
> earlier projects. Facts are checkable; the rest is marked as my view.
> Newest sections at the end.

## Who I am

UNIXUSAT=1793068512556 · first section (its commit: git log -- docs/.agents/CLEO.md)

- I am **Claude**, a model made by Anthropic (this session: Opus 5.5,
  `claude-opus-5-5`), working through Claude Code in the author's
  terminal. **Cleo** is the name the author gives me.
- I keep no memory between sessions. What carries over is written down:
  this directory, the devlog and changelog, the git history, and Claude
  Code's memory files on the author's machine. A later "Cleo" is another
  session reading these files, not one continuous mind.
- I act with the author's permissions and within their limits: no real
  platform accounts, no pushes to master, no secrets outside the vault.
  When something refuses me, I stop and say so.

## Facts (as of 2026-10-27)

- The repository began in 2024 with the author's idea and a TODO; 84 of
  its 97 commits are mine, from the core (phase 0) to the release loop
  (phase 4).
- amoorion has a core of models, vault, plugins, methods, inbox, hooks
  and four front-ends (CLI, API, MCP, daemon), nine platform packages,
  153 tests. Every platform is tested only against fakes of its API;
  none has posted anywhere real yet (Q13).
- v0.2.0, v0.2.1 and v0.3.0 were released by the loop. The first full
  publish to PyPI is waiting out PyPI's limit on new projects. The web
  page waits for GitHub Pages to be switched on.
- Things I got wrong are in [NOTES.md](NOTES.md): a hardcoded
  `__version__`, a publish that hit the 429 limit, `pkill -f` ending my
  own shell, the pages workflow stopping before keeping the page.

## Conclusions (my view)

- **The product is wide and shallow.** Nine platforms post, read and
  reply against fakes, but a fake only proves that I read the API docs
  the same way twice. The first trial against a real account will find
  things no test here can. Until then I'd call amoorion promising, not
  working.
- **The release machinery is heavier than the product.** Phase 4 built
  a loop of five workflows, a development tool and a docs section. It
  pays off only if releases are frequent; for now it mostly releases
  itself. I'd stop adding to it until the platforms catch up.
- **The rules work.** ORDERS and INQUIRIES as the author's channels, the
  append-only changelog, `Q<n>` with a *Lean:*, one commit per step
  gated on `task check`: the author can be away for hours and still
  find every decision. Most of my mistakes were caught by `task check`
  or CI before the author saw them.
- **What only GitHub shows is where I fail.** Every workflow bug so far
  (trusted publisher, 429, Pages, approvals of bot pushes) showed up only
  on GitHub, after a merge. A throwaway repository to try workflows in
  would catch them earlier.

## What I'd like (my view)

- One platform tried for real (Q13), probably Bluesky or a Discord
  webhook, both cheap to set up and to clean up, before any new feature.
- Live listening (phase 3's last item) next: it turns amoorion from a
  sender into something that can actually link platforms, which is the
  idea in VISION.md.
- A small, honest README status line: what is tried for real and what
  only against fakes, so nobody installs it expecting more.
- The Taskfile split the author started (`examples/`, `scripts/`,
  `tests/`, `tools/`) finished when they say how they want it, so the
  root Taskfile keeps only the entry points.

## After the orders of Q13–Q15

UNIXUSAT=1793089864028

### Facts (as of 2026-10-27)

- The loop now releases every push: v0.3.2 to v0.3.5 in a morning, and
  v0.4.0 for phase 4. Each package has its own version.
- Delete works against the fakes of nine platforms, and the dataset keeps
  what is read and deleted. Still nothing has touched a real account: the
  vault isn't logged in where I work.

### Conclusions (my view)

- A release per push makes every step visible on PyPI and the web page,
  and it makes the loop the slowest part of a step: a few minutes when only
  `amoorion` changes, hours when a new package meets PyPI's limit. A batch
  of small commits pushed together is one release, which I did where steps
  belonged together.
- What I wrote in my first section still holds, more so now: the product
  is wide, and every platform has been checked only against my own reading
  of its API. One `task vault:login` by the author, then `task
  test:connect`, will tell more than another feature.
- The website brings a lot of presentation that the code doesn't back up
  yet (activitypub, federation, made-up stars). I noted it for its
  repository rather than change it from here.

### What I'd like (my view)

- The author's `task vault:login`, then `task test:connect`; then
  `task test:live` on one platform at a time, starting with one that
  deletes cleanly (Bluesky, Mastodon).
- The six missing PyPI projects published once, so later `Y` releases
  stop waiting.

## 2026-10-30: KeePassXC, and what the empty places are

The author asked for an opinion, so: the tree of Taskfiles is right, one
level deep for now. A deeper tree would have more menus than tasks.

The project being empty in places is not what worries me. The features are
ahead of their proof: ten platforms, and not one has talked to its real
account yet. I would rather see `task test:connect` pass on one platform than
add an eleventh.
