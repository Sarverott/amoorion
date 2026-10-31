"""The front-ends of an `Amoorion`, on that same setup."""

from typing import Any

from amoorion.core import AmoorionError


class FrontEnds:
    """The ways to reach one `Amoorion` from outside; imported late, as each pulls in its own libraries."""

    def api(self) -> Any:
        """The HTTP API of this setup, an ASGI application for any server."""

        from amoorion.api import create_app

        return create_app(
            self.vault,
            self.store,
            self.dataset,
        )

    def mcp(self) -> Any:
        """The MCP server of this setup, its methods as tools for agents."""

        from amoorion.mcp import create_server

        return create_server(
            self.vault,
            self.store,
            self.dataset,
        )

    def mcp_client(self) -> Any:
        """A client talking to this setup's MCP server in memory: `async with amo.mcp_client() as client`."""

        from mcp import Client

        return Client(self.mcp())

    def cli(
        self,
        *argv: str,
    ) -> int:
        """Run a command line with this setup, as `amo.cli("--json", "plugins")`; answers the exit code."""

        from amoorion.cli import main

        return main(
            list(argv),
            self.vault,
            self.store,
            self.dataset,
        )

    def CALL(self) -> Any:  # noqa: N802
        """A command line as an expression: `amo.CALL() / "plugins" >> print`."""

        from amoorion.cli.call import CliCall

        return CliCall(lambda words: self.cli(*words))

    def run(
        self,
        *argv: str,
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> int:
        """Run the front-end of `flags["mode"]`: cli (default), api or mcp."""

        mode = self.flags.get(
            "mode",
            "cli",
        )

        if mode == "cli":
            return self.cli(*argv)

        if mode == "api":
            import uvicorn

            uvicorn.run(
                self.api(),
                host=host,
                port=port,
            )

        elif mode == "mcp":
            self.mcp().run("stdio")

        else:
            raise AmoorionError(f"no mode named {mode!r}: cli, api or mcp")

        return 0
