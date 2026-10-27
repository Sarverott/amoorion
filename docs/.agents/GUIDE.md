# Working guide

How an iteration goes here, for every agent and for people working the
same way. Strict on purpose: the author answers in batches and reads the
result later, so every step must be findable, checked and told.

## 1. Begin

1. Read `AGENTS.md`, this guide and `MAP.md`; the commands of every
   step are in `docs/contributing.md`.
2. `uv run task state` (`-- --online` when GitHub matters): branch, version
   stage, open pull request, waiting orders or inquiries, phases.
3. `git status`: anything changed that you didn't make is the author's.
4. Be on `development`, up to date with origin
   (`git pull --rebase --tags origin development`; the release merges master
   back by itself, `task flow:pull` only if it didn't).

## 2. Take in what the author left

In this order, each its own commit:

1. **The author's edits**: commit them as they are (`docs(...)`,
   `chore(...)`…). If they break `task check`, fix them in the same commit
   and say what and why in its body.
2. **ORDERS.md**: the batch moves word for word into
   `docs/changelog/phase-<n>.md` with the answered `Q<n>` (and its
   **Decision:**), BRAINSTORM.md loses those questions, ORDERS.md is left
   with its header only.
3. **INQUIRIES.md**, or an order in the chat: first the plan, items in
   TODO.md (and VISION.md when it is new ground) and the words, verbatim,
   in the changelog; then the work; the file is emptied when it is done.

## 3. Work, one step at a time

For every item:

1. Do the smallest whole step. New operations are methods; platforms are
   packages; dev tooling goes into `amoorion-dev`, not loose scripts.
2. Test it: against fakes, never real accounts. A bug fixed gets a test.
3. Touch what it changes in the docs: README, `docs/*.md`, `MAP.md`,
   `AGENTS.md`.
4. `uv run task check` must pass (exit code, not a grep).
5. Commit: conventional message, why in the body when not obvious, ending
   with your `Co-Authored-By:` line. Tick the TODO item in the commit that
   finishes it.
6. Push it: every push is a `Z` release (Q15). Wait for the `release` run
   to end (`gh run watch`), pull the merge back, then the next step.

Try things that can't run here (workflows, releases) in a throwaway clone
in your scratch space, never on the real branches.

## 4. Finish

1. Append a section to `docs/changelog/phase-<n>.md`:
   `## UNIXUSAT=<ms> · commit <hash>`, what was done, in prose.
2. Add a dated entry on top of `docs/.agents/NOTES.md`: what you found,
   what you assumed, what is untried.
3. Open questions go to BRAINSTORM.md as `Q<n>` with a *Lean:*.
4. Push `development`, watch `check` and `flow` (`gh run list`), fix what
   fails.
5. Tell the author: what was done, what broke and how it was fixed, what
   is untried, what they must do, the questions. Short, no jargon they
   didn't use.

## Never

- push or commit to `master`, merge pull requests, tag, release or publish
  by hand; the loop does it (`release.automerge` in `.github/flow.toml`);
- post to a real platform account, or run `task test:live`, without the
  author's go-ahead;
- rewrite a changelog section; settle a `Q<n>` in code;
- put a secret anywhere but the vault; overwrite `.env`;
- change repository settings on GitHub without asking.

## Where things go

| It is | It goes to |
| ----- | ---------- |
| the author's words | changelog, verbatim |
| a plan | VISION.md (why, what), TODO.md (checklist) |
| a question for the author | BRAINSTORM.md `Q<n>` |
| a finding, an assumption | `docs/.agents/NOTES.md` |
| how the repository is shaped | `MAP.md`, `docs/structure.md` |
| work for another repository | `~/__WORKSHOP/forge/NOTES-for-repositories.md` |
| a loose note of the author | `~/__WORKSHOP/craftbook/scrapnotes/` |
