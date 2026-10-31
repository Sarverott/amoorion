"""Workflow: methods run one after another."""

from typing import Any, ClassVar

from pydantic import Field

from amoorion.core import AmoorionError, Model
from amoorion.methods.base import METHODS, Method
from amoorion.workflows import Step, StepResult, run_steps

# Steps can't start steps: a rule that ends up calling itself would never stop.
NOT_A_STEP = {
    "workflow",
    "automate",
}


class WorkflowParams(Model):
    steps: list[Step] = Field(
        min_length=1,
        description="methods with their params, one after another; $last is the text of the previous answer",
    )


class StepsMethod(Method):
    def _call(
        self,
        method: str,
        params: dict[str, Any],
    ) -> Any:

        if method in NOT_A_STEP:
            raise AmoorionError(f"a step can't be {method}")

        step = METHODS.get(method)(
            self._vault,
            inbox=self._inbox,
            dataset=self._dataset,
        )

        return step.run(step.Params(**params))


@METHODS.register
class Workflow(StepsMethod):
    name: ClassVar[str] = "workflow"
    description: ClassVar[str] = (
        "Run methods one after another, until the end or the first failure"
    )
    Params: ClassVar[type[Model]] = WorkflowParams

    def run(
        self,
        params: WorkflowParams,
    ) -> list[StepResult]:

        return run_steps(
            params.steps,
            self._call,
        )
