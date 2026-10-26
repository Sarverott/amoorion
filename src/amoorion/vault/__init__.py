"""Secrets: passwords and tokens come from a vault, `.env` only links to it."""

from amoorion.vault.base import BACKENDS, Vault, VaultLink, open_vault
from amoorion.vault.bw_cli import BitwardenVault
from amoorion.vault.default import EnvVault

__all__ = ["BACKENDS", "BitwardenVault", "EnvVault", "Vault", "VaultLink", "open_vault"]
