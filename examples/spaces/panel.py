"""What both web apps show: amoorion on the dryrun platform, nothing goes anywhere."""

from amoorion import Amoorion

# A public Space must never hold real accounts: a sandbox, and only dryrun.
amo = Amoorion().use("dryrun")


def post(text: str) -> list[list[str]]:
    """Publish and read back; rows of (id, text), newest first."""

    if text.strip():
        amo.publish(text=text)

    return [[message["id"], message["text"]] for message in amo.read(limit=20)]
