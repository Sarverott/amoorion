"""Workflows: a list of steps, each a method with its params.

Text in params may name what is known, `$last` being the text of what the previous
step gave:

    steps:
      - {method: compose, params: {prompt: "Announce: $text"}}
      - {method: publish, params: {text: "$last", to: [mastodon]}}

Values are only ever put in as text, never evaluated.
"""

from string import Template
from typing import Any

from amoorion.core import AmoorionError, Model


class Step(Model):
    method: str
    params: dict[str, Any] = {}


class StepResult(Model):
    method: str
    ok: bool
    result: Any = None
    error: str | None = None


def fill(
    value: Any,
    known: dict[str, str],
) -> Any:
    """Put what is known into the text of params; unknown names stay as written."""

    if isinstance(value, str):
        return Template(value).safe_substitute(known)

    if isinstance(value, list):
        return [fill(item, known) for item in value]

    if isinstance(value, dict):
        return {key: fill(item, known) for key, item in value.items()}

    return value


def text_of(result: Any) -> str:
    """The text a method's answer carries: a message, a composition, a result's message, the first of a list."""

    if isinstance(result, list):
        return text_of(result[0]) if result else ""

    if isinstance(result, Model):
        for name in ("text", "message"):
            value = getattr(
                result,
                name,
                None,
            )

            if isinstance(value, str):
                return value

            if isinstance(value, Model):
                return text_of(value)

    return ""


def run_steps(
    steps: list[Step],
    call: Any,
    known: dict[str, str] | None = None,
) -> list[StepResult]:
    """Run until the end or the first failure; `call(method, params)` returns a method's models."""

    known = dict(known or {})

    results = []

    for step in steps:
        try:
            answer = call(
                step.method,
                fill(
                    step.params,
                    known,
                ),
            )
        except (AmoorionError, ValueError) as error:
            results.append(
                StepResult(
                    method=step.method,
                    ok=False,
                    error=str(error),
                )
            )

            break

        failed = [
            item.error or "failed"
            for item in (answer if isinstance(answer, list) else [answer])
            if getattr(item, "ok", True) is False
        ]

        known["last"] = text_of(answer)

        results.append(
            StepResult(
                method=step.method,
                ok=not failed,
                result=_plain(answer),
                error="; ".join(failed) or None,
            )
        )

        if failed:
            break

    return results


def _plain(answer: Any) -> Any:

    if isinstance(answer, list):
        return [item.model_dump(mode="json") for item in answer]

    return answer.model_dump(mode="json")
