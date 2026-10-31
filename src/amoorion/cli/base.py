"""CLI: runs what the command line asked for (parser.py), shows the answer (view.py).

`amoorion` alone in a terminal, or `amoorion -i`, asks step by step instead
(guide.py).

Servers (`api`, `mcp`, `daemon`) are subcommands too; their namespaces are
imported only when asked for, so the plain commands stay fast.
"""

import json
import sys
from collections.abc import Sequence
from importlib import import_module
from typing import Any

from amoorion.cli.parser import SERVERS, build_parser
from amoorion.cli.view import RichView
from amoorion.core import AmoorionError, JsonView
from amoorion.methods import METHODS


def main(
    argv: Sequence[str] | None = None,
    vault: Any = None,
    inbox: Any = None,
    dataset: Any = None,
) -> int:

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

        params = {
            key: value
            for key, value in vars(args).items()
            if key not in ("command", "json", "interactive")
        }

        method = METHODS.get(args.command)(
            vault,
            inbox=inbox,
            dataset=dataset,
        )

        result = method.run(method.Params(**params))
    except (AmoorionError, ValueError) as error:
        print(
            f"amoorion: {error}",
            file=sys.stderr,
        )

        return 1

    if args.json:
        print(
            json.dumps(
                JsonView().render(result),
                ensure_ascii=False,
                indent=2,
            )
        )

    else:
        RichView().render(result)

    return 0
