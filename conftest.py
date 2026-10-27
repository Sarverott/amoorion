"""For every test but the live ones: the inbox and the dataset in a temporary place, never the user's."""

import pytest


@pytest.fixture(autouse=True)
def _local_data(request, tmp_path, monkeypatch):
    if request.node.get_closest_marker("live") is None:
        monkeypatch.setenv("AMOORION_INBOX", str(tmp_path / "inbox.sqlite3"))
        monkeypatch.setenv("AMOORION_DATASET", str(tmp_path / "dataset"))
