"""matrix plugin: one room on a homeserver, through the client-server API.

Secrets (`matrix/<key>`): `uri` (the homeserver), `token` (the account's
access token), `room` (an id `!…:server` or an alias `#…:server`). Messages
are plain `m.text` events; encrypted rooms are not supported yet.
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_matrix.text import compose, part

API = "/_matrix/client/v3"
ONLY_MESSAGES = json.dumps({"types": ["m.room.message"]})


class Matrix(HttpPlugin):
    """One room of a Matrix server, through the client-server API.

    Deleting is called redacting there; the event stays, without its content.
    """

    name: ClassVar[str] = "matrix"
    description: ClassVar[str] = (
        "Matrix room (client-server API): post, read, reply, delete (redact)"
    )
    capabilities: ClassVar[frozenset[Capability]] = frozenset(Capability)
    secrets: ClassVar[tuple[str, ...]] = (
        "uri",
        "token",
        "room",
    )

    _room: str | None = None
    _me: str | None = None

    def _call(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """One authorized request to the platform's API; its address can be replaced by the `uri` secret."""

        headers = {"Authorization": f"Bearer {self.secret('token')}"}

        return self.request(
            method,
            f"{self.secret('uri').rstrip('/')}{API}{path}",
            headers=headers,
            **kwargs,
        )

    def _room_id(self) -> str:
        """The room's id, resolved once when the vault names its alias (`#…`)."""

        if self._room is None:
            room = self.secret("room")

            if room.startswith("#"):
                room = self._call("GET", f"/directory/room/{part(room)}")[
                    "room_id"
                ]

            self._room = room

        return self._room

    def _whoami(self) -> str:
        """The user of the token, asked once."""

        if self._me is None:
            self._me = self._call("GET", "/account/whoami")["user_id"]

        return self._me

    def _message(
        self,
        event: dict[str, Any],
    ) -> Message:
        """The platform's answer as a `Message`."""

        content = event.get("content") or {}

        reply = (content.get("m.relates_to") or {}).get("m.in_reply_to") or {}

        stamp = event.get("origin_server_ts")

        return Message(
            platform=self.name,
            text=content.get(
                "body",
                "",
            ),
            id=event["event_id"],
            url=f"https://matrix.to/#/{part(self._room_id())}/{part(event['event_id'])}",
            author=Account(
                platform=self.name,
                handle=event.get(
                    "sender",
                    "",
                ),
            ),
            reply_to=reply.get("event_id"),
            created_at=datetime.fromtimestamp(
                stamp / 1000,
                UTC,
            )
            if stamp
            else None,
        )

    def _send(
        self,
        text: str,
        reply_to: str | None = None,
    ) -> Message:
        """Send a text, optionally as a reply; answers the message."""

        content: dict[str, Any] = {
            "msgtype": "m.text",
            "body": text,
        }

        if reply_to:
            content["m.relates_to"] = {"m.in_reply_to": {"event_id": reply_to}}

        # A transaction id of our own: a retried request makes the server send only once.
        path = f"/rooms/{part(self._room_id())}/send/m.room.message/{uuid.uuid4().hex}"

        sent = self._call(
            "PUT",
            path,
            json=content,
        )

        event = {
            "event_id": sent["event_id"],
            "sender": self._whoami(),
            "content": content,
            "origin_server_ts": datetime.now(UTC).timestamp() * 1000,
        }

        return self._message(event)

    def post(
        self,
        post: Post,
    ) -> Message:
        """Publish a post; answers the message as the platform stored it."""

        return self._send(compose(post))

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:
        """The latest messages, newest first, at most `limit`."""

        params = {
            "dir": "b",
            "limit": min(
                limit,
                100,
            ),
            "filter": ONLY_MESSAGES,
        }

        chunk = self._call(
            "GET",
            f"/rooms/{part(self._room_id())}/messages",
            params=params,
        ).get(
            "chunk",
            [],
        )

        # A redacted (deleted) message stays in the timeline without its content.
        said = [
            event
            for event in chunk
            if event.get("type") == "m.room.message"
            and "body" in (event.get("content") or {})
        ]

        return [self._message(event) for event in said]

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:
        """Answer a message by its id; answers the new message."""

        if not to.id:
            raise AmoorionError("matrix needs the id of the event to reply to")

        return self._send(
            text,
            reply_to=to.id,
        )

    def delete(
        self,
        message: Message,
    ) -> None:
        """Redacts the event: its content is removed for everyone, the event stays as a gap."""

        if not message.id:
            raise AmoorionError("matrix needs the id of the event to delete")

        path = f"/rooms/{part(self._room_id())}/redact/{part(message.id)}/{uuid.uuid4().hex}"

        self._call(
            "PUT",
            path,
            json={"reason": "deleted by amoorion"},
        )

    def profile(self) -> str:
        """The name this account gets in the dataset."""

        return self.secret("room")
