"""Guided CLI: `amoorion` alone (in a terminal) or `amoorion -i` asks what to do, step by step.

Pick a method from a table, answer one question per parameter (platforms
are offered by what they can do), confirm anything that changes something
on a platform, see the answer, go again or quit. The same methods as the
subcommands; nothing here a subcommand couldn't do.
"""

import types
import typing
from typing import Any, TextIO

from pydantic import ValidationError
from pydantic.fields import FieldInfo
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from amoorion.cli.view import RichView
from amoorion.core import AmoorionError
from amoorion.methods import METHODS, Method
from amoorion.plugins import Capability, load_plugins

# What a method needs a platform to be able to do.
NEEDS = {
    "publish": Capability.POST,
    "read": Capability.READ,
    "snapshot": Capability.READ,
    "reply": Capability.REPLY,
    "delete": Capability.DELETE,
}
PLATFORM_FIELDS = ("platform", "to")
QUIT = ("q", "quit", "exit")


class _Lines:
    """A stream of answers whose end is the end, as Ctrl-D is in a terminal."""

    def __init__(self, stream: TextIO) -> None:
        self.stream = stream

    def readline(self) -> str:
        line = self.stream.readline()
        if not line:
            raise EOFError
        return line


def _inner(annotation: Any) -> Any:
    if typing.get_origin(annotation) in (typing.Union, types.UnionType):
        return next(
            arg for arg in typing.get_args(
                annotation
            ) if arg is not type(None)
        )

    return annotation


class Guide:
    def __init__(self, console: Console | None = None, stream: TextIO | None = None) -> None:
        self.console = console or Console()
        self.stream = _Lines(stream) if stream is not None else None

    def ask(self, question: str, **kwargs: Any) -> str:
        return Prompt.ask(question, console=self.console, stream=self.stream, **kwargs)

    def platforms(self, method: str) -> list[str]:
        plugins = load_plugins()
        need = NEEDS.get(method)
        return [name for name in plugins.names() if need is None or need in plugins.get(name).capabilities]

    def choose(self) -> type[Method] | None:
        table = Table("#", "Method", "Does", title="What should amoorion do?", title_justify="left")
        names = METHODS.names()
        for number, name in enumerate(names, 1):
            method = METHODS.get(name)
            table.add_row(str(number), name + ("" if method.read_only else " [yellow]*[/]"), method.description)
        self.console.print(table)
        self.console.print("[dim][yellow]*[/] changes something on a platform; q quits[/]")
        while True:
            answer = self.ask("Method (number or name)").strip()
            if answer.lower() in QUIT:
                return None
            if answer.isdigit() and 1 <= int(answer) <= len(names):
                return METHODS.get(names[int(answer) - 1])
            if answer in names:
                return METHODS.get(answer)
            self.console.print(f"[red]no method {answer!r}[/]")

    def value(self, method: str, name: str, field: FieldInfo) -> Any:
        annotation = _inner(field.annotation)
        is_list = typing.get_origin(annotation) is list
        label = f"[bold]{name}[/]" + (f" [dim]({field.description})[/]" if field.description else "")
        if name in PLATFORM_FIELDS:
            choices = self.platforms(method)
            self.console.print(f"  platforms that can {method}: " + ", ".join(choices))
        default = None if field.is_required() else field.get_default(call_default_factory=True)
        shown = ", ".join(default) if isinstance(default, list) else default
        while True:
            answer = self.ask(label, default=str(shown) if shown not in (None, "", []) else None).strip()
            if not answer:
                if field.is_required():
                    self.console.print("[red]needed[/]")
                    continue
                return default
            if is_list:
                return [part for part in answer.replace(",", " ").split() if part]
            if annotation is int:
                try:
                    return int(answer)
                except ValueError:
                    self.console.print("[red]a number, please[/]")
                    continue
            return answer

    def once(self, method: type[Method]) -> bool:
        """Ask a method's parameters and run it. False when the user turned back."""
        self.console.rule(f"[bold]{method.name}[/]: {method.description}")
        params = {name: self.value(method.name, name, field) for name, field in method.Params.model_fields.items()}
        try:
            validated = method.Params(**{key: value for key, value in params.items() if value is not None})
        except ValidationError as error:
            for problem in error.errors():
                self.console.print(f"[red]{'.'.join(map(str, problem['loc']))}: {problem['msg']}[/]")
            return False
        if not method.read_only and not Confirm.ask(
            f"Run {method.name} for real?", console=self.console, stream=self.stream, default=False
        ):
            return False
        try:
            result = method().run(validated)
        except AmoorionError as error:
            self.console.print(f"[red]{error}[/]")
            return False
        RichView(self.console).render(result)
        return True

    def run(self) -> int:
        self.console.print("[bold]amoorion[/]: administration of chatting and communication platforms")
        try:
            while True:
                method = self.choose()
                if method is None:
                    return 0
                self.once(method)
                if not Confirm.ask("Anything else?", console=self.console, stream=self.stream, default=True):
                    return 0
        except EOFError:  # the answers ended
            self.console.print()
            return 0
