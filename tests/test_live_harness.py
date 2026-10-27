"""The live test itself, run on dryrun, so it is known to work before it posts anywhere real."""

import importlib.util
from pathlib import Path

import pytest

from amoorion.vault import VaultLink, open_vault

spec = importlib.util.spec_from_file_location("live", Path(__file__).parent / "live" / "test_live.py")
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


def test_live_flow_on_dryrun(monkeypatch, capsys):
    monkeypatch.setenv("AMOORION_LIVE", "dryrun, other")
    live.test_live("dryrun", open_vault(VaultLink(kind="env")))
    printed = capsys.readouterr().out
    assert "dryrun: posted" in printed and "dryrun: replied" in printed and "dryrun: deleted" in printed


def test_platform_not_named_is_skipped(monkeypatch):
    monkeypatch.setenv("AMOORION_LIVE", "bluesky")
    with pytest.raises(pytest.skip.Exception):
        live.test_live("dryrun", open_vault(VaultLink(kind="env")))


def test_every_platform_but_dryrun_has_a_live_test():
    assert "dryrun" not in live.platforms() and {"bluesky", "discord", "matrix", "telegram"} <= set(live.platforms())


def test_connect_on_dryrun(monkeypatch, capsys):
    monkeypatch.delenv("AMOORION_LIVE", raising=False)
    live.test_connect("dryrun", open_vault(VaultLink(kind="env")))
    assert "dryrun: profile default" in capsys.readouterr().out


def test_without_names_a_platform_without_secrets_is_skipped(monkeypatch):
    monkeypatch.delenv("AMOORION_LIVE", raising=False)
    monkeypatch.delenv("AMOORION_SECRET_BLUESKY_USERNAME", raising=False)
    with pytest.raises(pytest.skip.Exception, match="secrets missing"):
        live.test_connect("bluesky", open_vault(VaultLink(kind="env")))


def test_named_without_secrets_fails(monkeypatch):
    monkeypatch.setenv("AMOORION_LIVE", "bluesky")
    monkeypatch.delenv("AMOORION_SECRET_BLUESKY_USERNAME", raising=False)
    with pytest.raises(pytest.fail.Exception, match="secrets missing"):
        live.test_connect("bluesky", open_vault(VaultLink(kind="env")))
