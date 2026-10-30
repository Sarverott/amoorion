"""Workflows: methods run one after another; rules running them on what arrives."""

from amoorion.workflows.base import Rule, Step, StepResult, fill, handled, mark_handled, matches, run_steps

__all__ = ["Rule", "Step", "StepResult", "fill", "handled", "mark_handled", "matches", "run_steps"]
