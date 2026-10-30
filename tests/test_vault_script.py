"""scripts/vault.sh with KeePassXC, in a copy of the repository's layout: never the real .env."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
ENV = "AMOORION_VAULT=keepassxc\nAMOORION_VAULT_PATH=./data/secrets.kdbx\nAMOORION_VAULT_TOKEN=master\n"


@pytest.fixture
def run(tmp_path):
    (tmp_path / "scripts").mkdir()
    shutil.copy(ROOT / "scripts/vault.sh", tmp_path / "scripts")
    (tmp_path / ".venv").symlink_to(ROOT / ".venv")
    (tmp_path / ".env").write_text(ENV)

    def run(command):
        return subprocess.run(["scripts/vault.sh", command], cwd=tmp_path, capture_output=True, text=True, check=False)

    return run


def test_new_makes_the_file_and_never_overwrites(run, tmp_path):
    assert "no " in run("status").stdout
    made = run("new")
    assert made.returncode == 0, made.stderr
    file = tmp_path / "data/secrets.kdbx"
    assert file.stat().st_mode & 0o777 == 0o600
    assert "group amoorion: no entries" in run("status").stdout
    before = file.read_bytes()
    again = run("new")
    assert again.returncode != 0 and "stays" in again.stderr
    assert file.read_bytes() == before


def test_a_wrong_password_is_told_and_never_shown(run, tmp_path):
    run("new")
    (tmp_path / ".env").write_text(ENV.replace("=master", "=wrong"))
    done = run("status")
    assert done.returncode != 0 and "not its master password" in done.stderr
    assert "=wrong" not in done.stdout + done.stderr


def test_login_and_lock_leave_env_alone(run, tmp_path):
    for command in ("login", "lock"):
        assert "no session" in run(command).stdout
    assert (tmp_path / ".env").read_text() == ENV
