"""The front-ends of an `Amoorion`, on that same setup."""

from typing import Any

from amoorion.core import AmoorionError


class FrontEnds:
    def api(self) -> Any:

        from amoorion.api import create_app

        return create_app(
            self.vault,
            self.store,
            self.dataset,
        )

    def mcp(self) -> Any:

        from amoorion.mcp import create_server

        return create_server(
            self.vault,
            self.store,
            self.dataset,
        )

    def cli(
        self,
        *argv: str,
    ) -> int:

        from amoorion.cli import main

        return main(
            list(argv),
            self.vault,
            self.store,
            self.dataset,
        )

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
