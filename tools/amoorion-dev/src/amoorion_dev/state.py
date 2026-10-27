"""The state of development, read from the repository and, unless offline, from GitHub and PyPI.

Local: branch, version and where it stands in the release loop, the last
release, what development has that master hasn't. The plan: phases, open
questions, orders and inquiries waiting. Remote (optional): the open
release pull request, the last run of every workflow, the latest GitHub
release, the version on PyPI. GitHub is asked with GH_TOKEN or GITHUB_TOKEN
when set, else without (60 calls an hour).
"""

import json
import os
import re
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any

from amoorion_dev import phases as plan
from amoorion_dev import version as versions
from amoorion_dev.repo import Repo

QUESTION = re.compile(r"^## (Q\d+): (.+)$", re.MULTILINE)
WAITING = {"orders": "docs/devlog/ORDERS.md", "inquiries": "docs/devlog/INQUIRIES.md"}
TIMEOUT = 5
KINDS = {"patch": "Z: a step", "minor": "Y: a phase completed", "major": "X: all phases done"}


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


def stage(repo: Repo, version: str) -> str:
    if versions.parse(version)[3] is not None:
        return "pre-release: the next release is being made"
    if repo.tagged(version):
        return "released"
    return "final: ready for master"


def waiting(repo: Repo, path: str) -> bool:
    """Whether the author left something below the header paragraph."""
    text = repo.read(path)
    body = text.split("\n\n", 2)[2] if text.count("\n\n") >= 2 else ""
    return bool(body.strip())


def counts(repo: Repo, master: str) -> tuple[int | None, int | None]:
    if not repo.git("rev-parse", "--verify", "-q", master):
        return None, None
    behind, ahead = (repo.git("rev-list", "--left-right", "--count", f"{master}...HEAD") or "0 0").split()
    return int(ahead), int(behind)


def fetch(url: str) -> Any:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "amoorion-dev"})
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=TIMEOUT) as answer:
        return json.load(answer)


def remote(repo: Repo) -> dict[str, Any]:
    settings = repo.settings()
    slug = settings.get("repository", {}).get("slug", "")
    work = settings.get("branches", {}).get("work", "development")
    release = settings.get("branches", {}).get("release", "master")
    api = f"https://api.github.com/repos/{slug}"
    found: dict[str, Any] = {}
    asks = {
        "pull_request": f"{api}/pulls?state=open&base={release}&head={slug.split('/')[0]}:{work}",
        "runs": f"{api}/actions/runs?per_page=30",
        "release": f"{api}/releases/latest",
        "pypi": "https://pypi.org/pypi/amoorion/json",
    }
    for name, url in asks.items():
        try:
            answer = fetch(url)
        except Exception as error:  # offline, rate-limited, not there yet: say so, go on
            found[name] = {"error": f"{type(error).__name__}: {error}"}
            continue
        if name == "pull_request":
            found[name] = (
                {"number": answer[0]["number"], "title": answer[0]["title"], "url": answer[0]["html_url"]}
                if answer
                else None
            )
        elif name == "runs":
            latest: dict[str, dict[str, str]] = {}
            for run in answer.get("workflow_runs", []):
                latest.setdefault(
                    run["name"],
                    {
                        "branch": run["head_branch"],
                        "status": run["conclusion"] or run["status"],
                        "url": run["html_url"],
                    },
                )
            found[name] = latest
        elif name == "release":
            found[name] = {"tag": answer["tag_name"], "url": answer["html_url"]}
        else:
            found[name] = {"version": answer["info"]["version"]}
    return found


def read(repo: Repo, online: bool = False) -> State:
    version = versions.current(repo)
    last = versions.last_release(repo)
    master = repo.settings().get("branches", {}).get("release", "master")
    ahead, behind = counts(repo, f"origin/{master}")
    coming = versions.plan(repo, last)
    return State(
        branch=repo.git("branch", "--show-current") or "(detached)",
        version=version,
        stage=stage(repo, version),
        last_release=last,
        next_release=versions.next_release(repo, last),
        news=versions.news(repo, f"v{last}") if last else [],
        ahead_of_master=ahead,
        behind_master=behind,
        changed_files=len(repo.git("status", "--porcelain").splitlines()),
        phases=[asdict(phase) | {"complete": phase.complete} for phase in plan.phases(repo)],
        phase_release=[
            f"{phase.number}: {phase.title}"
            for phase in plan.completed_since(repo, f"v{last}" if last else None)
        ],
        questions=[f"{number}: {title}" for number, title in QUESTION.findall(repo.read("docs/devlog/BRAINSTORM.md"))],
        waiting={name: waiting(repo, path) for name, path in WAITING.items()},
        packages={
            package.name: {"version": package.version(repo) or "", "next": coming.get(package.name, "")}
            for package in versions.packages(repo)
        },
        release_kind=versions.kind(repo, last),
        remote=remote(repo) if online else {},
    )


def markdown(state: State) -> str:
    """The state as a page of the docs (docs/devlog/STATE.md, made at every build)."""
    lines = [
        "# State of development",
        "",
        "Made when these docs were built, by `amoorion-dev state --markdown`.",
        "",
        "| | |",
        "| --- | --- |",
        f"| Version | `{state.version}` ({state.stage}) |",
        f"| Last release | {f'`v{state.last_release}`' if state.last_release else 'none yet'} |",
        f"| Next release | `v{state.next_release}` ({KINDS[state.release_kind]}) |",
        f"| Commits since the last release | {len(state.news)} |",
    ]
    if state.phase_release:
        lines.append(f"| Completes | phase {', phase '.join(state.phase_release)} |")
    remote = state.remote
    if isinstance(remote.get("pull_request"), dict) and "url" in remote["pull_request"]:
        pr = remote["pull_request"]
        lines.append(f"| Release pull request | [#{pr['number']} {pr['title']}]({pr['url']}) |")
    if isinstance(remote.get("pypi"), dict) and "version" in remote["pypi"]:
        lines.append(f"| On PyPI | `{remote['pypi']['version']}` |")
    lines += ["", "## Packages", "", "| Package | Version | In the next release |", "| --- | --- | --- |"]
    for name, found in state.packages.items():
        coming = found["next"] if found["next"] != found["version"] else "unchanged"
        lines.append(f"| `{name}` | `{found['version']}` | {coming} |")
    lines += ["", "## Phases", "", "| Phase | Done | |", "| --- | --- | --- |"]
    for phase in state.phases:
        mark = "complete" if phase["complete"] else "in progress" if phase["done"] else "not started"
        lines.append(f"| {phase['number']}: {phase['title']} | {phase['done']}/{phase['total']} | {mark} |")
    lines += ["", "## Open questions", ""]
    lines += [f"- {question}" for question in state.questions] or ["None."]
    if isinstance(remote.get("runs"), dict) and remote["runs"]:
        lines += ["", "## Workflows", "", "| Workflow | Branch | Last run |", "| --- | --- | --- |"]
        for name, run in sorted(remote["runs"].items()):
            lines.append(f"| {name} | {run['branch']} | [{run['status']}]({run['url']}) |")
    return "\n".join(lines) + "\n"
