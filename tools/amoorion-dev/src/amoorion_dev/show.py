"""The state of development in the terminal."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from amoorion_dev.state import KINDS, State

console = Console()


def show_state(state: State) -> None:
    """Print the state of development as tables."""

    summary = Table.grid(
        padding=(
            0,
            2,
        )
    )

    summary.add_column(style="bold")

    summary.add_column()

    summary.add_row(
        "Branch",
        state.branch
        + (
            f"  [yellow]{state.changed_files} files changed[/]"
            if state.changed_files
            else ""
        ),
    )

    summary.add_row(
        "Version",
        f"{state.version}  [dim]{state.stage}[/]",
    )

    summary.add_row(
        "Last release",
        f"v{state.last_release}" if state.last_release else "none yet",
    )

    summary.add_row(
        "Next release",
        f"v{state.next_release}  [dim]{KINDS[state.release_kind]}, {len(state.news)} commits since the last[/]",
    )

    if state.ahead_of_master is not None:
        summary.add_row(
            "Against master",
            f"{state.ahead_of_master} ahead, {state.behind_master} behind",
        )

    if state.phase_release:
        summary.add_row(
            "Completes",
            "[green]phase "
            + ", phase ".join(state.phase_release)
            + "[/] (a phase release)",
        )

    waiting = [name for name, there in state.waiting.items() if there]

    if waiting:
        summary.add_row(
            "Waiting",
            "[yellow]" + ", ".join(waiting) + " from the author[/]",
        )

    remote = state.remote

    pr = remote.get("pull_request")

    if isinstance(pr, dict) and "url" in pr:
        summary.add_row(
            "Pull request",
            f"#{pr['number']} {pr['title']}  [dim]{pr['url']}[/]",
        )

    elif "pull_request" in remote and pr is None:
        summary.add_row(
            "Pull request",
            "none open",
        )

    for name in ("release", "pypi"):
        found = remote.get(name)

        if isinstance(found, dict):
            summary.add_row(
                {"release": "GitHub release", "pypi": "On PyPI"}[name],
                found.get("tag")
                or found.get("version")
                or f"[red]{found.get('error')}[/]",
            )

    console.print(
        Panel(
            summary,
            title="amoorion: state of development",
            expand=False,
        )
    )

    packages = Table(
        "Package",
        "Version",
        "Next release",
        title="Packages (a version each)",
        title_justify="left",
    )

    for name, found in state.packages.items():
        coming = (
            found["next"]
            if found["next"] != found["version"]
            else "[dim]unchanged[/]"
        )

        packages.add_row(
            name,
            found["version"],
            coming,
        )

    console.print(packages)

    phases = Table(
        "Phase",
        "Done",
        title="Phases (docs/devlog/TODO.md)",
        title_justify="left",
    )

    for phase in state.phases:
        style = (
            "green"
            if phase["complete"]
            else "yellow"
            if phase["done"]
            else "dim"
        )

        phases.add_row(
            f"[{style}]{phase['number']}: {phase['title']}[/]",
            f"{phase['done']}/{phase['total']}",
        )

    console.print(phases)

    if state.questions:
        console.print(
            "[bold]Open questions[/] (docs/devlog/BRAINSTORM.md): "
            + "; ".join(state.questions)
        )

    runs = remote.get("runs")

    if isinstance(runs, dict) and runs:
        table = Table(
            "Workflow",
            "Branch",
            "Last run",
            title="Workflows",
            title_justify="left",
        )

        for name, run in sorted(runs.items()):
            colour = {
                "success": "green",
                "failure": "red",
            }.get(
                run["status"],
                "yellow",
            )

            table.add_row(
                name,
                run["branch"],
                f"[{colour}]{run['status']}[/]",
            )

        console.print(table)
