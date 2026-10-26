"""Secrets: passwords and tokens come from a vault, `.env` only links to it."""

from amoorion.vault.base import EnvVault, Vault, VaultLink, open_vault

__all__ = ["EnvVault", "Vault", "VaultLink", "open_vault"]
