"""Arrow menus and form fields: up and down choose, Enter confirms, Esc or left goes back.

(A terminal doesn't tell when Shift alone is pressed, so going back can't be on it.)
Ctrl-C and Ctrl-D leave, as `EOFError`. Input and output can be given, for tests.
"""

from typing import Any

from prompt_toolkit import Application, PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FormattedTextControl, Layout, Window
from prompt_toolkit.layout.dimension import Dimension


class _Back:
    """The answer of a menu or field left by going back."""

    def __repr__(self) -> str:
        """As it reads in a test's failure."""

        return "BACK"


BACK = _Back()


def _lines(
    title: str,
    options: list[tuple[Any, str]],
    at: int,
    chosen: set[int] | None,
) -> list[tuple[str, str]]:
    """What a menu shows now: the title, then one line per option, the current one marked."""

    lines = [
        (
            "bold",
            f"{title}\n",
        )
    ]

    for number, (_, label) in enumerate(options):
        box = "" if chosen is None else "[x] " if number in chosen else "[ ] "

        lines.append(
            (
                "reverse" if number == at else "",
                f"{'>' if number == at else ' '} {box}{label}\n",
            )
        )

    hint = "up/down choose, Enter confirms, Esc or left goes back"

    lines.append(
        (
            "italic",
            hint if chosen is None else f"{hint}, Space marks",
        )
    )

    return lines


def menu(
    title: str,
    options: list[tuple[Any, str]],
    many: bool = False,
    marked: list[Any] | None = None,
    **streams: Any,
) -> Any:
    """Choose one option's value, or with `many` a list of them; `BACK` when going back."""

    state = {"at": 0}

    chosen: set[int] | None = (
        {
            number
            for number, (value, _) in enumerate(options)
            if value in (marked or [])
        }
        if many
        else None
    )

    keys = KeyBindings()

    @keys.add("up")
    def up(event: Any) -> None:

        state["at"] = (state["at"] - 1) % len(options)

    @keys.add("down")
    def down(event: Any) -> None:

        state["at"] = (state["at"] + 1) % len(options)

    @keys.add("space")
    def mark(event: Any) -> None:

        if chosen is not None:
            chosen.symmetric_difference_update({state["at"]})

    @keys.add("enter")
    def confirm(event: Any) -> None:

        event.app.exit(
            result=options[state["at"]][0]
            if chosen is None
            else [options[number][0] for number in sorted(chosen)]
        )

    @keys.add("escape", eager=True)
    @keys.add("left")
    def back(event: Any) -> None:

        event.app.exit(result=BACK)

    @keys.add("c-c")
    @keys.add("c-d")
    def leave(event: Any) -> None:

        event.app.exit(exception=EOFError())

    return Application(
        layout=Layout(
            Window(
                FormattedTextControl(
                    lambda: _lines(
                        title,
                        options,
                        state["at"],
                        chosen,
                    )
                ),
                height=Dimension(max=len(options) + 2),
            )
        ),
        key_bindings=keys,
        erase_when_done=True,
        **streams,
    ).run()


def field(
    label: str,
    default: str = "",
    **streams: Any,
) -> Any:
    """One line of text, `default` already there to edit; `BACK` on Esc."""

    keys = KeyBindings()

    @keys.add("escape", eager=True)
    def back(event: Any) -> None:

        event.app.exit(result=BACK)

    try:
        return PromptSession(
            key_bindings=keys,
            **streams,
        ).prompt(
            f"{label}: ",
            default=default,
        )
    except KeyboardInterrupt as error:
        raise EOFError from error
