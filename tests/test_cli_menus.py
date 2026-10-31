"""Arrow menus and the guide on them, with keys from a pipe and nothing on a screen."""

import io

import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from rich.console import Console

from amoorion.cli.guide import Guide
from amoorion.cli.menu import BACK, field, menu

DOWN = "\x1b[B"
UP = "\x1b[A"
LEFT = "\x1b[D"
ENTER = "\r"


@pytest.fixture
def keys():

    with create_pipe_input() as pipe:
        yield pipe


def streams(pipe):

    return {
        "input": pipe,
        "output": DummyOutput(),
    }


OPTIONS = [
    (
        "a",
        "first",
    ),
    (
        "b",
        "second",
    ),
    (
        "c",
        "third",
    ),
]


def test_arrows_and_enter(keys):

    keys.send_text(DOWN + DOWN + UP + ENTER)

    assert menu("?", OPTIONS, **streams(keys)) == "b"


def test_arrows_wrap_around(keys):

    keys.send_text(UP + ENTER)

    assert menu("?", OPTIONS, **streams(keys)) == "c"


def test_left_goes_back(keys):

    keys.send_text(LEFT)

    assert menu("?", OPTIONS, **streams(keys)) is BACK


def test_space_marks_many(keys):

    keys.send_text(" " + DOWN + " " + DOWN + DOWN + " " + ENTER)

    assert menu(
        "?",
        OPTIONS,
        many=True,
        marked=["c"],
        **streams(keys),
    ) == [
        "b",
        "c",
    ]


def test_ctrl_c_leaves(keys):

    keys.send_text("\x03")

    with pytest.raises(EOFError):
        menu(
            "?",
            OPTIONS,
            **streams(keys),
        )


def test_field_edits_its_default(keys):

    keys.send_text("!" + ENTER)

    assert field("name", "x", **streams(keys)) == "x!"


def guide(keys):

    return Guide(
        console=Console(
            file=io.StringIO(),
            width=120,
        ),
        menus=True,
        **streams(keys),
    )


def test_guide_runs_a_method_going_back_on_the_way(
    keys,
    monkeypatch,
):

    monkeypatch.setenv(
        "AMOORION_VAULT",
        "env",
    )

    the = guide(keys)

    from amoorion.methods import METHODS

    position = METHODS.names().index("plugins")

    keys.send_text(DOWN * position + ENTER)

    assert the.choose().name == "plugins"

    keys.send_text(LEFT)

    assert the.choose() is None


def test_answers_go_back_to_the_previous_question(
    keys,
    monkeypatch,
):

    the = guide(keys)

    from amoorion.core import Model

    class Params(Model):
        first: str

        second: str

    class Method:
        name = "made-up"

        Params = None

    Method.Params = Params

    asked = iter(
        [
            "one",
            BACK,
            "again",
            "two",
        ]
    )

    monkeypatch.setattr(
        the,
        "value",
        lambda *_: next(asked),
    )

    assert the.answers(Method) == {
        "first": "again",
        "second": "two",
    }


def test_call_runs_the_same_command_line(monkeypatch):

    from amoorion import Amoorion

    output = []

    call = Amoorion().CALL() / "read" - "platform" + "nowhere" >> output.append

    assert call.words == ["read", "--platform", "nowhere"]

    assert call.code == 1 and "nowhere" in output[0]


def test_env_files_read_and_written(tmp_path):

    from amoorion.utilities import read_env, write_env

    path = tmp_path / "a.env"

    path.write_text("# keep me\nA=1\n")

    write_env(
        path,
        A="2",
        B="two words",
    )

    assert read_env(path) == {"A": "2", "B": "two words"}

    assert "# keep me" in path.read_text()
