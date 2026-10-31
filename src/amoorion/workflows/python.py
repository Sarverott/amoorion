"""Workflows written in Python: `@amo.workflow`, `@step`, `EXECUTE`, with logs and an artifact::

    @amo.workflow("announce", rules="resources/rulesets/world.rule.yml")
    def announce(amo, inputs):

        @step
        def write():
            return {"text": f"News: {inputs['text']}"}

        @step
        def send():
            log("sending")
            amo.publish(text="the news", to=["dryrun"])

        return EXECUTE(write, send).serial()

A step fails by raising or by answering `False`, and `EXECUTE` says whether all went
well. What a step answers besides `True`, `False` or `None` is kept in the artifact, under
the step's name; what a workflow answers besides those is the artifact.
"""

import asyncio
import functools
import inspect
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar, copy_context
from pathlib import Path
from typing import Any

from amoorion.core import Model


class WorkflowRun(Model):
    """How a run of a workflow went: what it said along the way, and what came out."""

    name: str
    ok: bool
    logs: list[str] = []
    artifact: Any = None
    error: str | None = None

    def save(
        self,
        path: str | Path,
    ) -> Path:
        """The run as a JSON file, for what comes next: the sender of a post, another workflow."""

        path = Path(path).expanduser()

        path.write_text(
            self.model_dump_json(
                indent=2,
                fallback=str,
            )
        )

        return path


class _Current:
    """What the running workflow has collected so far; steps run in threads share it."""

    def __init__(self) -> None:
        """Nothing yet."""

        self.logs: list[str] = []

        self.artifact: dict[str, Any] = {}


_current: ContextVar[_Current | None] = ContextVar(
    "amoorion_workflow_run",
    default=None,
)


def log(text: str) -> None:
    """One line into the logs of the running workflow; outside of one it goes nowhere."""

    current = _current.get()

    if current:
        current.logs.append(text)


def _finished(
    name: str,
    answer: Any,
) -> bool:
    """A step's answer into the logs and the artifact; whether it went well."""

    if answer is False:
        log(f"{name}: failed")

        return False

    current = _current.get()

    if current and answer is not None and answer is not True:
        current.artifact[name] = answer

    log(f"{name}: done")

    return True


def _failed(
    name: str,
    error: Exception,
) -> bool:
    """A step that raised: the reason goes into the logs."""

    log(f"{name}: failed: {error}")

    return False


def step(function: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a function, plain or async, as a step: it is logged, and answers whether it went well."""

    name = function.__name__

    if inspect.iscoroutinefunction(function):

        @functools.wraps(function)
        async def wrapper_async(
            *args: Any,
            **kwargs: Any,
        ) -> bool:

            log(f"{name}: begins")

            try:
                return _finished(
                    name,
                    await function(
                        *args,
                        **kwargs,
                    ),
                )
            except Exception as error:
                return _failed(
                    name,
                    error,
                )

        return wrapper_async

    @functools.wraps(function)
    def wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> bool:

        log(f"{name}: begins")

        try:
            return _finished(
                name,
                function(
                    *args,
                    **kwargs,
                ),
            )
        except Exception as error:
            return _failed(
                name,
                error,
            )

    return wrapper


class EXECUTE:
    """Steps to run together: `.serial()` one after another, `.paralel()` at the same time."""

    def __init__(
        self,
        *steps: Callable[..., Any],
    ) -> None:
        """The steps, in the order to run them."""

        self.steps = steps

    def serial(self) -> Any:
        """One after another, until the first failure; to be awaited when any step is async."""

        if any(inspect.iscoroutinefunction(one) for one in self.steps):
            return self._serial_async()

        return all(one() for one in self.steps)

    async def _serial_async(self) -> bool:
        """`serial` with async steps among them."""

        for one in self.steps:
            answer = one()

            if inspect.isawaitable(answer):
                answer = await answer

            if answer is False:
                return False

        return True

    async def paralel(self) -> bool:
        """All at the same time, plain ones in threads; every step ends, whatever the others do."""

        answers = await asyncio.gather(
            *(
                one()
                if inspect.iscoroutinefunction(one)
                else asyncio.to_thread(one)
                for one in self.steps
            )
        )

        return all(answer is not False for answer in answers)

    parallel = paralel


def _finish(answer: Any) -> Any:
    """Wait for what is still to be awaited, also from where a loop is already running (a notebook)."""

    if not inspect.isawaitable(answer):
        return answer

    async def waited() -> Any:

        return await answer

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(waited())

    with ThreadPoolExecutor(1) as pool:
        return pool.submit(
            copy_context().run,
            asyncio.run,
            waited(),
        ).result()


def run_workflow(
    name: str,
    function: Callable[..., Any],
    amo: Any,
    inputs: dict[str, Any],
) -> WorkflowRun:
    """Run one workflow; its failure is told in the run, not raised."""

    current = _Current()

    token = _current.set(current)

    try:
        answer = _finish(
            function(
                amo,
                inputs,
            )
        )
    except Exception as error:
        return WorkflowRun(
            name=name,
            ok=False,
            logs=current.logs,
            artifact=current.artifact or None,
            error=str(error),
        )
    finally:
        _current.reset(token)

    plain = answer is None or isinstance(answer, bool)

    return WorkflowRun(
        name=name,
        ok=answer is not False,
        logs=current.logs,
        artifact=(current.artifact or None) if plain else answer,
    )
