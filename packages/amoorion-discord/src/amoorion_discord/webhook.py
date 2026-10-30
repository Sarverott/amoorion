"""discord-webhook plugin: a channel webhook, no bot.

Secret: `url`, the channel's webhook URL; it posts, and deletes what it posted.
"""

from typing import ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Message, Post
from amoorion.plugins import Capability, HttpPlugin

from amoorion_discord.text import NO_PINGS, checked, compose, message


class DiscordWebhook(HttpPlugin):
    name: ClassVar[str] = "discord-webhook"
    description: ClassVar[str] = "Discord channel webhook, no bot: post, delete what it posted"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST, Capability.DELETE})
    secrets: ClassVar[tuple[str, ...]] = ("url",)

    def hidden(self) -> list[str]:
        # .../webhooks/<id>/<token>: the token is the secret part.
        return [self.secret("url").rstrip("/").rsplit("/", 1)[-1]]

    def post(self, post: Post) -> Message:
        body = {"content": checked(compose(post))} | NO_PINGS
        # wait=true: Discord answers with the message instead of nothing.
        sent = self.request("POST", self.secret("url"), params={"wait": "true"}, json=body)
        return message(self.name, sent, sent.get("guild_id"))

    def delete(self, message: Message) -> None:
        if not message.id:
            raise AmoorionError("discord-webhook needs the id of the message to delete")
        self.request("DELETE", f"{self.secret('url').rstrip('/')}/messages/{message.id}")

    def profile(self) -> str:
        # .../webhooks/<id>/<token>: the id names it, the token stays secret.
        return "webhook-" + self.secret("url").rstrip("/").rsplit("/", 2)[-2]
