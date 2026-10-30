"""Dataset: what amoorion knows of the posts on each platform, as JSON files (decision Q14).

Every profile (the account, page, blog, channel, chat or room a plugin
speaks as or in) has its own directory with an index:

    dataset/<platform>/<profile>/index.json        every post known: id, url, time, state
    dataset/<platform>/<profile>/posts/<id>.json   each post as last read
    dataset/<platform>/<profile>/deleted/<id>.json what `delete` removed, kept before it went

A post is `present` (seen by the last read that saw it), `gone` (not there
any more when a read covered all posts) or `deleted` (by amoorion). Where
it lives is set in `.env` (`dataset/` is ignored by git):

    AMOORION_DATASET=<path>   default: ./dataset
"""

import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from amoorion.dataset.entry import Entry, safe
from amoorion.models import Message


def default_path() -> Path:
    load_dotenv(Path.cwd() / ".env", override=False)
    return Path(os.environ.get("AMOORION_DATASET") or "dataset").expanduser()


class Dataset:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_path()

    def profile_dir(self, platform: str, profile: str) -> Path:
        return self.path / safe(platform) / safe(profile)

    def index(self, platform: str, profile: str) -> dict[str, Entry]:
        file = self.profile_dir(platform, profile) / "index.json"
        if not file.exists():
            return {}
        return {entry["id"]: Entry.model_validate(entry) for entry in json.loads(file.read_text())["posts"]}

    def _write_index(self, platform: str, profile: str, entries: dict[str, Entry]) -> None:
        directory = self.profile_dir(platform, profile)
        directory.mkdir(parents=True, exist_ok=True)
        ordered = sorted(entries.values(), key=lambda e: (e.created_at or e.seen_at or datetime.min.replace(tzinfo=UTC)), reverse=True)
        body = {
            "platform": platform,
            "profile": profile,
            "updated_at": datetime.now(UTC).isoformat(),
            "posts": [entry.model_dump(mode="json") for entry in ordered],
        }
        (directory / "index.json").write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n")

    def _write(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n")

    def record(self, platform: str, profile: str, messages: Iterable[Message], complete: bool = False) -> list[Message]:
        """Keep what a read saw. `complete`: the read covered every post, so the ones not seen are gone."""
        messages = [message for message in messages if message.id]
        entries = self.index(platform, profile)
        now = datetime.now(UTC)
        directory = self.profile_dir(platform, profile)
        for message in messages:
            name = f"posts/{safe(message.id)}.json"
            self._write(directory / name, message.model_dump(mode="json"))
            before = entries.get(message.id)
            entries[message.id] = Entry(
                id=message.id,
                file=name,
                url=message.url,
                created_at=message.created_at,
                text=message.text[:140],
                seen_at=now,
                deleted_at=before.deleted_at if before else None,
            )
        if complete:
            seen = {message.id for message in messages}
            for entry in entries.values():
                if entry.id not in seen and entry.state == "present":
                    entry.state = "gone"
        self._write_index(platform, profile, entries)
        return messages

    def find(self, platform: str, profile: str, id: str) -> Message | None:
        entry = self.index(platform, profile).get(id)
        file = self.profile_dir(platform, profile) / entry.file if entry else None
        if not file or not file.exists():
            return None
        data = json.loads(file.read_text())
        data.pop("deleting_at", None)  # keep_deleted's own note, not part of the message
        return Message.model_validate(data)

    def keep_deleted(self, platform: str, profile: str, message: Message) -> Path:
        """Keep what is about to be deleted; call before deleting it on the platform."""
        file = self.profile_dir(platform, profile) / "deleted" / f"{safe(message.id or 'unknown')}.json"
        self._write(file, message.model_dump(mode="json") | {"deleting_at": datetime.now(UTC).isoformat()})
        return file

    def deleted(self, platform: str, profile: str, message: Message) -> None:
        """Mark a post deleted in the index, after the platform deleted it."""
        entries = self.index(platform, profile)
        now = datetime.now(UTC)
        entry = entries.get(message.id) or Entry(
            id=message.id, file=f"deleted/{safe(message.id)}.json", url=message.url, created_at=message.created_at, text=message.text[:140]
        )
        entry.state, entry.deleted_at, entry.file = "deleted", now, f"deleted/{safe(message.id)}.json"
        entries[message.id] = entry
        self._write_index(platform, profile, entries)
