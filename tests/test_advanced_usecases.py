"""Every advanced use case and the web apps' shared part still run (dryrun and fakes)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[1] / "examples"


@pytest.mark.parametrize("path", sorted((EXAMPLES / "advanced-usecases").glob("*/run.py")), ids=lambda path: path.parent.name)
def test_use_case_runs(path, tmp_path):
    env = {key: value for key, value in os.environ.items() if not key.startswith("AMOORION_")}
    done = subprocess.run([sys.executable, str(path)], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip()


def test_every_directory_has_its_use_case():
    directories = [path for path in (EXAMPLES / "advanced-usecases").iterdir() if path.is_dir()]
    assert len(directories) >= 6 and all((path / "run.py").is_file() for path in directories)


def test_the_web_apps_post_on_dryrun_only(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(EXAMPLES / "spaces"))
    monkeypatch.setenv("AMOORION_VAULT", "env")
    monkeypatch.chdir(tmp_path)
    import panel

    assert panel.amo.used == ["dryrun"]
    assert panel.post("hello")[0][1] == "hello"
