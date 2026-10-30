"""MCP: every method becomes a tool whose arguments are the method's params.

Read-only methods are marked so; agents' clients can let them run without
asking, and ask before the rest (publishing reaches real accounts).
"""

import argparse
import inspect
from collections.abc import Callable
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from amoorion import __version__
from amoorion.core import AmoorionError, JsonView
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.methods import METHODS, Method
from amoorion.vault import Vault, open_vault


def _tool(method: type[Method], vault: Vault, inbox: Inbox | None, dataset: Dataset | None) -> Callable[..., Any]:
    def call(**params: Any) -> Any:
        try:
            return JsonView().render(method(vault, inbox=inbox, dataset=dataset).run(method.Params(**params)))
        except AmoorionError as error:  # tell the agent why, not only that it failed
            raise ToolError(str(error)) from error

    call.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        [
            inspect.Parameter(
                name,
                inspect.Parameter.KEYWORD_ONLY,
                annotation=field.annotation,
                default=inspect.Parameter.empty if field.is_required() else field.default,
            )
            for name, field in method.Params.model_fields.items()
        ]
    )
    return call


def create_server(vault: Vault | None = None, inbox: Inbox | None = None, dataset: Dataset | None = None) -> MCPServer:
    vault = vault or open_vault()
    server = MCPServer("amoorion", version=__version__, instructions=__doc__)
    for name in METHODS.names():
        method = METHODS.get(name)
        server.add_tool(
            _tool(method, vault, inbox, dataset),
            name=name,
            description=method.description,
            annotations=ToolAnnotations(readOnlyHint=method.read_only, destructiveHint=False),
        )
    return server


def serve(args: argparse.Namespace) -> None:
    server = create_server()
    if args.transport == "stdio":
        server.run("stdio")
    else:
        server.run(args.transport, host=args.host, port=args.port)
