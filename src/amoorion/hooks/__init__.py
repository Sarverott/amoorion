"""Incoming webhooks: services tell amoorion that something happened."""

from amoorion.hooks.base import HOOKS, Forbidden, Hook, schema
from amoorion.hooks.discord import DiscordHook
from amoorion.hooks.generic import GenericHook
from amoorion.hooks.github import GitHubHook
from amoorion.hooks.gitlab import GitLabHook
from amoorion.hooks.plane import PlaneHook
from amoorion.hooks.sentry import SentryHook

__all__ = [
    "HOOKS",
    "DiscordHook",
    "Forbidden",
    "GenericHook",
    "GitHubHook",
    "GitLabHook",
    "Hook",
    "PlaneHook",
    "SentryHook",
    "schema",
]
