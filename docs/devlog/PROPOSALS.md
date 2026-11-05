# PROPOSALS

Ideas put up for debate, by anyone working here: the author, Cleo, Joker,
Merlin, whoever joins. A question to answer goes to
[BRAINSTORM.md](BRAINSTORM.md); a proposal is an idea worked out far enough
to argue about. Each is `PP<n>` ("project proposition number n"), numbered
once and never reused. The form is the author's (PP0, word for word in
[phase-5 of the changelog](../changelog/phase-5.md)):

```md
### PP<n> beg
> from: full name, e.g. `Sett Sarverott A.A.B. <sett@sarverott.com>`
> addressing to: ALL, or names; formal or casual tone is read by whom it addresses
> related to: what it is about (how to name that: open, see PP1)
> label/topic/name/title: the name of its context
> taggings: (open, see PP1)

###### DEFINE
what is needed to understand the proposal; may answer a `Q<n>` or refer to an inquiry

###### COMBINE
drafting, refining the idea, equations, examples; pros and cons, the idea against reality

###### CONCLUDE
conclusions; questions for someone else to settle further (`Q<n>`), inquiries called for

> `UNIXUSAT=<ms since epoch>`
### PP<n> end
```

Answering a proposal and closing it are themselves open: PP1 proposes how.
Until they are decided, agents only add proposals and never decide one in
code; the questions a proposal raises go to BRAINSTORM.md as usual. The
`beg` and `end` headings mark each proposal; a `---` right after a heading
breaks the docs' build, so there is none between proposals.

---

### PP1 beg
> from: `Cleo (Claude Code, Opus 5.5 by Anthropic) <noreply@anthropic.com>`
> addressing to: `Sett Sarverott A.A.B. <sett@sarverott.com>`; Joker; Merlin
> related to: PP0; `docs/devlog/PROPOSALS.md`
> label/topic/name/title: how a proposal names what it is about, how it is answered, how it ends
> taggings: `process`, `devlog`

###### DEFINE
PP0 left two fields open, "related to" and "taggings", and didn't say how
others answer a proposal or when it ends. Without that, a debate across
several repositories and agents can't be followed: Joker's handoff in
amoorion-website and Cleo's notes here already point at each other in
loose words.

###### COMBINE
**related to:** a list of references, each one of these forms, so a reader
(or a tool) can find it:

| Form | Means |
| --- | --- |
| `PP3`, `Q16` | a proposal or question of this repository |
| `amoorion-website:PP2` | the same of another repository of the forge |
| `docs/devlog/TODO.md`, `src/amoorion/api/base.py:102` | a file, a line |
| `commit 253b50f`, `amoorion-website@253b50f` | a commit, here or there |
| `v0.4.36` | a release |
| `phase 5`, `TODO: Filling the vault through those menus` | a phase, an item of the plan |

**taggings:** a few lowercase words from a short list kept in this header,
grown when a proposal needs a new one: `process`, `devlog`, `release`,
`website`, `api`, `cli`, `vault`, `platform`, `docs`, `agents`. A tool could
then list proposals by tag; nothing needs it yet.

**answering:** a new `PP<n>` whose `related to` names the one it answers,
not an edit of somebody else's proposal. A proposal stays as its author
wrote it, the way the changelog does. A debate is then a chain:
PP4 related to PP1, PP7 related to PP4.

**ending:** the author decides. A decided proposal moves word for word,
with its answers and the **Decision:**, into `docs/changelog/phase-<n>.md`,
as answered `Q<n>` do now. What it calls for becomes a plan (VISION.md,
TODO.md) or a `Q<n>`.

Against it: a chain of whole proposals is heavier than a comment, and a
short "yes, but" would take a full form. A lighter form for answers (only
`from`, `related to` and CONCLUDE) would help there.

###### CONCLUDE
- Q: are these reference forms enough, and is a light form for answers wanted?
- Q: does the author alone close a proposal, or may its writer withdraw it?
- If agreed, `task state` could also list proposals by tag and show chains.

> `UNIXUSAT=1793858276625`
### PP1 end

### PP2 beg
> from: `Cleo (Claude Code, Opus 5.5 by Anthropic) <noreply@anthropic.com>`
> addressing to: `Sett Sarverott A.A.B. <sett@sarverott.com>`; Joker; Merlin
> related to: `scripts/build-website.sh`; `amoorion-website@9a9d1e2`; `amoorion-website@253b50f`; `v0.4.36`
> label/topic/name/title: one lockfile and a gate for amoorion-website before amoorion releases it
> taggings: `website`, `release`

###### DEFINE
Every release of amoorion clones amoorion-website's `main` and builds it.
Since `amoorion-website@9a9d1e2` there is no `package-lock.json`, only
`bun.lock`, but amoorion installs with `npm install`, which takes the newest
versions its ranges allow each time. Joker's side installs with npm and no
lock as well. The website has no CI and its hooks are commented out.

###### COMBINE
- **Bun from `bun.lock`:** amoorion's page job adds `oven-sh/setup-bun` and
  runs `bun install --frozen-lockfile`, then `bun run build -- --base`.
  The website keeps the lock Merlin's side writes already. Every release
  builds the same packages. The cost is one more tool in the page job.
- **npm with a committed `package-lock.json`:** nothing new in the job;
  Merlin's side would have to stop removing it, which it did once already.
- **A gate on the website's pull requests:** `lint`, `build --base
  /amoorion/`, its 13 tests, and Joker's probe (`{}` in `AMOORION_DATA` must
  fail the build). Then amoorion's release stops being the first to find a
  broken `main`.

###### CONCLUDE
- Q: Bun with `bun.lock` (Cleo's lean), or npm with a committed lock?
- Inquiry for amoorion-website: a CI workflow on its pull requests, as above.
- Once decided, Cleo changes `scripts/build-website.sh` and `gh-pages.yml`
  here; the website's half goes to `forge/NOTES-for-repositories.md`.

> `UNIXUSAT=1793858276626`
### PP2 end

### PP3 beg
> from: `Cleo (Claude Code, Opus 5.5 by Anthropic) <noreply@anthropic.com>`
> addressing to: ALL
> related to: `amoorion-website@5bfd7d6`; `amoorion-website@253b50f`; `~/__WORKSHOP/craftbook/scrapnotes/scrapnote-1793855954470.md`
> label/topic/name/title: every commit names the agent that did the work
> taggings: `agents`, `process`

###### DEFINE
In amoorion-website every commit is "Sett Sarverott". Telling Joker's work
from Merlin's took reading e-mail addresses and time zones. Here Cleo signs
with `Co-Authored-By:`, as the rules ask; Joker and Merlin have no such rule.

###### COMBINE
A `Co-Authored-By:` line per agent that worked on the commit, with a name
the author chooses for each, e.g. `Co-Authored-By: Joker <…>`,
`Co-Authored-By: Merlin <…>`. GitHub shows them, and `git log
--grep=Joker` finds an agent's work. For Merlin it has to be in AI Studio's
instructions, as it writes its own commit messages. For Joker, whose work
the author commits, the author's commit can carry the line.

A scope convention (`feat(joker): …`) would work too, but it takes the
place of the scope that says what changed.

Against it: one more thing to remember for each commit made by hand.

###### CONCLUDE
- Q: which names and addresses for Joker and Merlin?
- Inquiry for amoorion-website: the rule in its `AGENTS.md`, and in
  Merlin's instructions in AI Studio.
- Workshop-wide, it would belong in `~/__WORKSHOP/AGENTS.md` (BOS), a
  candidate **BOS method**.

> `UNIXUSAT=1793858276627`
### PP3 end
