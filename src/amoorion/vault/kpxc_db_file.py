"""keepassxc backend: a KeePassXC (KeePass 2, .kdbx) database file.

    AMOORION_VAULT=keepassxc
    AMOORION_VAULT_PATH=/path/to/secrets.kdbx
    AMOORION_VAULT_TOKEN=<master password>

Secret `bluesky/password` is the entry titled `bluesky` in the group
`amoorion`: keys `username`, `password`, `url` and `notes` are the entry's
standard fields, any other key an additional attribute of that name.
The database is opened read-only, once per process.
"""

from pathlib import Path
from typing import Any, ClassVar

from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError

from amoorion.core import AmoorionError
from amoorion.vault.base import BACKENDS, PREFIX, Vault, VaultLink

STANDARD_KEYS = ("username", "password", "url", "notes")


@BACKENDS.register
class KeePassXCVault(Vault):
    name: ClassVar[str] = "keepassxc"
    description: ClassVar[str] = "KeePassXC database file (.kdbx)"

    def __init__(self, link: VaultLink) -> None:
        super().__init__(link)
        if not link.path:
            raise AmoorionError("the keepassxc vault needs AMOORION_VAULT_PATH (the .kdbx file)")
        self._db: Any = None

    def _open(self) -> Any:
        if self._db is None:
            try:
                self._db = PyKeePass(Path(self.link.path).expanduser(), password=self.link.token)
            except FileNotFoundError:
                raise AmoorionError(f"no KeePassXC database at {self.link.path}: `task vault:new` makes it") from None
            except CredentialsError:
                raise AmoorionError(f"wrong master password for {self.link.path}") from None
        return self._db

    def get(self, name: str) -> str:
        platform, key = self.split(name)
        db = self._open()
        group = db.find_groups(name=PREFIX, first=True)
        entry = db.find_entries(title=platform, group=group, recursive=False, first=True) if group else None
        if entry is None:
            raise AmoorionError(f"KeePassXC has no entry {PREFIX}/{platform}")
        value = getattr(entry, key) if key in STANDARD_KEYS else entry.get_custom_property(key)
        if not value:
            raise AmoorionError(f"secret {name!r} not found in KeePassXC")
        return value
