"""scripts/version.py: which version the next release gets, counted from the last release tag."""

import importlib.util
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("version", ROOT / "scripts" / "version.py")
version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q", "-b", "development")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "feat: first")
    git("tag", "v0.2.0")
    monkeypatch.setattr(version, "ROOT", tmp_path)

    def commit(message):
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", message)

    return commit, git


@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        ([], "0.2.1"),  # a loop without news still releases a patch
        (["docs: d", "fix: f"], "0.2.1"),
        (["fix: f", "feat(cli): x"], "0.3.0"),
        (["feat!: x"], "0.3.0"),  # breaking raises the minor while 0.x
        (["fix: f\n\nBREAKING CHANGE: gone"], "0.3.0"),
    ],
)
def test_next_release(repo, messages, expected):
    commit, _ = repo
    for message in messages:
        commit(message)
    assert version.next_release(version.last_release()) == expected


def test_last_release_skips_pre_release_tags(repo):
    commit, git = repo
    commit("fix: f")
    git("tag", "v0.2.1a0")
    assert version.last_release() == "0.2.0"
    assert version.tagged("0.2.0") and not version.tagged("0.2.1")


def test_parse():
    assert version.parse("0.2.1a0") == (0, 2, 1, "a")
    assert version.parse("1.0.0") == (1, 0, 0, None)
    with pytest.raises(SystemExit):
        version.parse("1.0")


def test_hook_and_tasks_use_it():
    hooks = yaml.safe_load((ROOT / "lefthook.yml").read_text())
    assert "scripts/version.py mark" in hooks["post-merge"]["commands"]["pre-release"]["run"]
    flow = (ROOT / ".github" / "workflows" / "flow.yml").read_text()
    assert "scripts/version.py final" in flow
