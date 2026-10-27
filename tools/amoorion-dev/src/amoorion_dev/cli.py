"""amoorion-dev: the development tools' command line (see the package README)."""

import argparse
import json
import sys
import tomllib
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
    summary.add_row("Next release", f"v{state.next_release}  [dim]{len(state.news)} commits since the last[/]")
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


def published(repo: Repo) -> list[dict[str, str]]:
    """The packages released and published together: amoorion and every one in packages/."""
    found = [{"name": "amoorion", "path": "."}]
    for pyproject in sorted((repo.root / "packages").glob("*/pyproject.toml")):
        found.append({"name": tomllib.loads(pyproject.read_text())["project"]["name"], "path": str(pyproject.parent.relative_to(repo.root))})
    return found


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="amoorion-dev", description="Development tools of amoorion")
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    state = commands.add_parser("state", help="the state of development")
    state.add_argument("--online", action="store_true", help="also ask GitHub and PyPI")
    state.add_argument("--json", action="store_true")
    state.add_argument("--markdown", action="store_true", help="as the docs page")

    version = commands.add_parser("version", help="versions of the release loop")
    version.add_argument("action", choices=["current", "next", "mark", "final"])

    phases = commands.add_parser("phases", help="the phases of TODO.md")
    phases.add_argument("--completed", action="store_true", help="only those a release would complete (for the flow)")

    notes = commands.add_parser("notes", help="release notes of a tag")
    notes.add_argument("tag")
    notes.add_argument("--title", action="store_true", help="only the release's title")

    commands.add_parser("packages", help="the published packages, as JSON (for the publish workflow)")

    site = commands.add_parser("site", help="build the web page")
    site.add_argument("--out", type=Path, default=Path("site"))
    site.add_argument("--examples", type=Path, default=Path("examples/build"))

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
        print(json.dumps(published(repo)))
    elif args.command == "site":
        for path in web.build(repo, args.out, args.examples):
            console.print(f"wrote {path}")
    elif args.command == "identity":
        bot = repo.settings().get("bot", {})
        repo.run("git", "config", "user.name", bot["name"])
        repo.run("git", "config", "user.email", bot["email"])
        print(f"git user: {bot['name']} <{bot['email']}>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
