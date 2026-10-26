"""Shared by the tests of amoorion and of every plugin package."""

import pytest


@pytest.fixture(autouse=True)
def inbox_in_tmp(tmp_path, monkeypatch):
    """No test writes into the real inbox."""
    monkeypatch.setenv("AMOORION_INBOX", str(tmp_path / "inbox.sqlite3"))
