"""ntfy plugin: push notifications to one topic.

Secrets (`ntfy/<key>`): `topic`; optional `uri` (the server, default
https://ntfy.sh) and `token` (for protected topics). A topic on a public
server is readable by anyone who knows its name, so pick a long one.
"""

import json
from datetime import UTC, datetime
from typing import Any, ClassVar

import requests

from amoorion.core import AmoorionError
from amoorion.models import Message, Post
from amoorion.plugins import Capability, HttpPlugin

SERVER = "https://ntfy.sh"


class Ntfy(HttpPlugin):
    name: ClassVar[str] = "ntfy"
    description: ClassVar[str] = "ntfy: push notifications to one topic, and read them"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST, Capability.READ})
    secrets: ClassVar[tuple[str, ...]] = ("topic",)

    def _optional(self, key: str) -> str | None:
        try:
            return self.secret(key)
        except AmoorionError:
            return None

    @property
    def server(self) -> str:
        return (self._optional("uri") or SERVER).rstrip("/")

    def _headers(self) -> dict[str, str]:
        token = self._optional("token")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _message(self, event: dict[str, Any]) -> Message:
        return Message(
            platform=self.name,
            text=event.get("message", ""),
            id=event.get("id"),
            url=event.get("click"),
            created_at=datetime.fromtimestamp(event["time"], UTC) if "time" in event else None,
        )

    def post(self, post: Post) -> Message:
        body: dict[str, Any] = {"topic": self.secret("topic"), "message": post.text}
        if post.title:
            body["title"] = post.title
        if post.tags:
            body["tags"] = [tag.lstrip("#") for tag in post.tags]
        if post.links:
            body["click"] = post.links[0]
            if extra := post.links[1:]:
                body["message"] += "\n" + "\n".join(extra)
        return self._message(self.request("POST", self.server, json=body, headers=self._headers()))

    def read(self, limit: int = 20) -> list[Message]:
        url = f"{self.server}/{self.secret('topic')}/json"
        try:
            response = requests.get(
                url, params={"poll": "1", "since": "all"}, headers=self._headers(), timeout=self.timeout
            )
        except requests.RequestException as error:
            raise self._error(f"{self.name} unreachable: {error}") from None
        if not response.ok:
            raise self._error(f"{self.name} answered {response.status_code}: {self.reason(response)}")
        # One JSON object per line, oldest first.
        events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
        messages = [self._message(event) for event in events if event.get("event") == "message"]
        return messages[-limit:][::-1]

    def profile(self) -> str:
        return self.secret("topic")
