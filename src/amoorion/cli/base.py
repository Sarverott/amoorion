"""CLI: every method becomes a subcommand, its params become options.

`amoorion` alone in a terminal, or `amoorion -i`, asks step by step instead
(cli/guide.py).

Servers (`api`, `mcp`, `daemon`) are subcommands too; their namespaces are
imported only when asked for, so the plain commands stay fast.
"""

import argparse
import json
import sys
import types
import typing
from collections.abc import Callable, Sequence
from importlib import import_module
from typing import Any

from pydantic.fields import FieldInfo
from rich.console import Console
from rich.table import Table

from amoorion import __version__
from amoorion.core import AmoorionError, JsonView, Model, View
from amoorion.methods import METHODS

# name -> (help, "module:function" taking the parsed args)
SERVERS: dict[str, tuple[str, str]] = {}


class RichView(View):
    """Tables for lists, key/value tables for one model."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    @staticmethod
    def _cell(value: Any) -> str:
        if isinstance(value, bool):
            return "[green]yes[/]" if value else "[red]no[/]"
        if isinstance(value, dict) and isinstance(value.get("text"), str):
            # A message inside a result: what was said, and where.
            return value["text"] + (f"\n{value['url']}" if value.get("url") else f"\nid {value.get('id')}")
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False) if value else ""
        return "" if value is None else str(value)

    def render(self, model: Model | list[Model]) -> None:
        rows = JsonView().render(model if isinstance(model, list) else [model])
        if not rows:
            self.console.print("[dim]nothing[/dim]")
            return
        table = Table(*rows[0].keys())
        for row in rows:
            table.add_row(*(self._cell(value) for value in row.values()))
        self.console.print(table)


def _add_option(parser: argparse.ArgumentParser, name: str, field: FieldInfo) -> None:
    annotation = field.annotation
    args = typing.get_args(annotation)
    if typing.get_origin(annotation) in (typing.Union, types.UnionType):
        annotation = next(arg for arg in args if arg is not type(None))
    kwargs: dict[str, Any] = {"help": field.description, "dest": name}
    if typing.get_origin(annotation) is list:
        kwargs["nargs"] = "+"
        kwargs["type"] = typing.get_args(annotation)[0]
    elif annotation in (int, float):
        kwargs["type"] = annotation
    if field.is_required():
        kwargs["required"] = True
    else:
        kwargs["default"] = argparse.SUPPRESS
    parser.add_argument("--" + name.replace("_", "-"), **kwargs)


def server(name: str, help: str) -> Callable[[str], None]:
    """Register a server subcommand by the path of its runner."""

    def add(runner: str) -> None:
        SERVERS[name] = (help, runner)

    return add


server("api", "Serve the HTTP API")("amoorion.api.base:serve")
server("mcp", "Serve the MCP server for agents")("amoorion.mcp.base:serve")
server("daemon", "Run the long-running services")("amoorion.daemon.base:serve")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="amoorion", description="Administration of chatting and communication platforms")
    parser.add_argument("--version", action="version", version=f"amoorion {__version__}")
    parser.add_argument("--json", action="store_true", help="print JSON instead of tables")
    parser.add_argument("-i", "--interactive", action="store_true", help="ask step by step what to do")
    commands = parser.add_subparsers(dest="command", metavar="command")
    for name in METHODS.names():
        method = METHODS.get(name)
        sub = commands.add_parser(name, help=method.description, description=method.description)
        for field_name, field in method.Params.model_fields.items():
            _add_option(sub, field_name, field)
    for name, (help, _) in SERVERS.items():
        sub = commands.add_parser(name, help=help, description=help)
        sub.add_argument("--host", default="127.0.0.1")
        sub.add_argument("--port", type=int, default=8000)
        if name == "mcp":
            sub.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    return parser


def main(argv: Sequence[str] | None = None, vault: Any = None, inbox: Any = None, dataset: Any = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        if args.interactive or (sys.stdin.isatty() and sys.stdout.isatty()):
            from amoorion.cli.guide import Guide

            try:
                return Guide().run()
            except (KeyboardInterrupt, EOFError):
                print()
                return 0
        parser.print_help()
        return 0
    try:
        if args.command in SERVERS:
            module, function = SERVERS[args.command][1].split(":")
            getattr(import_module(module), function)(args)
            return 0
        params = {key: value for key, value in vars(args).items() if key not in ("command", "json", "interactive")}
        method = METHODS.get(args.command)(vault, inbox=inbox, dataset=dataset)
        result = method.run(method.Params(**params))
    except (AmoorionError, ValueError) as error:
        print(f"amoorion: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(JsonView().render(result), ensure_ascii=False, indent=2))
    else:
        RichView().render(result)
    return 0
