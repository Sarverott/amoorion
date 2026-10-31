"""Workflow: methods run one after another, or rules running them on what arrived."""

from typing import Any, ClassVar, Self

from pydantic import Field, model_validator

from amoorion.core import AmoorionError, Model
from amoorion.methods.base import METHODS, Method
from amoorion.workflows import (
    Rule,
    Step,
    StepResult,
    handled,
    known_of,
    mark_handled,
    matches,
    run_steps,
)


class WorkflowParams(Model):
    """The steps to run in order, or the rules to apply to the inbox."""

    steps: list[Step] | None = Field(
        None,
        min_length=1,
        description="methods with their params, one after another; $last is the text of the previous answer",
    )
    rules: list[Rule] | None = Field(
        None,
        min_length=1,
        description="what to do with which messages of the inbox, once per message; a failure is tried again next time",
    )
    limit: int = Field(
        100,
        ge=1,
        le=1000,
        description="with rules: look at this many of the newest messages",
    )

    @model_validator(mode="after")
    def steps_or_rules(self) -> Self:
        """One or the other, and rules here must have something to do."""

        if (self.steps is None) == (self.rules is None):
            raise ValueError("give either steps or rules")

        for rule in self.rules or []:
            if not rule.steps:
                raise ValueError(f"rule {rule.name} has no steps")

        return self


class Handled(Model):
    """One rule run on one message, and how its steps went."""

    rule: str
    platform: str
    message_id: str
    ok: bool
    steps: list[StepResult]


@METHODS.register
class Workflow(Method):
    """Methods one after another; each can use the previous answer as `$last`. Or rules over the inbox.

    Each message goes through a rule once; a rule that failed gets it again next time.
    """

    name: ClassVar[str] = "workflow"
    description: ClassVar[str] = (
        "Run methods one after another, until the first failure; or rules on the messages of the inbox, once per message"
    )
    Params: ClassVar[type[Model]] = WorkflowParams

    def _call(
        self,
        method: str,
        params: dict[str, Any],
    ) -> Any:
        """One step. A workflow can't be a step: no loops."""

        if method == self.name:
            raise AmoorionError(f"a step can't be {method}")

        step = METHODS.get(method)(
            self._vault,
            inbox=self._inbox,
            dataset=self._dataset,
        )

        return step.run(step.Params(**params))

    def run(
        self,
        params: WorkflowParams,
    ) -> list[StepResult] | list[Handled]:
        """Each step run, stopping at the first failure; or each rule run on each new message."""

        if params.steps:
            return run_steps(
                params.steps,
                self._call,
            )

        return self._apply(
            params.rules or [],
            params.limit,
        )

    def _apply(
        self,
        rules: list[Rule],
        limit: int,
    ) -> list[Handled]:
        """Oldest messages first, so that reactions keep the order things happened in."""

        done = []

        for message in reversed(self.inbox.list(limit=limit)):
            for rule in rules:
                if not matches(rule, message) or handled(
                    self.inbox, rule.name, message
                ):
                    continue

                steps = run_steps(
                    rule.steps,
                    self._call,
                    known_of(message),
                )

                ok = all(step.ok for step in steps)

                if ok:
                    mark_handled(
                        self.inbox,
                        rule.name,
                        message,
                    )

                done.append(
                    Handled(
                        rule=rule.name,
                        platform=message.platform,
                        message_id=message.id or "",
                        ok=ok,
                        steps=steps,
                    )
                )

        return done
