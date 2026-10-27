"""The bitwarden backend against a fake `bw` that answers like the real one."""

import json
import sys

import pytest

from amoorion.core import AmoorionError
from amoorion.vault import BitwardenVault, VaultLink, open_vault

ITEMS = [
    {
        "name": "amoorion/bluesky",
        "login": {"username": "me.bsky.social", "password": "app-pass", "uris": [{"uri": "https://bsky.social"}]},
        "fields": [{"name": "handle", "value": "@me", "type": 0}],
        "notes": None,
    },
    {"name": "amoorion/bluesky-old", "login": {"password": "old"}},
]

FAKE_BW = """#!{python}
import json, os, sys
args = sys.argv[1:]
assert args[0] == "--nointeraction", args
args = args[1:]
with open({log!r}, "a") as log:
    log.write(" ".join(args) + "\\n")
if os.environ.get("BW_SESSION") != "sess":
    print(json.dumps({{"status": "locked", "serverUrl": "https://vault.test"}}))
elif args[0] == "status":
    print(json.dumps({{"status": "unlocked", "serverUrl": "https://vault.test/"}}))
elif args[:2] == ["list", "items"]:
    term = args[args.index("--search") + 1]
    print(json.dumps([item for item in {items!r} if term in item["name"]]))
else:
    print("unknown command", file=sys.stderr)
    sys.exit(1)
"""


@pytest.fixture
def fake_bw(tmp_path, monkeypatch):
    log = tmp_path / "calls.log"
    bw = tmp_path / "bin" / "bw"
    bw.parent.mkdir()
    bw.write_text(FAKE_BW.format(python=sys.executable, log=str(log), items=ITEMS))
    bw.chmod(0o755)
    monkeypatch.setenv("PATH", str(bw.parent))
    return log


def vault(**link):
    return open_vault(VaultLink(kind="bitwarden", **({"token": "sess"} | link)))


def test_login_custom_field_and_uri(fake_bw):
    bitwarden = vault(addr="https://vault.test")
    assert isinstance(bitwarden, BitwardenVault)
    assert bitwarden.get("bluesky/password") == "app-pass"
    assert bitwarden.get("bluesky/username") == "me.bsky.social"
    assert bitwarden.get("bluesky/handle") == "@me"
    assert bitwarden.get("bluesky/uri") == "https://bsky.social"
    # status checked once, the item fetched once
    assert fake_bw.read_text().splitlines() == ["status", "list items --search amoorion/bluesky"]


def test_session_never_on_the_command_line(fake_bw):
    vault().get("bluesky/password")
    assert "sess" not in fake_bw.read_text()


def test_locked_vault(fake_bw):
    with pytest.raises(AmoorionError, match="locked"):
        vault(token="wrong").get("bluesky/password")


def test_other_server_refused(fake_bw):
    with pytest.raises(AmoorionError, match="not to https://other.test"):
        vault(addr="https://other.test").get("bluesky/password")


def test_missing_item_and_key(fake_bw):
    with pytest.raises(AmoorionError, match="0 items"):
        vault().get("telegram/token")
    with pytest.raises(AmoorionError, match="'bluesky/totp' not found"):
        vault().get("bluesky/totp")


def test_custom_prefix(fake_bw):
    with pytest.raises(AmoorionError, match="'team/bluesky'"):
        vault(path="team").get("bluesky/password")


def test_no_bw_on_path(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.delenv("AMOORION_BW", raising=False)
    monkeypatch.chdir(tmp_path)  # no tools/node_modules/.bin/bw here
    with pytest.raises(AmoorionError, match="not on PATH"):
        vault().get("bluesky/password")


def test_bw_from_npm_in_tools(tmp_path, monkeypatch):
    from amoorion.vault.bw_cli import NPM_BW, find_bw

    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    monkeypatch.delenv("AMOORION_BW", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / NPM_BW).parent.mkdir(parents=True)
    (tmp_path / NPM_BW).write_text("#!/bin/sh\n")
    assert find_bw() == str(tmp_path / NPM_BW)
    monkeypatch.setenv("AMOORION_BW", "/opt/bw")
    assert find_bw() == "/opt/bw"
