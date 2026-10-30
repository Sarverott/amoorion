"""keepassxc backend: a KeePassXC (KeePass 2, .kdbx) database file.

    AMOORION_VAULT=keepassxc
    AMOORION_VAULT_PATH=/path/to/secrets.kdbx
    AMOORION_VAULT_TOKEN=<master password>

Secret `bluesky/password` is the entry titled `bluesky` in the group
`amoorion`: keys `username`, `password`, `url` and `notes` are the entry's
standard fields, any other key an additional attribute of that name.
The database is opened read-only, once per process. Only `initialize`
(`task vault:new`) writes, and it only adds what is missing.
"""

import shutil
from pathlib import Path
from typing import Any, ClassVar

from pykeepass import PyKeePass, create_database
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


def initialize(link: VaultLink, schemas: dict[str, dict[str, Any]]) -> list[str]:
    """Make the file if it is missing and an empty entry per schema; return what was added.

    A value already there is never changed. An existing file is copied to
    `<file>.bak` before it is changed.
    """
    if not link.path:
        raise AmoorionError("the keepassxc vault needs AMOORION_VAULT_PATH (the .kdbx file)")
    if not link.token:
        raise AmoorionError("the keepassxc vault needs AMOORION_VAULT_TOKEN (the master password)")
    file = Path(link.path).expanduser()
    added: list[str] = []
    existed = file.exists()
    if existed:
        try:
            db = PyKeePass(file, password=link.token)
        except CredentialsError:
            raise AmoorionError(f"wrong master password for {link.path}") from None
    else:
        file.parent.mkdir(parents=True, exist_ok=True)
        db = create_database(str(file), password=link.token)
        added.append(str(file))
    group = db.find_groups(name=PREFIX, first=True)
    if group is None:
        group = db.add_group(db.root_group, PREFIX)
        added.append(f"group {PREFIX}")
    for platform, schema in sorted(schemas.items()):
        keys = {**schema["scopes"], **schema["optional"]}
        entry = db.find_entries(title=platform, group=group, recursive=False, first=True)
        if entry is None:
            entry = db.add_entry(group, platform, "", "")
            added.append(f"entry {platform}")
        missing = [key for key in keys if key not in STANDARD_KEYS and key not in entry.custom_properties]
        for key in missing:
            entry.set_custom_property(key, "")
            added.append(f"{platform}/{key}")
        if not entry.notes:
            lines = [f"{key}: {text}" for key, text in schema["scopes"].items()]
            lines += [f"{key} (optional): {text}" for key, text in schema["optional"].items()]
            entry.notes = "\n".join([schema["description"], "", *lines])
            added.append(f"{platform}: notes")
    if added:
        if existed:
            shutil.copy2(file, file.with_name(file.name + ".bak"))
        db.save()
        file.chmod(0o600)  # saving writes the file anew
    return added
