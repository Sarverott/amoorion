"""The shape pass: the author's layout, and never another meaning."""

import ast
import json
import subprocess

from amoorion_dev.shape import shaped_notebook, shaped_python

SOURCE = """\
def f(a, b):
    x = g(1, [2, 3])
    # why
    if x:
        return x, b
    else:
        print(a, b)
    for i in j(1, 2):
        print(i)
"""


def meaning(source: str) -> str:
    """The syntax tree; docstrings as Python itself reads them (ruff indents them)."""

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if (
            isinstance(
                node,
                (
                    ast.Module,
                    ast.ClassDef,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and ast.get_docstring(node) is not None
        ):
            node.body[0].value.value = ast.get_docstring(node)

    return ast.dump(tree)


def test_opens_the_code_up():

    assert (
        shaped_python(SOURCE)
        == """\
def f(
    a,
    b,
):

    x = g(
        1,
        [
            2,
            3,
        ],
    )

    # why
    if x:
        return x, b

    else:
        print(
            a,
            b,
        )

    for i in j(1, 2):
        print(i)
"""
    )


def test_changes_no_meaning_and_stays_as_it_is():

    shaped = shaped_python(SOURCE)

    assert meaning(shaped) == meaning(SOURCE)

    assert shaped_python(shaped) == shaped


def test_every_tracked_file_keeps_its_meaning():

    for name in subprocess.run(
        ["git", "ls-files", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines():
        with open(name) as file:
            source = file.read()

        assert meaning(shaped_python(source)) == meaning(source), name


def test_notebook_keeps_what_isnt_python():

    notebook = json.dumps(
        {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": ["f(1, 2)"],
                },
                {
                    "cell_type": "code",
                    "source": [
                        "!ls\n",
                        "f(1, 2)",
                    ],
                },
                {
                    "cell_type": "code",
                    "source": [
                        "x = 1\n",
                        "f(1, 2)",
                    ],
                },
            ]
        }
    )

    cells = json.loads(shaped_notebook(notebook))["cells"]

    assert cells[0]["source"] == ["f(1, 2)"]

    assert cells[1]["source"] == ["!ls\n", "f(1, 2)"]

    assert "".join(cells[2]["source"]) == "x = 1\n\nf(\n    1,\n    2,\n)"
