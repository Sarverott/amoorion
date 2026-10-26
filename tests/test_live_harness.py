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
    assert "dryrun: posted" in printed and "dryrun: replied" in printed


def test_platform_not_named_is_skipped(monkeypatch):
    monkeypatch.setenv("AMOORION_LIVE", "bluesky")
    with pytest.raises(pytest.skip.Exception):
        live.test_live("dryrun", open_vault(VaultLink(kind="env")))


def test_every_platform_but_dryrun_has_a_live_test():
    assert "dryrun" not in live.platforms() and {"bluesky", "discord", "matrix", "telegram"} <= set(live.platforms())
