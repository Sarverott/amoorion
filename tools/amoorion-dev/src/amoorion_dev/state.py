"""The state of development, read from the repository and, unless offline, from GitHub and PyPI.

Local: branch, version and where it stands in the release loop, the last
release, what development has that master hasn't. The plan: phases, open
questions, orders and inquiries waiting. Remote (optional): remote.py.
"""

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from amoorion_dev import phases as plan
from amoorion_dev import version as versions
from amoorion_dev.remote import remote
from amoorion_dev.repo import Repo

QUESTION = re.compile(
    r"^## (Q\d+): (.+)$",
    re.MULTILINE,
)
WAITING = {
    "orders": "docs/devlog/ORDERS.md",
    "inquiries": "docs/devlog/INQUIRIES.md",
}
KINDS = {
    "patch": "Z: a step",
    "minor": "Y: a phase completed",
    "major": "X: all phases done",
}


@dataclass
class State:
    branch: str
    version: str
    stage: str
    last_release: str | None
    next_release: str
    news: list[str]
    ahead_of_master: int | None
    behind_master: int | None
    changed_files: int
    phases: list[dict[str, Any]]
    phase_release: list[str]
    questions: list[str]
    waiting: dict[str, bool]
    # name -> {"version": now, "next": in the next release} (Q15: a version each)
    packages: dict[str, dict[str, str]] = field(default_factory=dict)
    release_kind: str = "patch"
    remote: dict[str, Any] = field(default_factory=dict)


def stage(
    repo: Repo,
    version: str,
) -> str:

    if versions.parse(version)[3] is not None:
        return "pre-release: the next release is being made"

    if repo.tagged(version):
        return "released"

    return "final: ready for master"


def waiting(
    repo: Repo,
    path: str,
) -> bool:
    """Whether the author left something below the header paragraph."""

    text = repo.read(path)

    body = text.split("\n\n", 2)[2] if text.count("\n\n") >= 2 else ""

    return bool(body.strip())


def counts(
    repo: Repo,
    master: str,
) -> tuple[int | None, int | None]:

    if not repo.git("rev-parse", "--verify", "-q", master):
        return None, None

    behind, ahead = (
        repo.git("rev-list", "--left-right", "--count", f"{master}...HEAD")
        or "0 0"
    ).split()

    return int(ahead), int(behind)


def read(
    repo: Repo,
    online: bool = False,
) -> State:

    version = versions.current(repo)

    last = versions.last_release(repo)

    master = (
        repo.settings()
        .get(
            "branches",
            {},
        )
        .get(
            "release",
            "master",
        )
    )

    ahead, behind = counts(
        repo,
        f"origin/{master}",
    )

    coming = versions.plan(
        repo,
        last,
    )

    return State(
        branch=repo.git("branch", "--show-current") or "(detached)",
        version=version,
        stage=stage(
            repo,
            version,
        ),
        last_release=last,
        next_release=versions.next_release(
            repo,
            last,
        ),
        news=versions.news(
            repo,
            f"v{last}",
        )
        if last
        else [],
        ahead_of_master=ahead,
        behind_master=behind,
        changed_files=len(
            repo.git(
                "status",
                "--porcelain",
            ).splitlines()
        ),
        phases=[
            asdict(phase) | {"complete": phase.complete}
            for phase in plan.phases(repo)
        ],
        phase_release=[
            f"{phase.number}: {phase.title}"
            for phase in plan.completed_since(
                repo, f"v{last}" if last else None
            )
        ],
        questions=[
            f"{number}: {title}"
            for number, title in QUESTION.findall(
                repo.read("docs/devlog/BRAINSTORM.md")
            )
        ],
        waiting={name: waiting(repo, path) for name, path in WAITING.items()},
        packages={
            package.name: {
                "version": package.version(repo) or "",
                "next": coming.get(package.name, ""),
            }
            for package in versions.packages(repo)
        },
        release_kind=versions.kind(
            repo,
            last,
        ),
        remote=remote(repo) if online else {},
    )
