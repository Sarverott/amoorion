"""A command line as a Python expression, for what would otherwise be a list of strings.

    amo.CALL() / "read" - "platform" + "nowhere" >> print

`/` names a command, `-` an option, `+` a value, and `>>` runs it and hands the output
to a function. Python's precedence is what chooses these: they read left to right, and
`>>` comes last. It is the same `main` as `amoorion read --platform nowhere`.
"""

import contextlib
import io
from collections.abc import Callable
from typing import Any, Self


class CliCall:
    """A command line being put together, run by `>>`."""

    def __init__(
        self,
        run: Callable[[list[str]], int],
    ) -> None:
        """`run` takes the words of the command line and answers the exit code."""

        self.run = run

        self.words: list[str] = []

        self.code: int | None = None

    def _add(
        self,
        word: str,
    ) -> Self:
        """One more word."""

        self.words.append(str(word))

        return self

    def __truediv__(
        self,
        command: str,
    ) -> Self:
        """`/ "read"`: a command."""

        return self._add(command)

    def __sub__(
        self,
        option: str,
    ) -> Self:
        """`- "platform"`: the option `--platform`."""

        return self._add(f"--{option}")

    def __add__(
        self,
        value: Any,
    ) -> Self:
        """`+ "nowhere"`: a value."""

        return self._add(value)

    def __rshift__(
        self,
        receiver: Callable[[str], Any],
    ) -> Self:
        """`>> print`: run it, give the output (errors included) to `receiver`; the exit code stays in `code`."""

        output = io.StringIO()

        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(output),
        ):
            self.code = self.run(self.words)

        receiver(output.getvalue())

        return self
