"""scripts/vault.sh with KeePassXC, in a copy of the repository's layout: never the real .env."""

import shutil
import subprocess
from pathlib import Path

import pytest
from pykeepass import PyKeePass

ROOT = Path(__file__).parents[1]
ENV = "AMOORION_VAULT=keepassxc\nAMOORION_VAULT_PATH=./data/secrets.kdbx\nAMOORION_VAULT_TOKEN=master\n"


@pytest.fixture
def run(tmp_path):

    (tmp_path / "scripts").mkdir()

    shutil.copy(
        ROOT / "scripts/vault.sh",
        tmp_path / "scripts",
    )

    (tmp_path / ".venv").symlink_to(ROOT / ".venv")

    (tmp_path / ".env").write_text(ENV)

    def run(command):

        return subprocess.run(
            [
                "scripts/vault.sh",
                command,
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    return run


def test_new_makes_an_empty_entry_per_platform(
    run,
    tmp_path,
):

    assert "no " in run("status").stdout

    made = run("new")

    assert made.returncode == 0, made.stderr

    file = tmp_path / "data/secrets.kdbx"

    assert file.stat().st_mode & 0o777 == 0o600

    db = PyKeePass(
        file,
        password="master",
    )

    x = db.find_entries(
        title="x",
        first=True,
    )

    assert x.group.name == "amoorion"

    assert {"api-key", "uri"} <= set(
        x.custom_properties
    ) and not x.get_custom_property("api-key")

    assert "api-key: " in x.notes and "uri (optional): " in x.notes

    assert db.find_entries(title="discord-webhook", first=True) is not None

    assert db.find_entries(title="dryrun", first=True) is None

    assert {"github-secret", "gitlab-token", "discord-public-key"} <= set(
        db.find_entries(title="hooks", first=True).custom_properties
    )


def test_new_again_changes_nothing_and_keeps_values(
    run,
    tmp_path,
):

    run("new")

    file = tmp_path / "data/secrets.kdbx"

    db = PyKeePass(
        file,
        password="master",
    )

    x = db.find_entries(
        title="x",
        first=True,
    )

    x.set_custom_property(
        "api-key",
        "kept",
    )

    x.notes = "mine"

    db.find_entries(title="bluesky", first=True).password = "kept too"

    db.delete_entry(
        db.find_entries(
            title="matrix",
            first=True,
        )
    )

    db.save()

    assert (
        "added entry matrix," in run("new").stdout
    )  # a new package's entry comes in later

    db = PyKeePass(
        file,
        password="master",
    )

    assert (
        db.find_entries(title="x", first=True).get_custom_property("api-key")
        == "kept"
    )

    assert db.find_entries(title="x", first=True).notes == "mine"

    assert db.find_entries(title="bluesky", first=True).password == "kept too"

    assert (tmp_path / "data/secrets.kdbx.bak").exists()

    before = file.read_bytes()

    assert "nothing to add" in run("new").stdout

    assert file.read_bytes() == before


def test_a_wrong_password_is_told_and_never_shown(
    run,
    tmp_path,
):

    run("new")

    (tmp_path / ".env").write_text(
        ENV.replace(
            "=master",
            "=wrong",
        )
    )

    done = run("status")

    assert done.returncode != 0 and "not its master password" in done.stderr

    assert "=wrong" not in done.stdout + done.stderr


def test_login_and_lock_leave_env_alone(
    run,
    tmp_path,
):

    for command in ("login", "lock"):
        assert "no session" in run(command).stdout

    assert (tmp_path / ".env").read_text() == ENV
