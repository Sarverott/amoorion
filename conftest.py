"""For every test but the live ones: the inbox and the dataset in a temporary place, and no vault of the
user's `.env` (a vault link read once would stay in os.environ, master password too, for the tests after it)."""

from pathlib import Path

import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def _local_data(request, tmp_path, monkeypatch):
    if request.node.get_closest_marker("live") is None:
        monkeypatch.setenv("AMOORION_INBOX", str(tmp_path / "inbox.sqlite3"))
        monkeypatch.setenv("AMOORION_DATASET", str(tmp_path / "dataset"))
        monkeypatch.setattr(
            "amoorion.vault.base.load_dotenv",
            lambda path, **kwargs: path != Path.cwd() / ".env" and load_dotenv(path, **kwargs),
        )
        for name in ("AMOORION_VAULT", "AMOORION_VAULT_ADDR", "AMOORION_VAULT_TOKEN", "AMOORION_VAULT_PATH"):
            monkeypatch.delenv(name, raising=False)
