"""amoorion-dev against small git repositories made here."""

import subprocess

import pytest
import json

from amoorion_dev import notes, phases, state, version, webpage
from amoorion_dev.state_page import markdown
from amoorion_dev.repo import Repo

TODO = """# TODO

## Phase 0: core

- [x] one
- [x] two,
      on two lines

## Phase 1: platforms

- [x] three
- [ ] four

Later phases: see VISION.md.
"""


@pytest.fixture
def repo(tmp_path):

    def git(*args):

        subprocess.run(
            [
                "git",
                *args,
            ],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

    def write(
        path,
        text,
    ):

        (tmp_path / path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        (tmp_path / path).write_text(text)

    def commit(
        message,
        files=None,
    ):

        for path, text in (files or {}).items():
            write(
                path,
                text,
            )

        git(
            "add",
            "-A",
        )

        git(
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            message,
        )

    git(
        "init",
        "-q",
        "-b",
        "development",
    )

    commit(
        "feat: first",
        {
            "pyproject.toml": '[project]\nname = "amoorion"\nversion = "0.2.0"\n',
            "packages/amoorion-a/pyproject.toml": '[project]\nname = "amoorion-a"\nversion = "0.2.0"\n',
            "packages/amoorion-b/pyproject.toml": '[project]\nname = "amoorion-b"\nversion = "0.2.0"\n',
            "docs/devlog/TODO.md": TODO,
            "docs/changelog/phase-0.md": "# Phase 0: core\n\nAppend-only.\n\n## one\n\nthe start\n",
            "CHANGELOG.md": "## v0.2.0 (2026-10-26)\n\n### Feat\n\n- first\n",
        },
    )

    git(
        "tag",
        "v0.2.0",
    )

    return Repo(tmp_path), commit, git


def test_phases_parse_items_and_stop_at_the_list_end():

    found = phases.parse(TODO)

    assert [(p.number, p.done, p.total, p.complete) for p in found] == [
        (0, 2, 2, True),
        (1, 1, 2, False),
    ]


@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        ([], "0.2.1"),  # a loop without news still releases a patch
        (["docs: d", "fix: f"], "0.2.1"),
        (["fix: f", "feat(cli): x"], "0.2.1"),  # every step is a Z (Q15)
        (["feat!: x"], "0.2.1"),
        (["fix: f\n\nBREAKING CHANGE: gone"], "0.2.1"),
    ],
)
def test_next_release(
    repo,
    messages,
    expected,
):

    found, commit, _ = repo

    for message in messages:
        commit(message)

    assert version.next_release(found, version.last_release(found)) == expected


def test_a_completed_phase_raises_the_minor(repo):

    found, commit, _ = repo

    commit(
        "docs: phase 1 done",
        {
            "docs/devlog/TODO.md": TODO.replace(
                "- [ ] four",
                "- [x] four",
            )
        },
    )

    assert [p.number for p in phases.completed_since(found, "v0.2.0")] == [1]

    assert version.next_release(found, "0.2.0") == "0.3.0"


def test_last_release_skips_pre_release_tags(repo):

    found, commit, git = repo

    commit("fix: f")

    git(
        "tag",
        "v0.2.1a0",
    )

    assert version.last_release(found) == "0.2.0"

    assert found.tagged("0.2.0") and not found.tagged("0.2.1")

    assert version.news(found, "v0.2.0") == ["fix: f"]


def test_parse():

    assert version.parse("0.2.1a0") == (0, 2, 1, "a")

    with pytest.raises(SystemExit):
        version.parse("1.0")


def test_notes_have_the_commits_and_the_story(repo):

    found, commit, git = repo

    commit(
        "feat: second",
        {
            "docs/changelog/phase-0.md": "# Phase 0: core\n\nAppend-only.\n\n## one\n\nthe start\n\n## two\n\nmore\n",
            "docs/changelog/phase-1.md": "# Phase 1: platforms\n\nAppend-only.\n\n## three\n\nnew phase\n",
            "CHANGELOG.md": "## v0.3.0 (2026-10-27)\n\n### Feat\n\n- second\n\n## v0.2.0 (2026-10-26)\n\n- first\n",
        },
    )

    git(
        "tag",
        "v0.3.0",
    )

    text = notes.notes(
        found,
        "v0.3.0",
    )

    assert (
        "## What changed" in text
        and "- second" in text
        and "- first" not in text
    )

    assert (
        "### Phase 0: core" in text
        and "#### two" in text
        and "the start" not in text
    )

    assert (
        "### Phase 1: platforms" in text
        and "new phase" in text
        and "Append-only" not in text
    )

    assert notes.title(found, "v0.3.0") == "amoorion v0.3.0"


def test_state_reads_offline(repo):

    found, _, _ = repo

    read = state.read(found)

    assert (
        read.version == "0.2.0"
        and read.stage == "released"
        and read.next_release == "0.2.1"
    )

    assert [p["number"] for p in read.phases] == [0, 1] and read.remote == {}

    assert "| 1: platforms | 1/2 | in progress |" in markdown(read)

    assert (
        read.packages["amoorion-a"] == {"version": "0.2.0", "next": "0.2.0"}
        and read.release_kind == "patch"
    )

    assert "| `amoorion` | `0.2.0` | 0.2.1 |" in markdown(
        read
    ) and "(Z: a step)" in markdown(read)


def test_a_patch_bumps_amoorion_and_the_changed_packages_only(repo):

    found, commit, _ = repo

    commit(
        "fix(a): f",
        {"packages/amoorion-a/x.py": "x = 1\n"},
    )

    assert version.plan(found, "0.2.0") == {
        "amoorion": "0.2.1",
        "amoorion-a": "0.2.1",
        "amoorion-b": "0.2.0",
    }


def test_a_phase_bumps_every_package_to_the_minor(repo):

    found, commit, _ = repo

    commit(
        "fix(a): f",
        {"packages/amoorion-a/x.py": "x = 1\n"},
    )

    commit(
        "docs: phase 1 done",
        {
            "docs/devlog/TODO.md": TODO.replace(
                "- [ ] four",
                "- [x] four",
            )
        },
    )

    assert set(version.plan(found, "0.2.0").values()) == {"0.3.0"}


def test_the_last_phase_of_the_plan_is_the_major(repo):

    found, commit, _ = repo

    commit(
        "chore: plan",
        {".github/flow.toml": "[release]\nmajor_after_phase = 1\n"},
    )

    commit(
        "docs: phase 1 done",
        {
            "docs/devlog/TODO.md": TODO.replace(
                "- [ ] four",
                "- [x] four",
            )
        },
    )

    assert version.kind(found, "0.2.0") == "major" and set(
        version.plan(found, "0.2.0").values()
    ) == {"1.0.0"}


def test_a_release_publishes_what_it_bumped(repo):

    found, commit, git = repo

    commit(
        "fix(b): f",
        {"packages/amoorion-b/x.py": "x = 1\n"},
    )

    for package in version.packages(found):
        if package.name in ("amoorion", "amoorion-b"):
            file = found.root / package.pyproject

            file.write_text(
                file.read_text().replace(
                    "0.2.0",
                    "0.2.1",
                )
            )

    commit("bump: version 0.2.0 → 0.2.1")

    git(
        "tag",
        "v0.2.1",
    )

    assert version.changed_in(found, "v0.2.1") == ["amoorion", "amoorion-b"]

    assert version.last_release(found, "v0.2.1") == "0.2.0"


def test_the_site_puts_the_presentation_page_at_its_root(
    repo,
    tmp_path,
):

    found, commit, _ = repo

    commit(
        "docs: readme",
        {"README.md": "# amoorion\n\nbadges\n\n---\n\nWhat it is.\n"},
    )

    website = tmp_path / "website"

    (website / "assets").mkdir(parents=True)

    (website / "index.html").write_text("<html>presentation</html>")

    examples = tmp_path / "examples"

    examples.mkdir()

    (examples / "01-first-steps.html").write_text("<html>example</html>")

    out = tmp_path / "site"

    webpage.build(
        found,
        out,
        examples,
        website,
    )

    assert (out / "index.html").read_text() == "<html>presentation</html>"

    assert (
        "What it is." in (out / "project.html").read_text()
        and "badges" not in (out / "project.html").read_text()
    )

    assert (
        'href="01-first-steps.html"'
        in (out / "examples" / "index.html").read_text()
    )

    manifest = json.loads((out / "manifest.json").read_text())

    assert manifest["packages"] == {
        "amoorion": "0.2.0",
        "amoorion-a": "0.2.0",
        "amoorion-b": "0.2.0",
    }

    assert (
        "project.html" in manifest["pages"]
        and (out / "site.webmanifest").is_file()
        and (out / ".nojekyll").is_file()
    )

    assert "Lost between platforms" in (out / "404.html").read_text()

    assert "Allow: /" in (out / "robots.txt").read_text()

    assert "examples/01-first-steps.html" in (out / "llms.txt").read_text()


def test_without_the_presentation_page_the_project_page_is_the_root(
    repo,
    tmp_path,
):

    found, _, _ = repo

    webpage.build(
        found,
        tmp_path / "site",
    )

    assert "Universal tool" in (tmp_path / "site" / "index.html").read_text()

    assert not (tmp_path / "site" / "project.html").exists()
