"""Guided CLI: `amoorion` alone (in a terminal) or `amoorion -i` asks what to do, step by step.

Pick a method from a table, answer one question per parameter (platforms
are offered by what they can do), confirm anything that changes something
on a platform, see the answer, go again or quit. The same methods as the
subcommands; nothing here a subcommand couldn't do.

At a terminal the questions are arrow menus and form fields, and going back
returns to the previous question, up to the choice of the method. From a pipe
they are plain lines.
"""

import types
import typing
from typing import Any, TextIO

from pydantic import ValidationError
from pydantic.fields import FieldInfo
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from amoorion.cli.menu import BACK, field, menu
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
PLATFORM_FIELDS = (
    "platform",
    "to",
)
QUIT = (
    "q",
    "quit",
    "exit",
)


class _Lines:
    """A stream of answers whose end is the end, as Ctrl-D is in a terminal."""

    def __init__(
        self,
        stream: TextIO,
    ) -> None:
        """Wrap a text stream given by a test or a pipe."""

        self.stream = stream

    def readline(self) -> str:
        """The next line; the end of the stream raises `EOFError`, as a closed terminal does."""

        line = self.stream.readline()

        if not line:
            raise EOFError

        return line


def _inner(annotation: Any) -> Any:
    """The type inside `X | None`: optional parameters are asked the same way as the others."""

    if typing.get_origin(annotation) in (typing.Union, types.UnionType):
        return next(
            arg for arg in typing.get_args(annotation) if arg is not type(None)
        )

    return annotation


class Guide:
    """`amoorion` alone: a dialogue that asks what to do and then each parameter.

    It is built from the methods themselves, so a new method appears here by itself.
    """

    def __init__(
        self,
        console: Console | None = None,
        stream: TextIO | None = None,
        menus: bool | None = None,
        **streams: Any,
    ) -> None:
        """`console`, `stream` and `streams` are there for tests; a person uses the terminal."""

        self.console = console or Console()

        self.stream = _Lines(stream) if stream is not None else None

        self.menus = (
            stream is None and self.console.is_terminal
            if menus is None
            else menus
        )

        self.streams = streams

    def yes(
        self,
        question: str,
        default: bool,
    ) -> bool:
        """A yes or no; going back from a menu means no."""

        if not self.menus:
            return Confirm.ask(
                question,
                console=self.console,
                stream=self.stream,
                default=default,
            )

        options = [
            (
                True,
                "yes",
            ),
            (
                False,
                "no",
            ),
        ]

        return (
            menu(
                question,
                options if default else options[::-1],
                **self.streams,
            )
            is True
        )

    def ask(
        self,
        question: str,
        **kwargs: Any,
    ) -> str:
        """One question on this console."""

        return Prompt.ask(
            question,
            console=self.console,
            stream=self.stream,
            **kwargs,
        )

    def platforms(
        self,
        method: str,
    ) -> list[str]:
        """The platforms able to do what a method needs."""

        plugins = load_plugins()

        need = NEEDS.get(method)

        return [
            name
            for name in plugins.names()
            if need is None or need in plugins.get(name).capabilities
        ]

    def choose(self) -> type[Method] | None:
        """Show the table of methods and ask for one; `None` means leaving."""

        if self.menus:
            answer = menu(
                "What should amoorion do? (* changes something on a platform)",
                [
                    (
                        name,
                        f"{name}{'' if METHODS.get(name).read_only else ' *'}: "
                        f"{METHODS.get(name).description}",
                    )
                    for name in METHODS.names()
                ],
                **self.streams,
            )

            return None if answer is BACK else METHODS.get(answer)

        table = Table(
            "#",
            "Method",
            "Does",
            title="What should amoorion do?",
            title_justify="left",
        )

        names = METHODS.names()

        for number, name in enumerate(names, 1):
            method = METHODS.get(name)

            table.add_row(
                str(number),
                name + ("" if method.read_only else " [yellow]*[/]"),
                method.description,
            )

        self.console.print(table)

        self.console.print(
            "[dim][yellow]*[/] changes something on a platform; q quits[/]"
        )

        while True:
            answer = self.ask("Method (number or name)").strip()

            if answer.lower() in QUIT:
                return None

            if answer.isdigit() and 1 <= int(answer) <= len(names):
                return METHODS.get(names[int(answer) - 1])

            if answer in names:
                return METHODS.get(answer)

            self.console.print(f"[red]no method {answer!r}[/]")

    def value(
        self,
        method: str,
        name: str,
        info: FieldInfo,
    ) -> Any:
        """Ask for one parameter, in the way its type wants: a platform from a list, a list, a number."""

        if self.menus:
            return self.form_value(
                method,
                name,
                info,
            )

        annotation = _inner(info.annotation)

        is_list = typing.get_origin(annotation) is list

        label = f"[bold]{name}[/]" + (
            f" [dim]({info.description})[/]" if info.description else ""
        )

        if name in PLATFORM_FIELDS:
            choices = self.platforms(method)

            self.console.print(
                f"  platforms that can {method}: " + ", ".join(choices)
            )

        default = (
            None
            if info.is_required()
            else info.get_default(call_default_factory=True)
        )

        shown = ", ".join(default) if isinstance(default, list) else default

        while True:
            answer = self.ask(
                label,
                default=str(shown) if shown not in (None, "", []) else None,
            ).strip()

            if not answer:
                if info.is_required():
                    self.console.print("[red]needed[/]")

                    continue

                return default

            if is_list:
                return [
                    part for part in answer.replace(",", " ").split() if part
                ]

            if annotation is int:
                try:
                    return int(answer)
                except ValueError:
                    self.console.print("[red]a number, please[/]")

                    continue

            return answer

    def form_value(
        self,
        method: str,
        name: str,
        info: FieldInfo,
    ) -> Any:
        """One parameter as a menu or a field; `BACK` when going back."""

        annotation = _inner(info.annotation)

        is_list = typing.get_origin(annotation) is list

        default = (
            None
            if info.is_required()
            else info.get_default(call_default_factory=True)
        )

        label = name + (f" ({info.description})" if info.description else "")

        if name in PLATFORM_FIELDS:
            options = [(one, one) for one in self.platforms(method)]

            if is_list:
                return menu(
                    label,
                    options,
                    many=True,
                    marked=default,
                    **self.streams,
                )

            return menu(
                label,
                options,
                **self.streams,
            )

        if annotation is bool:
            return menu(
                label,
                [
                    (
                        True,
                        "yes",
                    ),
                    (
                        False,
                        "no",
                    ),
                ],
                **self.streams,
            )

        shown = ", ".join(default) if isinstance(default, list) else default

        while True:
            answer = field(
                label,
                "" if shown in (None, []) else str(shown),
                **self.streams,
            )

            if answer is BACK:
                return BACK

            answer = answer.strip()

            if not answer:
                if info.is_required():
                    self.console.print("[red]needed[/]")

                    continue

                return default

            if is_list:
                return [
                    part for part in answer.replace(",", " ").split() if part
                ]

            if annotation is int:
                try:
                    return int(answer)
                except ValueError:
                    self.console.print("[red]a number, please[/]")

                    continue

            return answer

    def answers(
        self,
        method: type[Method],
    ) -> dict[str, Any] | None:
        """A method's parameters, one question at a time; going back returns to the previous one."""

        fields = list(method.Params.model_fields.items())

        params: dict[str, Any] = {}

        at = 0

        while at < len(fields):
            name, info = fields[at]

            answer = self.value(
                method.name,
                name,
                info,
            )

            if answer is BACK:
                if at == 0:
                    return None

                at -= 1

                continue

            params[name] = answer

            at += 1

        return params

    def once(
        self,
        method: type[Method],
    ) -> bool:
        """Ask a method's parameters and run it. False when the user turned back."""

        self.console.rule(f"[bold]{method.name}[/]: {method.description}")

        params = self.answers(method)

        if params is None:
            return False

        try:
            validated = method.Params(
                **{
                    key: value
                    for key, value in params.items()
                    if value is not None
                }
            )
        except ValidationError as error:
            for problem in error.errors():
                self.console.print(
                    f"[red]{'.'.join(map(str, problem['loc']))}: {problem['msg']}[/]"
                )

            return False

        if not method.read_only and not self.yes(
            f"Run {method.name} for real?",
            False,
        ):
            return False

        try:
            with self.console.status(f"{method.name}…"):
                result = method().run(validated)
        except AmoorionError as error:
            self.console.print(f"[red]{error}[/]")

            return False

        RichView(self.console).render(result)

        return True

    def run(self) -> int:
        """Keep asking until the person is done; a closed input ends the dialogue quietly."""

        self.console.print(
            "[bold]amoorion[/]: administration of chatting and communication platforms"
        )

        try:
            while True:
                method = self.choose()

                if method is None:
                    return 0

                self.once(method)

                if not self.yes(
                    "Anything else?",
                    True,
                ):
                    return 0
        except EOFError:  # the answers ended
            self.console.print()

            return 0
