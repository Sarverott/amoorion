"""Versions of the release loop: master → development → master (docs/releasing.md).

Every package has its own version (Q15). A release is one of three kinds,
counted from the last release tag (`v<version of amoorion>`):

- `Z`, patch: every step. `amoorion` is bumped, and every package changed
  since the last release; the rest keep their versions.
- `Y`, minor: a phase of TODO.md completed since the last release. Every
  package gets the new version of `amoorion`.
- `X`, major: the phase `release.major_after_phase` of `.github/flow.toml`
  (the last of the plan) completed, so all phases are done. Every package
  too.

Writing them down, `mark` and `final`: bump.py.
"""

import re
import tomllib
from dataclasses import dataclass

from amoorion_dev.phases import completed_since, phases
from amoorion_dev.repo import Repo

VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$")
MAIN = "amoorion"


@dataclass
class Package:
    name: str
    path: str  # "." for amoorion

    @property
    def pyproject(self) -> str:

        return (
            "pyproject.toml"
            if self.path == "."
            else f"{self.path}/pyproject.toml"
        )

    def version(
        self,
        repo: Repo,
        revision: str | None = None,
    ) -> str | None:

        text = repo.read(
            self.pyproject,
            revision,
        )

        return tomllib.loads(text)["project"]["version"] if text else None


def packages(repo: Repo) -> list[Package]:
    """amoorion and every package in packages/."""

    found = [
        Package(
            MAIN,
            ".",
        )
    ]

    for pyproject in sorted((repo.root / "packages").glob("*/pyproject.toml")):
        name = tomllib.loads(pyproject.read_text())["project"]["name"]

        found.append(
            Package(
                name,
                str(pyproject.parent.relative_to(repo.root)),
            )
        )

    return found


def parse(version: str) -> tuple[int, int, int, str | None]:

    match = VERSION.match(version)

    if not match:
        raise SystemExit(f"version {version!r} is not X.Y.Z or X.Y.Z(a|b|rc)N")

    major, minor, patch, kind, _ = match.groups()

    return int(major), int(minor), int(patch), kind


def released(version: str) -> str:
    """The version without its pre-release part."""

    return re.sub(
        r"(a|b|rc)\d+$",
        "",
        version,
    )


def current(repo: Repo) -> str:

    return tomllib.loads(repo.read("pyproject.toml"))["project"]["version"]


def last_release(
    repo: Repo,
    before: str = "HEAD",
) -> str | None:

    tags = repo.git(
        "tag",
        "--list",
        "v*",
        "--merged",
        before,
        "--sort=-v:refname",
    ).splitlines()

    found = [
        tag[1:]
        for tag in tags
        if VERSION.match(tag[1:]) and parse(tag[1:])[3] is None
    ]

    if before != "HEAD":
        found = [version for version in found if f"v{version}" != before]

    return found[0] if found else None


def news(
    repo: Repo,
    since: str,
    path: str | None = None,
) -> list[str]:
    """Subjects of the commits since `since` (touching `path`) that are neither merges nor version bumps."""

    args = [
        "log",
        "--no-merges",
        "--format=%s",
        f"{since}..HEAD",
    ]

    subjects = repo.git(
        *args,
        *(
            [
                "--",
                path,
            ]
            if path
            else []
        ),
    ).splitlines()

    return [subject for subject in subjects if not subject.startswith("bump:")]


def kind(
    repo: Repo,
    base: str | None,
) -> str:
    """ "major", "minor" or "patch": what the release after `base` is."""

    if base is None:
        return "patch"

    completed = completed_since(
        repo,
        f"v{base}",
    )

    if not completed:
        return "patch"

    last = (
        repo.settings()
        .get(
            "release",
            {},
        )
        .get("major_after_phase")
    )

    plan = {phase.number: phase.complete for phase in phases(repo)}

    if last is not None and all(
        plan.get(number, False) for number in range(int(last) + 1)
    ):
        return "major"

    return "minor"


def bumped(
    version: str,
    how: str,
) -> str:

    major, minor, patch, _ = parse(version)

    return {
        "major": f"{major + 1}.0.0",
        "minor": f"{major}.{minor + 1}.0",
        "patch": f"{major}.{minor}.{patch + 1}",
    }[how]


def next_release(
    repo: Repo,
    base: str | None,
) -> str:
    """The version of amoorion in the next release."""

    if base is None:
        return released(current(repo))

    return bumped(
        base,
        kind(
            repo,
            base,
        ),
    )


def plan(
    repo: Repo,
    base: str | None,
) -> dict[str, str]:
    """The version of every package in the next release."""

    target = next_release(
        repo,
        base,
    )

    how = kind(
        repo,
        base,
    )

    versions = {}

    for package in packages(repo):
        before = (
            package.version(
                repo,
                f"v{base}",
            )
            if base
            else None
        )

        if package.name == MAIN or how != "patch":
            versions[package.name] = target

        elif before is None:  # new since the last release
            versions[package.name] = released(package.version(repo) or target)

        elif news(repo, f"v{base}", package.path):
            versions[package.name] = bumped(
                before,
                "patch",
            )

        else:
            versions[package.name] = before

    return versions


def changed_in(
    repo: Repo,
    tag: str,
) -> list[str]:
    """The packages whose version the release `tag` changed (what it publishes)."""

    base = last_release(
        repo,
        tag,
    )

    return [
        package.name
        for package in packages(repo)
        if base is None
        or package.version(repo, f"v{base}") != package.version(repo, tag)
    ]
