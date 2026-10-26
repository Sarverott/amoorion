"""Secrets: passwords and tokens come from a vault, `.env` only links to it."""

from amoorion.vault.base import BACKENDS, Vault, VaultLink, open_vault
from amoorion.vault.default import EnvVault

__all__ = ["BACKENDS", "EnvVault", "Vault", "VaultLink", "open_vault"]
