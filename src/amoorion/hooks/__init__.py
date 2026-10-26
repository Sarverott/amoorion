"""Incoming webhooks: services tell amoorion that something happened."""

from amoorion.hooks.base import HOOKS, Forbidden, GenericHook, Hook

__all__ = ["HOOKS", "Forbidden", "GenericHook", "Hook"]
