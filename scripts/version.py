"""Versions of the release loop: master → development → master (docs/releasing.md).

    current   print the version of every package (they are released together)
    mark      on development, after master was pulled in: when the version is
              released (tagged v<version>), make it the next patch as a
              pre-release, X.Y.(Z+1)a0, and commit it (lefthook post-merge)
    final     before development goes to master: make the version the next
              release, counted from the last release tag by the commits since
              (breaking or feat: minor while 0.x, else patch), write its
              CHANGELOG.md section, and commit (release workflow on development)

`mark` and `final` commit only when they change something. Commitizen writes
the version files (`version_files`, `uv lock` as its hook) and renders the
changelog; the next version is counted here, since commitizen counts from a
tag of the current version, and pre-releases get none.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$")
BREAKING = re.compile(r"^\w+(\([^)]*\))?!:|^BREAKING[ -]CHANGE:", re.MULTILINE)
FEATURE = re.compile(r"^feat(\([^)]*\))?:", re.MULTILINE)
SECTION = re.compile(r"^## v(\S+)", re.MULTILINE)


def run(*args: str, check: bool = True) -> str:
    result = subprocess.run(args, cwd=ROOT, check=check, text=True, capture_output=True, stdin=subprocess.DEVNULL)
    return result.stdout.strip()


def current() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


def parse(version: str) -> tuple[int, int, int, str | None]:
    match = VERSION.match(version)
    if not match:
        raise SystemExit(f"version {version!r} is not X.Y.Z or X.Y.Z(a|b|rc)N")
    major, minor, patch, kind, _ = match.groups()
    return int(major), int(minor), int(patch), kind


def tagged(version: str) -> bool:
    return bool(run("git", "tag", "--list", f"v{version}"))


def last_release() -> str | None:
    tags = run("git", "tag", "--list", "v*", "--merged", "HEAD", "--sort=-v:refname").splitlines()
    released = [tag[1:] for tag in tags if VERSION.match(tag[1:]) and parse(tag[1:])[3] is None]
    return released[0] if released else None


def write(version: str) -> None:
    run("uv", "run", "--frozen", "cz", "bump", version, "--files-only", "--yes", "--allow-no-commit")


def commit(before: str, after: str) -> None:
    run("git", "add", "-A", "pyproject.toml", "uv.lock", "packages", "CHANGELOG.md")
    run("git", "commit", "--no-verify", "-m", f"bump: version {before} → {after}")
    print(f"bump: version {before} → {after}")


def next_release(base: str | None) -> str:
    if base is None:
        return current().split("a")[0].split("b")[0].split("rc")[0]
    major, minor, patch, _ = parse(base)
    messages = run("git", "log", f"v{base}..HEAD", "--format=%B%x00")
    if BREAKING.search(messages):
        # major_version_zero: a breaking change raises the minor while 0.x
        return f"{major}.{minor + 1}.0" if major == 0 else f"{major + 1}.0.0"
    if FEATURE.search(messages):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def changelog_section(version: str, base: str | None) -> str:
    """The CHANGELOG.md section of `version`: the commits since the last release."""
    args = ["uv", "run", "--frozen", "cz", "changelog", "--dry-run", "--unreleased-version", f"v{version}"]
    if base:
        args += ["--start-rev", f"v{base}"]
    return run(*args).strip() + "\n"


def cmd_current() -> None:
    print(current())


def cmd_mark() -> None:
    version = current()
    major, minor, patch, kind = parse(version)
    if kind is not None or not tagged(version):
        print(f"{version} is not released yet, it stays")
        return
    marked = f"{major}.{minor}.{patch + 1}a0"
    write(marked)
    commit(version, marked)


def cmd_final() -> None:
    version = current()
    base = last_release()
    final = next_release(base)
    if version != final:
        write(final)
    # An unreleased section on top (an earlier `final`) gives way to the new one.
    text = CHANGELOG.read_text() if CHANGELOG.exists() else ""
    top = SECTION.search(text)
    if top and not tagged(top.group(1)):
        following = SECTION.search(text, top.end())
        text = text[: top.start()] + (text[following.start() :] if following else "")
    CHANGELOG.write_text(changelog_section(final, base) + "\n" + text.lstrip("\n"))
    if not run("git", "status", "--porcelain"):
        print(f"{final} is the next release already")
        return
    commit(version, final)


def main() -> None:
    commands = {"current": cmd_current, "mark": cmd_mark, "final": cmd_final}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(__doc__)
    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
