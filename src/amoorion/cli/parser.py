"""The command line: every method becomes a subcommand, its params become options."""

import argparse
import types
import typing
from typing import Any

from pydantic.fields import FieldInfo

from amoorion import __version__
from amoorion.methods import METHODS

# name -> (help, "module:function" taking the parsed args)
SERVERS: dict[str, tuple[str, str]] = {
    "api": (
        "Serve the HTTP API",
        "amoorion.api.base:serve",
    ),
    "mcp": (
        "Serve the MCP server for agents",
        "amoorion.mcp.base:serve",
    ),
    "daemon": (
        "Run the long-running services",
        "amoorion.daemon.base:serve",
    ),
}


def _add_option(
    parser: argparse.ArgumentParser,
    name: str,
    field: FieldInfo,
) -> None:
    """add option? please explain"""

    annotation = field.annotation

    args = typing.get_args(annotation)

    if typing.get_origin(annotation) in (typing.Union, types.UnionType):
        annotation = next(arg for arg in args if arg is not type(None))

    kwargs: dict[str, Any] = {
        "help": field.description,
        "dest": name,
    }

    if typing.get_origin(annotation) is list:
        kwargs["nargs"] = "+"

        kwargs["type"] = typing.get_args(annotation)[0]

    elif annotation in (int, float):
        kwargs["type"] = annotation

    if field.is_required():
        kwargs["required"] = True

    else:
        kwargs["default"] = argparse.SUPPRESS

    parser.add_argument(
        "--" + name.replace("_", "-"),
        **kwargs,
    )


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="amoorion",
        description="Administration of chatting and communication platforms",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"amoorion {__version__}",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="print JSON instead of tables",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="ask step by step what to do",
    )

    commands = parser.add_subparsers(
        dest="command",
        metavar="command",
    )

    for name in METHODS.names():
        method = METHODS.get(name)

        sub = commands.add_parser(
            name,
            help=method.description,
            description=method.description,
        )

        for field_name, field in method.Params.model_fields.items():
            _add_option(
                sub,
                field_name,
                field,
            )

    for name, (help, _) in SERVERS.items():
        sub = commands.add_parser(
            name,
            help=help,
            description=help,
        )

        sub.add_argument(
            "--host",
            default="127.0.0.1",
        )

        sub.add_argument(
            "--port",
            type=int,
            default=8000,
        )

        if name == "mcp":
            sub.add_argument(
                "--transport",
                choices=[
                    "stdio",
                    "streamable-http",
                ],
                default="stdio",
            )

    return parser
