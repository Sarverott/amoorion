"""Secrets: passwords and tokens come from a vault, `.env` only links to it."""

from amoorion.vault.base import BACKENDS, Vault, VaultLink, open_vault
from amoorion.vault.bw_cli import BitwardenVault
from amoorion.vault.default import EnvVault
from amoorion.vault.http_vault import HttpVault
from amoorion.vault.kpxc_db_file import KeePassXCVault

__all__ = [
    "BACKENDS",
    "BitwardenVault",
    "EnvVault",
    "HttpVault",
    "KeePassXCVault",
    "Vault",
    "VaultLink",
    "open_vault",
]
