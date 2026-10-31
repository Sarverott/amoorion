"""Daemon: runs services side by side until one ends or it is stopped.

A service is anything long-running: the API (which also receives the hooks)
and a NATS subscriber now; platform listeners (Discord, Telegram, Matrix
bots) later. When one service ends or fails, the others are stopped.
"""

import argparse
import asyncio
from typing import ClassVar

from amoorion.core import Controller
from amoorion.nats import NatsService, enabled


class Service(Controller):
    """One long-running part of the daemon. It runs until stopped; see `Daemon`."""

    async def run(self) -> None:
        """Work until stopped; returning or raising ends the whole daemon."""

        raise NotImplementedError

    async def stop(self) -> None:
        """Ask the service to end; `run` should return soon after."""


class ApiService(Service):
    """The HTTP API with its hooks, as a service of the daemon."""

    name: ClassVar[str] = "api"
    description: ClassVar[str] = "HTTP API and hooks"

    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:
        """Prepare the server; uvicorn loads here since not every daemon has this service."""

        super().__init__()

        import uvicorn

        from amoorion.api import create_app

        self.server = uvicorn.Server(
            uvicorn.Config(
                create_app(),
                host=host,
                port=port,
            )
        )

    async def run(self) -> None:
        """Serve until `stop` is called."""

        await self.server.serve()

    async def stop(self) -> None:
        """Ask the server to finish what it is doing and exit."""

        self.server.should_exit = True


class Daemon(Controller):
    """Runs the services together; when one ends, all are stopped.

    A half-working daemon is worse than a stopped one, as something restarts it from
    outside (systemd, a container).
    """

    name: ClassVar[str] = "daemon"

    def __init__(
        self,
        services: list[Service],
    ) -> None:
        """The services to run."""

        super().__init__()

        self.services = services

    async def run(self) -> None:
        """Start every service, wait for the first to end, stop the rest, raise its failure if any."""

        tasks = [
            asyncio.create_task(service.run(), name=service.name)
            for service in self.services
        ]

        try:
            # One ending is enough: see the class.
            done, _ = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            for service in self.services:
                await service.stop()

            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        for task in done:
            task.result()  # a failed service makes the daemon fail


def services(
    host: str,
    port: int,
) -> list[Service]:
    """The API always; NATS when `.env` names its server."""

    found: list[Service] = [
        ApiService(
            host,
            port,
        )
    ]

    if server := enabled():
        found.append(NatsService(server))

    return found


def serve(args: argparse.Namespace) -> None:
    """Run the daemon until stopped: `amoorion daemon`."""

    asyncio.run(
        Daemon(
            services(
                args.host,
                args.port,
            )
        ).run()
    )
