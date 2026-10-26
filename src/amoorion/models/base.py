"""Platform-independent data: what a plugin takes and gives back."""

from datetime import datetime

from pydantic import Field

from amoorion.core import Model


class Account(Model):
    """Who speaks on a platform."""

    platform: str
    handle: str
    name: str | None = None


class Post(Model):
    """What to publish: written once, sent to any platform."""

    text: str = Field(min_length=1)
    title: str | None = None
    links: list[str] = []
    tags: list[str] = []


class Message(Model):
    """Something said on a platform: a published post, a chat line, a hook event."""

    platform: str
    text: str
    id: str | None = None
    url: str | None = None
    author: Account | None = None
    reply_to: str | None = None
    created_at: datetime | None = None


class Result(Model):
    """Outcome of one platform's part of a method."""

    platform: str
    ok: bool
    message: Message | None = None
    error: str | None = None
