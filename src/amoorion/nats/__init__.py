"""NATS: what methods did goes out on subjects, what comes in goes to the inbox."""

from amoorion.nats.base import NatsService, announce, enabled, in_subject, out_subject

__all__ = ["NatsService", "announce", "enabled", "in_subject", "out_subject"]
