import pytest

from amoorion.core import AmoorionError
from amoorion.vault import EnvVault, VaultLink, open_vault


def test_link_from_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("AMOORION_VAULT", raising=False)
    monkeypatch.delenv("AMOORION_VAULT_ADDR", raising=False)
    env = tmp_path / ".env"
    env.write_text("AMOORION_VAULT=env\nAMOORION_VAULT_ADDR=https://vault.test\n")
    link = VaultLink.from_env(env)
    assert link.kind == "env" and link.addr == "https://vault.test"


def test_env_vault_reads_named_secret(monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_BLUESKY_APP_PASSWORD", "s3cret")
    vault = open_vault(VaultLink(kind="env"))
    assert isinstance(vault, EnvVault)
    assert vault.get("bluesky/app-password") == "s3cret"


def test_missing_secret_names_the_variable(monkeypatch):
    monkeypatch.delenv("AMOORION_SECRET_X_TOKEN", raising=False)
    with pytest.raises(AmoorionError, match="AMOORION_SECRET_X_TOKEN"):
        open_vault(VaultLink(kind="env")).get("x/token")


def test_unknown_backend():
    with pytest.raises(AmoorionError):
        open_vault(VaultLink(kind="nope"))
