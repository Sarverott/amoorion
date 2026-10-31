"""The workflows of an `Amoorion`: written in Python, run by name or by what arrives."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from amoorion.core import AmoorionError
from amoorion.workflows import (
    Rule,
    Step,
    WorkflowRun,
    handled,
    known_of,
    load_rules,
    mark_handled,
    matches,
    run_steps,
    run_workflow,
)

Rules = str | Path | list[Any]


def rules_of(rules: Rules | None) -> list[Rule]:
    """Rules as they may be given: a YAML file or directory, or a list of rules and files."""

    if rules is None:
        return []

    if isinstance(rules, str | Path):
        return load_rules(rules)

    found: list[Rule] = []

    for rule in rules:
        if isinstance(rule, str | Path):
            found += load_rules(rule)

        else:
            found.append(Rule.model_validate(rule))

    return found


class Workflows:
    """Workflows kept by name on this object."""

    def workflow(
        self,
        name: str | None = None,
        *,
        rules: Rules | None = None,
        steps: list[Step | dict[str, Any]] | None = None,
        limit: int = 100,
    ) -> Any:
        """With a name, a decorator keeping a function as a workflow; without, the method `workflow`.

        `@amo.workflow("name", rules=…)` keeps the function; `amo.workflow(steps=[…])` runs
        steps, `amo.workflow(rules=…)` runs rules on the inbox.
        """

        if name is None:
            given = {"steps": steps} if steps is not None else {}

            if rules is not None:
                given |= {
                    "rules": [rule.model_dump() for rule in rules_of(rules)],
                    "limit": limit,
                }

            return self.call(
                "workflow",
                **given,
            )

        if steps is not None:
            raise AmoorionError(
                "a named workflow is a function; steps belong to its rules"
            )

        def keep(function: Callable[..., Any]) -> Callable[..., Any]:

            self._workflows[name] = (
                function,
                rules_of(rules),
            )

            return function

        return keep

    def workflows(self) -> list[str]:
        """The names of the workflows kept on this object."""

        return list(self._workflows)

    def perform(
        self,
        name: str,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowRun:
        """Run a kept workflow by its name, whatever its rules say."""

        if name not in self._workflows:
            raise AmoorionError(f"no workflow named {name!r}")

        function, _ = self._workflows[name]

        return run_workflow(
            name,
            function,
            self,
            inputs or {},
        )

    def react(
        self,
        limit: int = 100,
    ) -> list[WorkflowRun]:
        """Run kept workflows on the inbox's new messages their rules match, once per message.

        Oldest first; safe to run from a timer. A failed run gets the message again next time.
        The steps of a rule run first, and their results are in `inputs["steps"]`.
        """

        store = self.store

        runs = []

        for message in reversed(store.list(limit=limit)):
            for name, (_, rules) in self._workflows.items():
                rule = next(
                    (one for one in rules if matches(one, message)),
                    None,
                )

                key = f"workflow:{name}"

                if rule is None or handled(store, key, message):
                    continue

                run = self._react_one(
                    name,
                    rule,
                    message,
                )

                if run.ok:
                    mark_handled(
                        store,
                        key,
                        message,
                    )

                runs.append(run)

        return runs

    def _react_one(
        self,
        name: str,
        rule: Rule,
        message: Any,
    ) -> WorkflowRun:
        """One message: the rule's steps, then the workflow if they went well."""

        known = known_of(message)

        done = run_steps(
            rule.steps,
            self.method("workflow")._call,
            known,
        )

        failed = next(
            (one for one in done if not one.ok),
            None,
        )

        if failed:
            return WorkflowRun(
                name=name,
                ok=False,
                error=f"rule {rule.name}, {failed.method}: {failed.error}",
            )

        return self.perform(
            name,
            known | {"steps": [one.model_dump(mode="json") for one in done]},
        )
