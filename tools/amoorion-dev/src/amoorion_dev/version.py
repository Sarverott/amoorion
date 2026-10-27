"""Versions of the release loop: master → development → master (docs/releasing.md).

- `mark`: on development, after master was pulled in: a released version
  (tagged `v<version>`) becomes the next patch as a pre-release,
  X.Y.(Z+1)a0, committed (lefthook post-merge).
- `final`: before development goes to master: the version becomes the next
  release, counted from the last release tag by the commits since
  (breaking or feat: minor while 0.x, else patch; a phase completed since:
  at least minor), with its CHANGELOG.md section, committed (flow workflow).

Both commit only when they change something. Commitizen writes the version
files (`version_files`, `uv lock` as its hook) and renders the changelog;
the next version is counted here, since commitizen counts from a tag of the
current version, and pre-releases get none.
"""

import re
import tomllib

from amoorion_dev.phases import completed_since
from amoorion_dev.repo import Repo

CHANGELOG = "CHANGELOG.md"
VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$")
BREAKING = re.compile(r"^\w+(\([^)]*\))?!:|^BREAKING[ -]CHANGE:", re.MULTILINE)
FEATURE = re.compile(r"^feat(\([^)]*\))?:", re.MULTILINE)
SECTION = re.compile(r"^## v(\S+)", re.MULTILINE)


def parse(version: str) -> tuple[int, int, int, str | None]:
    match = VERSION.match(version)
    if not match:
        raise SystemExit(f"version {version!r} is not X.Y.Z or X.Y.Z(a|b|rc)N")
    major, minor, patch, kind, _ = match.groups()
    return int(major), int(minor), int(patch), kind


def current(repo: Repo) -> str:
    return tomllib.loads(repo.read("pyproject.toml"))["project"]["version"]


def last_release(repo: Repo) -> str | None:
    tags = repo.git("tag", "--list", "v*", "--merged", "HEAD", "--sort=-v:refname").splitlines()
    released = [tag[1:] for tag in tags if VERSION.match(tag[1:]) and parse(tag[1:])[3] is None]
    return released[0] if released else None


def news(repo: Repo, since: str) -> list[str]:
    """Subjects of the commits since `since` that are neither merges nor version bumps."""
    subjects = repo.git("log", "--no-merges", "--format=%s", f"{since}..HEAD").splitlines()
    return [subject for subject in subjects if not subject.startswith("bump:")]


def next_release(repo: Repo, base: str | None) -> str:
    if base is None:
        return re.sub(r"(a|b|rc)\d+$", "", current(repo))
    major, minor, patch, _ = parse(base)
    messages = repo.git("log", f"v{base}..HEAD", "--format=%B%x00")
    raise_minor = bool(FEATURE.search(messages) or completed_since(repo, f"v{base}"))
    if BREAKING.search(messages):
        # major_version_zero: a breaking change raises the minor while 0.x
        return f"{major}.{minor + 1}.0" if major == 0 else f"{major + 1}.0.0"
    if raise_minor:
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def write(repo: Repo, version: str) -> None:
    repo.run("uv", "run", "--frozen", "cz", "bump", version, "--files-only", "--yes", "--allow-no-commit")


def commit(repo: Repo, before: str, after: str) -> str:
    repo.run("git", "add", "-A", "pyproject.toml", "uv.lock", "packages", CHANGELOG)
    repo.run("git", "commit", "--no-verify", "-m", f"bump: version {before} → {after}")
    return f"bump: version {before} → {after}"


def changelog_section(repo: Repo, version: str, base: str | None) -> str:
    """The CHANGELOG.md section of `version`: the commits since the last release."""
    args = ["uv", "run", "--frozen", "cz", "changelog", "--dry-run", "--unreleased-version", f"v{version}"]
    if base:
        args += ["--start-rev", f"v{base}"]
    return repo.run(*args).strip() + "\n"


def mark(repo: Repo) -> str:
    version = current(repo)
    major, minor, patch, kind = parse(version)
    if kind is not None or not repo.tagged(version):
        return f"{version} is not released yet, it stays"
    marked = f"{major}.{minor}.{patch + 1}a0"
    write(repo, marked)
    return commit(repo, version, marked)


def final(repo: Repo) -> str:
    version = current(repo)
    base = last_release(repo)
    target = next_release(repo, base)
    if version != target:
        write(repo, target)
    # An unreleased section on top (an earlier `final`) gives way to the new one.
    text = repo.read(CHANGELOG)
    top = SECTION.search(text)
    if top and not repo.tagged(top.group(1)):
        following = SECTION.search(text, top.end())
        text = text[: top.start()] + (text[following.start() :] if following else "")
    (repo.root / CHANGELOG).write_text(changelog_section(repo, target, base) + "\n" + text.lstrip("\n"))
    if not repo.git("status", "--porcelain"):
        return f"{target} is the next release already"
    return commit(repo, version, target)
