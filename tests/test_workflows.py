"""The workflows keep the shape docs/releasing.md describes."""

from pathlib import Path

import pytest
import yaml

GITHUB = Path(__file__).parents[1] / ".github"
WORKFLOWS = sorted((GITHUB / "workflows").glob("*.yml"))


def load(path: Path) -> dict:

    data = yaml.safe_load(path.read_text())

    # YAML 1.1 reads the key `on` as True.
    data["on"] = data.pop(
        True,
        data.get("on"),
    )

    return data


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.stem)
def test_every_workflow_can_be_started_by_hand(path):

    assert "workflow_dispatch" in load(path)["on"]


def test_every_package_is_published_by_the_local_action():

    [step] = [
        s
        for s in load(GITHUB / "workflows" / "publish.yml")["jobs"]["package"][
            "steps"
        ]
        if "uses" in s and s["uses"].startswith("./")
    ]

    assert step["uses"] == "./.github/actions/publish-package"

    action = yaml.safe_load(
        (GITHUB / "actions" / "publish-package" / "action.yml").read_text()
    )

    assert action["runs"]["using"] == "composite"

    assert all(
        step.get("shell") == "bash"
        for step in action["runs"]["steps"]
        if "run" in step
    )


def test_the_bot_commits_as_set_in_flow_toml():

    for path in WORKFLOWS:
        assert "git config user." not in path.read_text(), (
            f"{path.name}: use `amoorion-dev identity`"
        )


def test_a_release_merges_back_after_publishing_and_the_page():

    jobs = load(GITHUB / "workflows" / "release.yml")["jobs"]

    assert jobs["publish"]["uses"] == "./.github/workflows/publish.yml"

    assert jobs["pages"]["uses"] == "./.github/workflows/gh-pages.yml"

    assert set(jobs["back"]["needs"]) == {"release", "publish", "pages"}

    for called in ("publish", "gh-pages"):
        assert (
            "workflow_call"
            in load(GITHUB / "workflows" / f"{called}.yml")["on"]
        )


def test_check_does_not_wait_on_the_flows_pull_requests():

    assert load(GITHUB / "workflows/check.yml")["on"]["pull_request"][
        "branches"
    ] == ["development"]


def test_the_flow_tries_again_to_start_the_release():

    steps = load(GITHUB / "workflows/flow.yml")["jobs"]["propose"]["steps"]

    [step] = [step for step in steps if step.get("name") == "Release by itself"]

    assert (
        "for try in" in step["run"]
        and "gh workflow run release.yml --ref master && exit 0" in step["run"]
    )
