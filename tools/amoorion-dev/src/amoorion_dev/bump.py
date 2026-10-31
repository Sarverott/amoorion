"""Writing versions down: the two moves of the release loop.

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

from amoorion_dev.repo import Repo
from amoorion_dev.version import (
    MAIN,
    current,
    last_release,
    packages,
    parse,
    plan,
)

CHANGELOG = "CHANGELOG.md"
LINE = re.compile(
    r'^version = "[^"]*"',
    re.MULTILINE,
)
SECTION = re.compile(
    r"^## v(\S+)",
    re.MULTILINE,
)


def write(
    repo: Repo,
    versions: dict[str, str],
) -> None:
    """Write the versions into the packages' pyproject.toml, only where they differ."""

    for package in packages(repo):
        if (
            package.name in versions
            and package.version(repo) != versions[package.name]
        ):
            file = repo.root / package.pyproject

            file.write_text(
                LINE.sub(
                    f'version = "{versions[package.name]}"',
                    file.read_text(),
                    count=1,
                )
            )

    repo.run(
        "uv",
        "lock",
        "--quiet",
    )


def commit(
    repo: Repo,
    before: str,
    after: str,
) -> str:
    """Commit the bump, with commitizen's form of message."""

    # Same version: an earlier `final` set it, only the changelog section is renewed.
    message = (
        f"bump: version {before} → {after}"
        if before != after
        else f"bump: changelog of {after}"
    )

    repo.run(
        "git",
        "add",
        "-A",
        "pyproject.toml",
        "uv.lock",
        "packages",
        CHANGELOG,
    )

    repo.run(
        "git",
        "commit",
        "--no-verify",
        "-m",
        message,
    )

    return message


def changelog_section(
    repo: Repo,
    version: str,
    base: str | None,
    versions: dict[str, str],
) -> str:
    """The CHANGELOG.md section of `version`: the packages it bumps, the commits since the last release."""

    args = [
        "uv",
        "run",
        "--frozen",
        "cz",
        "changelog",
        "--dry-run",
        "--unreleased-version",
        f"v{version}",
    ]

    if base:
        args += [
            "--start-rev",
            f"v{base}",
        ]

    heading, _, rest = repo.run(*args).strip().partition("\n")

    bumps = [
        f"{name} {new}"
        for name, new in versions.items()
        if base is None or name == MAIN or new != _at(repo, name, base)
    ]

    return f"{heading}\n\n**Packages:** {', '.join(bumps)}\n{rest}\n"


def _at(
    repo: Repo,
    name: str,
    base: str,
) -> str | None:
    """A package's version at a release."""

    package = next(
        package for package in packages(repo) if package.name == name
    )

    return package.version(
        repo,
        f"v{base}",
    )


def mark(repo: Repo) -> str:
    """After a release: the next pre-release, X.Y.(Z+1)a0. An unreleased version stays.

    Answers what it did, for the log.
    """

    version = current(repo)

    major, minor, patch, kind_ = parse(version)

    if kind_ is not None or not repo.tagged(version):
        return f"{version} is not released yet, it stays"

    marked = f"{major}.{minor}.{patch + 1}a0"

    write(
        repo,
        {MAIN: marked},
    )

    return commit(
        repo,
        version,
        marked,
    )


def final(repo: Repo) -> str:
    """Before a release: finalize the versions of what changed, and write the changelog.

    Runs in the flow; answers what it did, for the log.
    """

    version = current(repo)

    base = last_release(repo)

    versions = plan(
        repo,
        base,
    )

    target = versions[MAIN]

    write(
        repo,
        versions,
    )

    # An unreleased section on top (an earlier `final`) gives way to the new one.
    text = repo.read(CHANGELOG)

    top = SECTION.search(text)

    if top and not repo.tagged(top.group(1)):
        following = SECTION.search(
            text,
            top.end(),
        )

        text = text[: top.start()] + (
            text[following.start() :] if following else ""
        )

    (repo.root / CHANGELOG).write_text(
        changelog_section(repo, target, base, versions)
        + "\n"
        + text.lstrip("\n")
    )

    if not repo.git("status", "--porcelain"):
        return f"{target} is the next release already"

    return commit(
        repo,
        version,
        target,
    )
