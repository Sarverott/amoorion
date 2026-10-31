"""Outside programs are run by methods, one method per program, none running just anything."""

import ast
from pathlib import Path

SOURCE = Path(__file__).parents[1] / "src" / "amoorion"

# The vault sits below the methods, which need it to start.
BELOW_THE_METHODS = {"vault/bw_cli.py"}

PROGRAMS = {
    "subprocess",
    "multiprocessing.popen",
    "pty",
}


def _imports(path):

    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_only_methods_start_programs():

    found = {
        str(path.relative_to(SOURCE))
        for path in SOURCE.rglob("*.py")
        if PROGRAMS & set(_imports(path))
    }

    strays = {
        name
        for name in found - BELOW_THE_METHODS
        if not name.startswith("methods/")
    }

    assert not strays


def test_no_call_runs_in_a_shell():

    for path in SOURCE.rglob("*.py"):
        assert "shell=True" not in path.read_text(), path
