"""Two identities side by side, each with its own KeePassXC file, inbox and dataset."""

import tempfile
from pathlib import Path

from pykeepass import PyKeePass

from amoorion import Amoorion
from amoorion.plugins import load_plugins
from amoorion.vault import VaultLink
from amoorion.vault.kpxc_db_file import initialize

scratch = Path(tempfile.mkdtemp())
schemas = {"ntfy": load_plugins().get("ntfy").schema()}


def identity(name: str, topic: str | None) -> Amoorion:
    """Its env file holds a throwaway master password; a real one stays out of examples."""
    file, env = scratch / f"{name}.kdbx", scratch / f"{name}.env"
    initialize(VaultLink(kind="keepassxc", path=str(file), token="example"), schemas)
    if topic:
        db = PyKeePass(file, password="example")
        db.find_entries(title="ntfy", first=True).set_custom_property("topic", topic)
        db.save()
    env.write_text(f"AMOORION_VAULT=keepassxc\nAMOORION_VAULT_PATH={file}\nAMOORION_VAULT_TOKEN=example\nAMOORION_INBOX={scratch}/{name}.sqlite3\n")
    return Amoorion(env, scratch / f"{name}-dataset")


work, private = identity("work", "work-news"), identity("private", None)
for label, amo in (("work", work), ("private", private)):
    ready = next(status["ready"] for status in amo.accounts() if status["platform"] == "ntfy")
    print(label, "can use ntfy:", ready, "| inbox:", amo.store.path.name)
