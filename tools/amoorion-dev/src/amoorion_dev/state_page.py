"""The state of development as a page of the docs."""

from amoorion_dev.state import KINDS, State


def markdown(state: State) -> str:
    """The state as a page of the docs (docs/devlog/STATE.md, made at every build)."""

    lines = [
        "# State of development",
        "",
        "Made when these docs were built, by `amoorion-dev state --markdown`.",
        "",
        "| | |",
        "| --- | --- |",
        f"| Version | `{state.version}` ({state.stage}) |",
        f"| Last release | {f'`v{state.last_release}`' if state.last_release else 'none yet'} |",
        f"| Next release | `v{state.next_release}` ({KINDS[state.release_kind]}) |",
        f"| Commits since the last release | {len(state.news)} |",
    ]

    if state.phase_release:
        lines.append(
            f"| Completes | phase {', phase '.join(state.phase_release)} |"
        )

    remote = state.remote

    if (
        isinstance(remote.get("pull_request"), dict)
        and "url" in remote["pull_request"]
    ):
        pr = remote["pull_request"]

        lines.append(
            f"| Release pull request | [#{pr['number']} {pr['title']}]({pr['url']}) |"
        )

    if isinstance(remote.get("pypi"), dict) and "version" in remote["pypi"]:
        lines.append(f"| On PyPI | `{remote['pypi']['version']}` |")

    lines += [
        "",
        "## Packages",
        "",
        "| Package | Version | In the next release |",
        "| --- | --- | --- |",
    ]

    for name, found in state.packages.items():
        coming = (
            found["next"] if found["next"] != found["version"] else "unchanged"
        )

        lines.append(f"| `{name}` | `{found['version']}` | {coming} |")

    lines += [
        "",
        "## Phases",
        "",
        "| Phase | Done | |",
        "| --- | --- | --- |",
    ]

    for phase in state.phases:
        mark = (
            "complete"
            if phase["complete"]
            else "in progress"
            if phase["done"]
            else "not started"
        )

        lines.append(
            f"| {phase['number']}: {phase['title']} | {phase['done']}/{phase['total']} | {mark} |"
        )

    lines += [
        "",
        "## Open questions",
        "",
    ]

    lines += [f"- {question}" for question in state.questions] or ["None."]

    if isinstance(remote.get("runs"), dict) and remote["runs"]:
        lines += [
            "",
            "## Workflows",
            "",
            "| Workflow | Branch | Last run |",
            "| --- | --- | --- |",
        ]

        for name, run in sorted(remote["runs"].items()):
            lines.append(
                f"| {name} | {run['branch']} | [{run['status']}]({run['url']}) |"
            )

    return "\n".join(lines) + "\n"
