"""Every class and function of the code says what it is: the code explains itself."""

import ast
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]

SOURCES = subprocess.run(
    [
        "git",
        "ls-files",
        "src/*.py",
        "packages/*/src/*.py",
        "tools/*/src/*.py",
        "scripts/*.py",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.splitlines()


def undocumented(
    node: ast.AST,
    prefix: str = "",
) -> list[str]:
    """Names of the classes and functions in `node` without a docstring; not those inside functions."""

    found = []

    for child in node.body:
        if isinstance(
            child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            name = prefix + child.name

            if not ast.get_docstring(child):
                found.append(name)

            if isinstance(child, ast.ClassDef):
                found += undocumented(
                    child,
                    name + ".",
                )

    return found


@pytest.mark.parametrize("name", SOURCES)
def test_everything_has_a_docstring(name):

    tree = ast.parse((ROOT / name).read_text())

    assert undocumented(tree) == []
