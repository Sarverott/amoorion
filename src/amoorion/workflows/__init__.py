"""Workflows: methods run one after another; rules running them on what arrives."""

from amoorion.workflows.base import Step, StepResult, fill, run_steps
from amoorion.workflows.python import (
    EXECUTE,
    WorkflowRun,
    log,
    run_workflow,
    step,
)
from amoorion.workflows.rules import (
    Rule,
    handled,
    known_of,
    load_rules,
    mark_handled,
    matches,
)

__all__ = [
    "EXECUTE",
    "Rule",
    "Step",
    "StepResult",
    "WorkflowRun",
    "fill",
    "handled",
    "known_of",
    "load_rules",
    "log",
    "mark_handled",
    "matches",
    "run_steps",
    "run_workflow",
    "step",
]
