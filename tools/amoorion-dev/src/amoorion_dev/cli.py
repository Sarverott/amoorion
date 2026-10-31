"""amoorion-dev: the development tools' command line (see the package README)."""

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from amoorion_dev import bump
from amoorion_dev import notes as release_notes
from amoorion_dev import phases as plan
from amoorion_dev import webpage as web
from amoorion_dev import shape as shaping
from amoorion_dev import state as development
from amoorion_dev import version as versions
from amoorion_dev.repo import Repo
from amoorion_dev.show import show_state
from amoorion_dev.state_page import markdown

console = Console()


def published(
    repo: Repo,
    revision: str | None = None,
) -> list[dict[str, str]]:
    """The packages of the workspace, with their versions (at `revision`): amoorion and every one in packages/."""

    return [
        {
            "name": package.name,
            "path": package.path,
            "version": package.version(repo, revision) or "",
        }
        for package in versions.packages(repo)
    ]


def build_parser() -> argparse.ArgumentParser:
    """The command line of the tools: one subcommand per concern."""

    parser = argparse.ArgumentParser(
        prog="amoorion-dev",
        description="Development tools of amoorion",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="command",
    )

    state = commands.add_parser(
        "state",
        help="the state of development",
    )

    state.add_argument(
        "--online",
        action="store_true",
        help="also ask GitHub and PyPI",
    )

    state.add_argument(
        "--json",
        action="store_true",
    )

    state.add_argument(
        "--markdown",
        action="store_true",
        help="as the docs page",
    )

    version = commands.add_parser(
        "version",
        help="versions of the release loop",
    )

    version.add_argument(
        "action",
        choices=[
            "current",
            "list",
            "next",
            "mark",
            "final",
        ],
    )

    phases = commands.add_parser(
        "phases",
        help="the phases of TODO.md",
    )

    phases.add_argument(
        "--completed",
        action="store_true",
        help="only those a release would complete (for the flow)",
    )

    notes = commands.add_parser(
        "notes",
        help="release notes of a tag",
    )

    notes.add_argument("tag")

    notes.add_argument(
        "--title",
        action="store_true",
        help="only the release's title",
    )

    packages = commands.add_parser(
        "packages",
        help="the packages and their versions, as JSON (for the publish workflow)",
    )

    packages.add_argument(
        "--only",
        default="",
        help="only these, comma-separated (empty: all)",
    )

    packages.add_argument(
        "--released",
        metavar="TAG",
        help="only those the release TAG bumped, at their version there",
    )

    setting = commands.add_parser(
        "setting",
        help="a value of .github/flow.toml, e.g. pypi.tries",
    )

    setting.add_argument("key")

    site = commands.add_parser(
        "site",
        help="build the web page",
    )

    site.add_argument(
        "--out",
        type=Path,
        default=Path("site"),
    )

    site.add_argument(
        "--examples",
        type=Path,
        default=Path("examples/build"),
    )

    site.add_argument(
        "--website",
        type=Path,
        help="the built presentation page (website/dist), put at the root",
    )

    shape = commands.add_parser(
        "shape",
        help="format the code in amoorion's shape (shape.py)",
    )

    shape.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="files (default: every .py and .ipynb git knows or would add)",
    )

    shape.add_argument(
        "--check",
        action="store_true",
        help="only tell what is out of shape",
    )

    commands.add_parser(
        "identity",
        help="set git's user to the bot of .github/flow.toml",
    )

    return parser


def shape_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Format the code, or with `--check` only list what isn't in shape, failing if any."""

    paths = args.paths or [
        repo.root / name
        for name in repo.git(
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "*.py",
            "*.ipynb",
        ).splitlines()
    ]

    changed = shaping.run(
        paths,
        check=args.check,
    )

    for path in changed:
        print(path)

    return 1 if args.check and changed else 0


def state_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Show the state of development: as a table, JSON, or the docs' page."""

    found = development.read(
        repo,
        online=args.online,
    )

    if args.json:
        print(
            json.dumps(
                asdict(found),
                indent=2,
            )
        )

    elif args.markdown:
        print(
            markdown(found),
            end="",
        )

    else:
        show_state(found)

    return 0


def version_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Show or move versions (see `version` and `bump`)."""

    if args.action == "current":
        print(versions.current(repo))

    elif args.action == "list":
        table = Table(
            "Package",
            "Version",
            "Next release",
        )

        coming = versions.plan(
            repo,
            versions.last_release(repo),
        )

        for package in published(repo):
            table.add_row(
                package["name"],
                package["version"],
                coming.get(
                    package["name"],
                    "",
                ),
            )

        console.print(table)

    elif args.action == "next":
        print(
            versions.next_release(
                repo,
                versions.last_release(repo),
            )
        )

    else:
        print(getattr(bump, args.action)(repo))

    return 0


def phases_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """The phases of TODO.md, or those a release would complete."""

    last = versions.last_release(repo)

    if args.completed:
        for phase in plan.completed_since(repo, f"v{last}" if last else None):
            print(f"{phase.number}: {phase.title}")

    else:
        for phase in plan.phases(repo):
            print(
                f"{phase.number}: {phase.title}  {phase.done}/{phase.total}"
                + ("  complete" if phase.complete else "")
            )

    return 0


def notes_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Print the release notes of a tag, or only their title."""

    print(
        release_notes.title(
            repo,
            args.tag,
        )
        if args.title
        else release_notes.notes(
            repo,
            args.tag,
        ),
        end="\n" if args.title else "",
    )

    return 0


def packages_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """The packages as JSON, for the matrix of the publish workflow."""

    only = {name.strip() for name in args.only.split(",") if name.strip()}

    found = published(
        repo,
        args.released,
    )

    if args.released:
        bumped = set(
            versions.changed_in(
                repo,
                args.released,
            )
        )

        found = [package for package in found if package["name"] in bumped]

    print(
        json.dumps(
            [
                package
                for package in found
                if not only or package["name"] in only
            ]
        )
    )

    return 0


def setting_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Print one value of .github/flow.toml."""

    value: object = repo.settings()

    for part in args.key.split("."):
        if not isinstance(value, dict) or part not in value:
            print(
                f"no {args.key} in .github/flow.toml",
                file=sys.stderr,
            )

            return 1

        value = value[part]

    print(json.dumps(value) if isinstance(value, bool) else value)

    return 0


def site_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Build the web page."""

    for path in web.build(repo, args.out, args.examples, args.website):
        console.print(f"wrote {path}")

    return 0


def identity_command(
    repo: Repo,
    args: argparse.Namespace,
) -> int:
    """Make the bot of flow.toml git's user, for commits of the workflows."""

    bot = repo.settings().get(
        "bot",
        {},
    )

    repo.run(
        "git",
        "config",
        "user.name",
        bot["name"],
    )

    repo.run(
        "git",
        "config",
        "user.email",
        bot["email"],
    )

    print(f"git user: {bot['name']} <{bot['email']}>")

    return 0


COMMANDS = {
    "state": state_command,
    "version": version_command,
    "phases": phases_command,
    "notes": notes_command,
    "packages": packages_command,
    "setting": setting_command,
    "site": site_command,
    "shape": shape_command,
    "identity": identity_command,
}


def main(argv: Sequence[str] | None = None) -> int:
    """Parse and run a subcommand in the repository at hand; answers the exit code."""

    args = build_parser().parse_args(argv)

    return COMMANDS[args.command](
        Repo.here(),
        args,
    )


if __name__ == "__main__":
    sys.exit(main())
