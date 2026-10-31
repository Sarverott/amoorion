"""States of an `Amoorion`: where things are and hashes to detect changes, never a secret."""

import hashlib
from pathlib import Path
from typing import Self

import yaml


def _sha(data: bytes) -> str:

    return hashlib.sha256(data).hexdigest()


class States:
    def hashes(self) -> dict[str, str]:
        """What now is, as hashes. Of the link only its public parts: a hash of a password can be guessed at."""

        link = self.link

        indexes = (
            sorted(self.dataset.path.glob("*/*/index.json"))
            if self.dataset.path.is_dir()
            else []
        )

        inbox = self.store.path

        return {
            "vault": _sha(f"{link.kind}|{link.addr}|{link.path}".encode()),
            "dataset": _sha(
                b"".join(
                    str(file.relative_to(self.dataset.path)).encode()
                    + file.read_bytes()
                    for file in indexes
                )
            ),
            "inbox": _sha(inbox.read_bytes() if inbox.is_file() else b""),
        }

    def changes(self) -> list[str]:
        """What differs from the last `load` or `save`."""

        now = self.hashes()

        return [
            name
            for name, value in now.items()
            if self._hashes.get(name) != value
        ]

    def save(
        self,
        path: str | Path,
    ) -> Self:
        """Write where things are and their hashes as YAML. No secret goes there."""

        self._hashes = self.hashes()

        state = {
            "env": str(self.env) if self.env else None,
            "dataset": str(self._dataset_path) if self._dataset_path else None,
            "flags": self.flags,
            "plugins": self.used,
            "hashes": self._hashes,
        }

        Path(path).expanduser().write_text(
            yaml.safe_dump(
                state,
                sort_keys=False,
            )
        )

        return self

    def load(
        self,
        path: str | Path,
    ) -> Self:
        """Take over what `save` wrote; `changes()` then tells what moved since."""

        state = yaml.safe_load(Path(path).expanduser().read_text()) or {}

        self._dataset_path = (
            Path(state["dataset"]) if state.get("dataset") else None
        )

        self._open(Path(state["env"]) if state.get("env") else None)

        self.flags = dict(state.get("flags") or {})

        self.used = []

        self.use(*(state.get("plugins") or []))

        self._hashes = dict(state.get("hashes") or {})

        return self
