"""Phases of the plan: `## Phase <n>: <title>` in docs/devlog/TODO.md, with `- [x]` / `- [ ]` items.

A phase is complete when all its items are ticked. A phase completed since
the last release makes the next release a phase release (`.github/flow.toml`).
"""

import re
from dataclasses import dataclass

from amoorion_dev.repo import Repo

TODO = "docs/devlog/TODO.md"
HEADING = re.compile(r"^## Phase (\d+): (.+)$", re.MULTILINE)
ITEM = re.compile(r"^- \[([ xX])\] ", re.MULTILINE)


@dataclass
class Phase:
    number: int
    title: str
    done: int
    total: int

    @property
    def complete(self) -> bool:
        return self.total > 0 and self.done == self.total


def parse(text: str) -> list[Phase]:
    headings = list(HEADING.finditer(text))
    phases = []
    for heading, following in zip(headings, [*headings[1:], None], strict=True):
        body = text[heading.end() : following.start() if following else len(text)]
        # The text after a phase's list (a closing line, the next sections) is not its items.
        body = re.split(r"^(?!- |\s|$)", body, maxsplit=1, flags=re.MULTILINE)[0] if body.strip() else body
        marks = ITEM.findall(body)
        title = heading.group(2).strip()
        phases.append(Phase(int(heading.group(1)), title, sum(mark != " " for mark in marks), len(marks)))
    return phases


def phases(repo: Repo, revision: str | None = None) -> list[Phase]:
    return parse(repo.read(TODO, revision))


def current(repo: Repo) -> Phase | None:
    """The first phase not complete."""
    return next((phase for phase in phases(repo) if not phase.complete), None)


def completed_since(repo: Repo, revision: str | None) -> list[Phase]:
    """Phases complete now that were not complete at `revision` (the last release)."""
    before = {phase.number: phase.complete for phase in phases(repo, revision)} if revision else {}
    return [phase for phase in phases(repo) if phase.complete and not before.get(phase.number, False)]
