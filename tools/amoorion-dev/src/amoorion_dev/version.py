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

- `mark`: on development, after master was pulled in: a released
  `amoorion` becomes the next patch as a pre-release, X.Y.(Z+1)a0,
  committed (lefthook post-merge, the release's merge back).
- `final`: before development goes to master: every package gets the
  version of the next release, with its CHANGELOG.md section, committed
  (flow workflow).

Both commit only when they change something. The versions are written into
each pyproject.toml here, `uv lock` follows; commitizen renders the
changelog.
"""

import re
import tomllib
from dataclasses import dataclass

from amoorion_dev.phases import completed_since, phases
from amoorion_dev.repo import Repo

CHANGELOG = "CHANGELOG.md"
VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$")
LINE = re.compile(r'^version = "[^"]*"', re.MULTILINE)
SECTION = re.compile(r"^## v(\S+)", re.MULTILINE)
MAIN = "amoorion"


@dataclass
class Package:
    name: str
    path: str  # "." for amoorion

    @property
    def pyproject(self) -> str:
        return "pyproject.toml" if self.path == "." else f"{self.path}/pyproject.toml"

    def version(self, repo: Repo, revision: str | None = None) -> str | None:
        text = repo.read(self.pyproject, revision)
        return tomllib.loads(text)["project"]["version"] if text else None


def packages(repo: Repo) -> list[Package]:
    """amoorion and every package in packages/."""
    found = [Package(MAIN, ".")]
    for pyproject in sorted((repo.root / "packages").glob("*/pyproject.toml")):
        name = tomllib.loads(pyproject.read_text())["project"]["name"]
        found.append(Package(name, str(pyproject.parent.relative_to(repo.root))))
    return found


def parse(version: str) -> tuple[int, int, int, str | None]:
    match = VERSION.match(version)
    if not match:
        raise SystemExit(f"version {version!r} is not X.Y.Z or X.Y.Z(a|b|rc)N")
    major, minor, patch, kind, _ = match.groups()
    return int(major), int(minor), int(patch), kind


def released(version: str) -> str:
    """The version without its pre-release part."""
    return re.sub(r"(a|b|rc)\d+$", "", version)


def current(repo: Repo) -> str:
    return tomllib.loads(repo.read("pyproject.toml"))["project"]["version"]


def last_release(repo: Repo, before: str = "HEAD") -> str | None:
    tags = repo.git("tag", "--list", "v*", "--merged", before, "--sort=-v:refname").splitlines()
    found = [tag[1:] for tag in tags if VERSION.match(tag[1:]) and parse(tag[1:])[3] is None]
    if before != "HEAD":
        found = [version for version in found if f"v{version}" != before]
    return found[0] if found else None


def news(repo: Repo, since: str, path: str | None = None) -> list[str]:
    """Subjects of the commits since `since` (touching `path`) that are neither merges nor version bumps."""
    args = ["log", "--no-merges", "--format=%s", f"{since}..HEAD"]
    subjects = repo.git(*args, *(["--", path] if path else [])).splitlines()
    return [subject for subject in subjects if not subject.startswith("bump:")]


def kind(repo: Repo, base: str | None) -> str:
    """"major", "minor" or "patch": what the release after `base` is."""
    if base is None:
        return "patch"
    completed = completed_since(repo, f"v{base}")
    if not completed:
        return "patch"
    last = repo.settings().get("release", {}).get("major_after_phase")
    plan = {phase.number: phase.complete for phase in phases(repo)}
    if last is not None and all(plan.get(number, False) for number in range(int(last) + 1)):
        return "major"
    return "minor"


def bumped(version: str, how: str) -> str:
    major, minor, patch, _ = parse(version)
    return {"major": f"{major + 1}.0.0", "minor": f"{major}.{minor + 1}.0", "patch": f"{major}.{minor}.{patch + 1}"}[how]


def next_release(repo: Repo, base: str | None) -> str:
    """The version of amoorion in the next release."""
    if base is None:
        return released(current(repo))
    return bumped(base, kind(repo, base))


def plan(repo: Repo, base: str | None) -> dict[str, str]:
    """The version of every package in the next release."""
    target = next_release(repo, base)
    how = kind(repo, base)
    versions = {}
    for package in packages(repo):
        before = package.version(repo, f"v{base}") if base else None
        if package.name == MAIN or how != "patch":
            versions[package.name] = target
        elif before is None:  # new since the last release
            versions[package.name] = released(package.version(repo) or target)
        elif news(repo, f"v{base}", package.path):
            versions[package.name] = bumped(before, "patch")
        else:
            versions[package.name] = before
    return versions


def changed_in(repo: Repo, tag: str) -> list[str]:
    """The packages whose version the release `tag` changed (what it publishes)."""
    base = last_release(repo, tag)
    return [
        package.name
        for package in packages(repo)
        if base is None or package.version(repo, f"v{base}") != package.version(repo, tag)
    ]


def write(repo: Repo, versions: dict[str, str]) -> None:
    for package in packages(repo):
        if package.name in versions and package.version(repo) != versions[package.name]:
            file = repo.root / package.pyproject
            file.write_text(LINE.sub(f'version = "{versions[package.name]}"', file.read_text(), count=1))
    repo.run("uv", "lock", "--quiet")


def commit(repo: Repo, before: str, after: str) -> str:
    repo.run("git", "add", "-A", "pyproject.toml", "uv.lock", "packages", CHANGELOG)
    repo.run("git", "commit", "--no-verify", "-m", f"bump: version {before} → {after}")
    return f"bump: version {before} → {after}"


def changelog_section(repo: Repo, version: str, base: str | None, versions: dict[str, str]) -> str:
    """The CHANGELOG.md section of `version`: the packages it bumps, the commits since the last release."""
    args = ["uv", "run", "--frozen", "cz", "changelog", "--dry-run", "--unreleased-version", f"v{version}"]
    if base:
        args += ["--start-rev", f"v{base}"]
    heading, _, rest = repo.run(*args).strip().partition("\n")
    bumps = [
        f"{name} {new}"
        for name, new in versions.items()
        if base is None or name == MAIN or new != _at(repo, name, base)
    ]
    return f"{heading}\n\n**Packages:** {', '.join(bumps)}\n{rest}\n"


def _at(repo: Repo, name: str, base: str) -> str | None:
    package = next(package for package in packages(repo) if package.name == name)
    return package.version(repo, f"v{base}")


def mark(repo: Repo) -> str:
    version = current(repo)
    major, minor, patch, kind_ = parse(version)
    if kind_ is not None or not repo.tagged(version):
        return f"{version} is not released yet, it stays"
    marked = f"{major}.{minor}.{patch + 1}a0"
    write(repo, {MAIN: marked})
    return commit(repo, version, marked)


def final(repo: Repo) -> str:
    version = current(repo)
    base = last_release(repo)
    versions = plan(repo, base)
    target = versions[MAIN]
    write(repo, versions)
    # An unreleased section on top (an earlier `final`) gives way to the new one.
    text = repo.read(CHANGELOG)
    top = SECTION.search(text)
    if top and not repo.tagged(top.group(1)):
        following = SECTION.search(text, top.end())
        text = text[: top.start()] + (text[following.start() :] if following else "")
    (repo.root / CHANGELOG).write_text(changelog_section(repo, target, base, versions) + "\n" + text.lstrip("\n"))
    if not repo.git("status", "--porcelain"):
        return f"{target} is the next release already"
    return commit(repo, version, target)
