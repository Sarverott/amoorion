"""Release notes: what changed (the commits, CHANGELOG.md) and how it happened (docs/changelog/).

The phase files of docs/changelog/ are append-only, so what a release adds
to them is what follows their text at the previous release.
"""

import re

from amoorion_dev.phases import completed_since
from amoorion_dev.repo import Repo
from amoorion_dev.version import VERSION, parse

STORY = "docs/changelog"


def section(
    changelog: str,
    tag: str,
) -> str:
    """The section of `tag` in CHANGELOG.md, without its heading."""

    lines, inside = [], False

    for line in changelog.splitlines():
        if line.startswith("## v"):
            if inside:
                break

            inside = line.startswith(f"## {tag} ")

            continue

        if inside:
            lines.append(line)

    return "\n".join(lines).strip()


def previous_release(
    repo: Repo,
    tag: str,
) -> str | None:
    """The release before a tag, skipping pre-releases."""

    tags = repo.git(
        "tag",
        "--list",
        "v*",
        "--merged",
        tag,
        "--sort=-v:refname",
    ).splitlines()

    released = [
        t
        for t in tags
        if t != tag and VERSION.match(t[1:]) and parse(t[1:])[3] is None
    ]

    return released[0] if released else None


def story(
    repo: Repo,
    tag: str,
    since: str | None,
) -> list[tuple[str, str]]:
    """(phase title, what was appended to its file) for every phase file that grew."""

    told = []

    files = repo.git(
        "ls-tree",
        "--name-only",
        tag,
        f"{STORY}/",
    ).splitlines()

    for path in sorted(
        files,
        key=lambda name: [
            int(n) if n.isdigit() else n for n in re.split(r"(\d+)", name)
        ],
    ):
        now = repo.read(
            path,
            tag,
        )

        before = (
            repo.read(
                path,
                since,
            )
            if since
            else ""
        )

        heading = now.splitlines()[0].lstrip("# ").strip() if now else path

        if before and now.startswith(before):
            added = now[len(before) :]

        else:  # a new file: all of it but its title
            added = now.partition("\n")[2]

        added = added.replace(
            "Append-only.\n",
            "",
            1,
        ).strip()

        if added:
            told.append(
                (
                    heading,
                    added,
                )
            )

    return told


def title(
    repo: Repo,
    tag: str,
) -> str:
    """The title of a release; it names the phases it completed."""

    since = previous_release(
        repo,
        tag,
    )

    phases = (
        completed_since(
            repo,
            since,
        )
        if since
        else []
    )

    done = "; ".join(
        f"phase {phase.number} done: {phase.title}" for phase in phases
    )

    return f"amoorion {tag}" + (f" — {done}" if done else "")


def notes(
    repo: Repo,
    tag: str,
) -> str:
    """The release notes: what changed, from the changelog, and the phases done."""

    since = previous_release(
        repo,
        tag,
    )

    parts = []

    changes = section(
        repo.read(
            "CHANGELOG.md",
            tag,
        ),
        tag,
    )

    parts.append(
        "## What changed\n\n" + (changes or "No changes worth a line.")
    )

    told = story(
        repo,
        tag,
        f"{since}" if since else None,
    )

    if told:
        parts.append(
            "## The story\n\nFrom `docs/changelog/`, what was added since "
            + (since or "the start")
            + "."
        )

        for heading, body in told:
            # Its own headings sit below the phase's.
            body = re.sub(
                r"^(#+) ",
                lambda match: "#" * min(len(match.group(1)) + 2, 6) + " ",
                body,
                flags=re.M,
            )

            parts.append(f"### {heading}\n\n{body}")

    return "\n\n".join(parts) + "\n"
