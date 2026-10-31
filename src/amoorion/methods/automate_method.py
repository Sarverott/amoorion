"""Automate: rules acting on the messages of the inbox."""

from typing import ClassVar

from pydantic import Field

from amoorion.core import Model
from amoorion.methods.base import METHODS
from amoorion.methods.workflow_method import StepsMethod
from amoorion.workflows import (
    Rule,
    StepResult,
    handled,
    known_of,
    mark_handled,
    matches,
    run_steps,
)


class AutomateParams(Model):
    """Rules to apply, and how far back in the inbox to look."""

    rules: list[Rule] = Field(
        min_length=1,
        description="what to do with which messages of the inbox",
    )
    limit: int = Field(
        100,
        ge=1,
        le=1000,
        description="look at this many of the newest messages",
    )


class Handled(Model):
    """One rule run on one message, and how its steps went."""

    rule: str
    platform: str
    message_id: str
    ok: bool
    steps: list[StepResult]


@METHODS.register
class Automate(StepsMethod):
    """Reacting to what arrives: rules over the inbox, for running again and again.

    Each message goes through a rule once; a rule that failed gets it again next time.
    """

    name: ClassVar[str] = "automate"
    description: ClassVar[str] = (
        "Run rules on the messages of the inbox, once per message; a failure is tried again next time"
    )
    Params: ClassVar[type[Model]] = AutomateParams

    def run(
        self,
        params: AutomateParams,
    ) -> list[Handled]:
        """Oldest messages first, so that reactions keep the order things happened in."""

        done = []

        for message in reversed(self.inbox.list(limit=params.limit)):
            for rule in params.rules:
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
