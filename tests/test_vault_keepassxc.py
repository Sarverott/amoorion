"""The keepassxc backend against a real .kdbx made for the test."""

import pytest
from pykeepass import create_database

from amoorion.core import AmoorionError
from amoorion.vault import KeePassXCVault, VaultLink, open_vault


@pytest.fixture
def kdbx(tmp_path):
    path = tmp_path / "secrets.kdbx"
    db = create_database(str(path), password="master")
    group = db.add_group(db.root_group, "amoorion")
    entry = db.add_entry(group, "bluesky", "me.bsky.social", "app-pass", url="https://bsky.social")
    entry.set_custom_property("handle", "@me")
    db.add_entry(db.root_group, "telegram", "bot", "outside-the-group")
    db.save()
    return str(path)


def test_standard_and_custom_keys(kdbx):
    vault = open_vault(VaultLink(kind="keepassxc", path=kdbx, token="master"))
    assert isinstance(vault, KeePassXCVault)
    assert vault.get("bluesky/password") == "app-pass"
    assert vault.get("bluesky/username") == "me.bsky.social"
    assert vault.get("bluesky/url") == "https://bsky.social"
    assert vault.get("bluesky/handle") == "@me"


def test_only_entries_of_the_amoorion_group(kdbx):
    with pytest.raises(AmoorionError, match="no entry amoorion/telegram"):
        open_vault(VaultLink(kind="keepassxc", path=kdbx, token="master")).get("telegram/password")


def test_missing_key(kdbx):
    with pytest.raises(AmoorionError, match="'bluesky/notes' not found"):
        open_vault(VaultLink(kind="keepassxc", path=kdbx, token="master")).get("bluesky/notes")


def test_wrong_password_and_missing_file(kdbx, tmp_path):
    with pytest.raises(AmoorionError, match="wrong master password"):
        open_vault(VaultLink(kind="keepassxc", path=kdbx, token="nope")).get("bluesky/password")
    with pytest.raises(AmoorionError, match="no KeePassXC database"):
        open_vault(VaultLink(kind="keepassxc", path=str(tmp_path / "none.kdbx"), token="x")).get("bluesky/password")


def test_needs_path():
    with pytest.raises(AmoorionError, match="AMOORION_VAULT_PATH"):
        open_vault(VaultLink(kind="keepassxc"))
