"""Incoming webhooks: services tell amoorion that something happened."""

from amoorion.hooks.base import HOOKS, Forbidden, GenericHook, Hook, schema
from amoorion.hooks.discord import DiscordHook
from amoorion.hooks.github import GitHubHook
from amoorion.hooks.gitlab import GitLabHook

__all__ = ["HOOKS", "DiscordHook", "Forbidden", "GenericHook", "GitHubHook", "GitLabHook", "Hook", "schema"]
