"""Two identities side by side, each with its own KeePassXC file, inbox and dataset."""

import tempfile
from pathlib import Path

from pykeepass import PyKeePass

from amoorion import Amoorion
from amoorion.plugins import load_plugins
from amoorion.vault import VaultLink
from amoorion.vault.kpxc_db_file import initialize

# A folder for the env and vault files of both identities.
scratch = Path(tempfile.mkdtemp())
# What a new vault gets an empty entry for.
schemas = {"ntfy": load_plugins().get("ntfy").schema()}


def identity(
    name: str,
    topic: str | None,
) -> Amoorion:
    """Its env file holds a throwaway master password; a real one stays out of examples."""

    file, env = scratch / f"{name}.kdbx", scratch / f"{name}.env"

    initialize(
        VaultLink(
            kind="keepassxc",
            path=str(file),
            token="example",
        ),
        schemas,
    )

    if topic:
        db = PyKeePass(
            file,
            password="example",
        )

        db.find_entries(
            title="ntfy",
            first=True,
        ).set_custom_property(
            "topic",
            topic,
        )

        db.save()

    env.write_text(
        f"AMOORION_VAULT=keepassxc\nAMOORION_VAULT_PATH={file}\nAMOORION_VAULT_TOKEN=example\nAMOORION_INBOX={scratch}/{name}.sqlite3\n"
    )

    return Amoorion(
        env,
        scratch / f"{name}-dataset",
    )


# Only `work` gets a topic, so only it will be ready.
work, private = identity("work", "work-news"), identity("private", None)
# Neither sees the secrets of the other, in one process.
for label, amo in (("work", work), ("private", private)):
    ready = next(
        status["ready"]
        for status in amo.accounts()
        if status["platform"] == "ntfy"
    )
    print(
        label,
        "can use ntfy:",
        ready,
        "| inbox:",
        amo.store.path.name,
    )
