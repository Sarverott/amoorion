"""The shape of the code of amoorion: open, one thing per line, room for comments.

No formatter writes this shape by itself, so it comes in two passes:

1. `shape`: libcst adds what ruff would never add. A trailing comma to everything
   of two or more items that a statement holds (calls, definitions, collections),
   and a blank line between the statements of a function.
2. `ruff format`: does all the rest, and keeps what is split by a trailing comma.

Conditions stay on one line (`if isinstance(value, bool):`), as they read better
this way. Only the layout changes, never what the code does: the package's
tests/test_shape.py compares the syntax trees.
"""

import json
import subprocess
from pathlib import Path

import libcst as cst


def _commas(node):
    """`node` with a trailing comma in everything of two or more items it holds."""

    if isinstance(
        node,
        cst.Call,
    ):
        return node.with_changes(
            func=_descend(node.func),
            args=_last_comma(
                [
                    item.with_changes(value=_commas(item.value))
                    for item in node.args
                ]
            ),
        )

    if (
        isinstance(
            node,
            cst.Tuple,
        )
        and not node.lpar
    ):
        # `return a, b` has no brackets to open
        return node

    if isinstance(
        node,
        (cst.List, cst.Set, cst.Tuple, cst.Dict),
    ):
        return node.with_changes(
            elements=_last_comma(
                [
                    item.with_changes(value=_commas(item.value))
                    for item in node.elements
                ]
            )
        )

    if isinstance(
        node,
        cst.IfExp,
    ):
        return node.with_changes(
            body=_commas(node.body),
            orelse=_commas(node.orelse),
        )

    return _descend(node)


def _descend(node):
    """`Table(a, b).add(c, d)`: both calls of a chain open."""

    if isinstance(
        node,
        cst.Attribute,
    ):
        return node.with_changes(value=_commas(node.value))

    if isinstance(
        node,
        cst.Await,
    ):
        return node.with_changes(expression=_commas(node.expression))

    return node


def _last_comma(items):

    if len(items) < 2:
        return items

    return [
        *items[:-1],
        items[-1].with_changes(comma=cst.Comma()),
    ]


def _blank(node):
    """`node` with a blank line above it (and above its comments)."""

    lines = node.leading_lines

    if lines and lines[0].comment is None:
        return node

    return node.with_changes(
        leading_lines=[
            cst.EmptyLine(indent=False),
            *lines,
        ]
    )


def _is_docstring(statement) -> bool:

    return (
        isinstance(statement, cst.SimpleStatementLine)
        and isinstance(statement.body[0], cst.Expr)
        and isinstance(
            statement.body[0].value,
            (cst.SimpleString, cst.ConcatenatedString),
        )
    )


class _Open(cst.CSTTransformer):
    """The first pass; `spaced_module` also spaces the top level (notebook cells)."""

    def __init__(
        self,
        spaced_module: bool,
    ) -> None:

        self.spaced_module = spaced_module

        self.functions = 0

    def _value(
        self,
        updated,
    ):

        return updated.with_changes(value=_commas(updated.value))

    def leave_Assign(
        self,
        original,
        updated,
    ):

        return self._value(updated)

    def leave_AugAssign(
        self,
        original,
        updated,
    ):

        return self._value(updated)

    def leave_Expr(
        self,
        original,
        updated,
    ):

        return self._value(updated)

    def leave_AnnAssign(
        self,
        original,
        updated,
    ):

        return self._value(updated) if updated.value else updated

    def leave_Return(
        self,
        original,
        updated,
    ):

        return self._value(updated) if updated.value else updated

    def leave_Raise(
        self,
        original,
        updated,
    ):

        return (
            updated.with_changes(exc=_commas(updated.exc))
            if updated.exc
            else updated
        )

    def visit_FunctionDef(
        self,
        node,
    ) -> None:

        self.functions += 1

    def _space(
        self,
        body,
    ):

        return [
            body[0],
            *(_blank(statement) for statement in body[1:]),
        ]

    def leave_IndentedBlock(
        self,
        original,
        updated,
    ):

        if not self.functions:
            return updated

        return updated.with_changes(body=self._space(updated.body))

    def _open_head(
        self,
        updated,
    ):
        """A blank line under `def …:` (ruff removes one under `for`, `if` and the like)."""

        body = updated.body

        if not isinstance(
            body,
            cst.IndentedBlock,
        ) or _is_docstring(body.body[0]):
            return updated

        return updated.with_changes(
            body=body.with_changes(
                body=[
                    _blank(body.body[0]),
                    *body.body[1:],
                ]
            )
        )

    def leave_FunctionDef(
        self,
        original,
        updated,
    ):

        self.functions -= 1

        parameters = updated.params

        ordered = [
            *parameters.posonly_params,
            *parameters.params,
            *(
                [parameters.star_arg]
                if isinstance(parameters.star_arg, cst.Param)
                else []
            ),
            *parameters.kwonly_params,
            *([parameters.star_kwarg] if parameters.star_kwarg else []),
        ]

        # `def f(a, /):` can't take a comma after the slash from its last name
        if len(ordered) >= 2 and not (
            parameters.posonly_params
            and ordered[-1] is parameters.posonly_params[-1]
        ):
            last = ordered[-1]

            if last is parameters.star_kwarg:
                parameters = parameters.with_changes(
                    star_kwarg=last.with_changes(comma=cst.Comma())
                )

            elif last is parameters.star_arg:
                parameters = parameters.with_changes(
                    star_arg=last.with_changes(comma=cst.Comma())
                )

            elif parameters.kwonly_params:
                parameters = parameters.with_changes(
                    kwonly_params=_last_comma(list(parameters.kwonly_params))
                )

            else:
                parameters = parameters.with_changes(
                    params=[
                        *parameters.params[:-1],
                        last.with_changes(comma=cst.Comma()),
                    ]
                )

        return self._open_head(updated.with_changes(params=parameters))

    def leave_If(
        self,
        original,
        updated,
    ):

        if not self.functions or updated.orelse is None:
            return updated

        return updated.with_changes(orelse=_blank(updated.orelse))

    def leave_Module(
        self,
        original,
        updated,
    ):

        if not self.spaced_module or not updated.body:
            return updated

        return updated.with_changes(body=self._space(updated.body))


def shape(
    source: str,
    spaced_module: bool = False,
) -> str:
    """The first pass alone."""

    return cst.parse_module(source).visit(_Open(spaced_module)).code


def _ruff(
    source: str,
    name: str,
) -> str:

    return subprocess.run(
        [
            "ruff",
            "format",
            "--stdin-filename",
            name,
            "-",
        ],
        input=source,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def shaped_python(
    source: str,
    name: str = "code.py",
) -> str:

    return _ruff(
        shape(source),
        name,
    )


def shaped_notebook(
    text: str,
    name: str = "cell.py",
) -> str:
    """A notebook with its code cells in shape. A cell that isn't plain Python stays as it is."""

    notebook = json.loads(text)

    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue

        try:
            source = _ruff(
                shape(
                    "".join(cell["source"]),
                    spaced_module=True,
                ),
                name,
            )

        except (cst.ParserSyntaxError, subprocess.CalledProcessError):
            continue

        cell["source"] = source.rstrip("\n").splitlines(keepends=True)

    return (
        json.dumps(
            notebook,
            indent=1,
            ensure_ascii=False,
        )
        + "\n"
    )


def run(
    paths: list[Path],
    check: bool = False,
) -> list[Path]:
    """Shape `paths`; with `check` only tell. Returns those out of shape."""

    changed = []

    for path in paths:
        before = path.read_text()

        after = (
            shaped_notebook(before)
            if path.suffix == ".ipynb"
            else shaped_python(
                before,
                str(path),
            )
        )

        if after == before:
            continue

        changed.append(path)

        if not check:
            path.write_text(after)

    return changed
