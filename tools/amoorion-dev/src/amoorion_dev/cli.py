"""amoorion-dev: the development tools' command line (see the package README)."""

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from amoorion_dev import notes as release_notes
from amoorion_dev import phases as plan
from amoorion_dev import site as web
from amoorion_dev import state as development
from amoorion_dev import version as versions
from amoorion_dev.repo import Repo

console = Console()


def show_state(state: development.State) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column()
    summary.add_row("Branch", state.branch + (f"  [yellow]{state.changed_files} files changed[/]" if state.changed_files else ""))
    summary.add_row("Version", f"{state.version}  [dim]{state.stage}[/]")
    summary.add_row("Last release", f"v{state.last_release}" if state.last_release else "none yet")
    summary.add_row(
        "Next release",
        f"v{state.next_release}  [dim]{development.KINDS[state.release_kind]}, {len(state.news)} commits since the last[/]",
    )
    if state.ahead_of_master is not None:
        summary.add_row("Against master", f"{state.ahead_of_master} ahead, {state.behind_master} behind")
    if state.phase_release:
        summary.add_row("Completes", "[green]phase " + ", phase ".join(state.phase_release) + "[/] (a phase release)")
    waiting = [name for name, there in state.waiting.items() if there]
    if waiting:
        summary.add_row("Waiting", "[yellow]" + ", ".join(waiting) + " from the author[/]")
    remote = state.remote
    pr = remote.get("pull_request")
    if isinstance(pr, dict) and "url" in pr:
        summary.add_row("Pull request", f"#{pr['number']} {pr['title']}  [dim]{pr['url']}[/]")
    elif "pull_request" in remote and pr is None:
        summary.add_row("Pull request", "none open")
    for name in ("release", "pypi"):
        found = remote.get(name)
        if isinstance(found, dict):
            summary.add_row(
                {"release": "GitHub release", "pypi": "On PyPI"}[name],
                found.get("tag") or found.get("version") or f"[red]{found.get('error')}[/]",
            )
    console.print(Panel(summary, title="amoorion: state of development", expand=False))

    packages = Table("Package", "Version", "Next release", title="Packages (a version each)", title_justify="left")
    for name, found in state.packages.items():
        coming = found["next"] if found["next"] != found["version"] else "[dim]unchanged[/]"
        packages.add_row(name, found["version"], coming)
    console.print(packages)

    phases = Table("Phase", "Done", title="Phases (docs/devlog/TODO.md)", title_justify="left")
    for phase in state.phases:
        style = "green" if phase["complete"] else "yellow" if phase["done"] else "dim"
        phases.add_row(f"[{style}]{phase['number']}: {phase['title']}[/]", f"{phase['done']}/{phase['total']}")
    console.print(phases)
    if state.questions:
        console.print("[bold]Open questions[/] (docs/devlog/BRAINSTORM.md): " + "; ".join(state.questions))
    runs = remote.get("runs")
    if isinstance(runs, dict) and runs:
        table = Table("Workflow", "Branch", "Last run", title="Workflows", title_justify="left")
        for name, run in sorted(runs.items()):
            colour = {"success": "green", "failure": "red"}.get(run["status"], "yellow")
            table.add_row(name, run["branch"], f"[{colour}]{run['status']}[/]")
        console.print(table)


def published(repo: Repo, revision: str | None = None) -> list[dict[str, str]]:
    """The packages of the workspace, with their versions (at `revision`): amoorion and every one in packages/."""
    return [
        {"name": package.name, "path": package.path, "version": package.version(repo, revision) or ""}
        for package in versions.packages(repo)
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="amoorion-dev", description="Development tools of amoorion")
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    state = commands.add_parser("state", help="the state of development")
    state.add_argument("--online", action="store_true", help="also ask GitHub and PyPI")
    state.add_argument("--json", action="store_true")
    state.add_argument("--markdown", action="store_true", help="as the docs page")

    version = commands.add_parser("version", help="versions of the release loop")
    version.add_argument("action", choices=["current", "list", "next", "mark", "final"])

    phases = commands.add_parser("phases", help="the phases of TODO.md")
    phases.add_argument("--completed", action="store_true", help="only those a release would complete (for the flow)")

    notes = commands.add_parser("notes", help="release notes of a tag")
    notes.add_argument("tag")
    notes.add_argument("--title", action="store_true", help="only the release's title")

    packages = commands.add_parser("packages", help="the packages and their versions, as JSON (for the publish workflow)")
    packages.add_argument("--only", default="", help="only these, comma-separated (empty: all)")
    packages.add_argument("--released", metavar="TAG", help="only those the release TAG bumped, at their version there")

    setting = commands.add_parser("setting", help="a value of .github/flow.toml, e.g. pypi.tries")
    setting.add_argument("key")

    site = commands.add_parser("site", help="build the web page")
    site.add_argument("--out", type=Path, default=Path("site"))
    site.add_argument("--examples", type=Path, default=Path("examples/build"))
    site.add_argument("--website", type=Path, help="the built presentation page (website/dist), put at the root")

    commands.add_parser("identity", help="set git's user to the bot of .github/flow.toml")

    args = parser.parse_args(argv)
    repo = Repo.here()

    if args.command == "state":
        found = development.read(repo, online=args.online)
        if args.json:
            print(json.dumps(asdict(found), indent=2))
        elif args.markdown:
            print(development.markdown(found), end="")
        else:
            show_state(found)
    elif args.command == "version":
        if args.action == "current":
            print(versions.current(repo))
        elif args.action == "list":
            table = Table("Package", "Version", "Next release")
            coming = versions.plan(repo, versions.last_release(repo))
            for package in published(repo):
                table.add_row(package["name"], package["version"], coming.get(package["name"], ""))
            console.print(table)
        elif args.action == "next":
            print(versions.next_release(repo, versions.last_release(repo)))
        else:
            print(getattr(versions, args.action)(repo))
    elif args.command == "phases":
        last = versions.last_release(repo)
        if args.completed:
            for phase in plan.completed_since(repo, f"v{last}" if last else None):
                print(f"{phase.number}: {phase.title}")
        else:
            for phase in plan.phases(repo):
                print(f"{phase.number}: {phase.title}  {phase.done}/{phase.total}" + ("  complete" if phase.complete else ""))
    elif args.command == "notes":
        print(release_notes.title(repo, args.tag) if args.title else release_notes.notes(repo, args.tag), end="\n" if args.title else "")
    elif args.command == "packages":
        only = {name.strip() for name in args.only.split(",") if name.strip()}
        found = published(repo, args.released)
        if args.released:
            bumped = set(versions.changed_in(repo, args.released))
            found = [package for package in found if package["name"] in bumped]
        print(json.dumps([package for package in found if not only or package["name"] in only]))
    elif args.command == "setting":
        value: object = repo.settings()
        for part in args.key.split("."):
            if not isinstance(value, dict) or part not in value:
                print(f"no {args.key} in .github/flow.toml", file=sys.stderr)
                return 1
            value = value[part]
        print(json.dumps(value) if isinstance(value, bool) else value)
    elif args.command == "site":
        for path in web.build(repo, args.out, args.examples, args.website):
            console.print(f"wrote {path}")
    elif args.command == "identity":
        bot = repo.settings().get("bot", {})
        repo.run("git", "config", "user.name", bot["name"])
        repo.run("git", "config", "user.email", bot["email"])
        print(f"git user: {bot['name']} <{bot['email']}>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
