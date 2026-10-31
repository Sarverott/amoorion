import asyncio

import pytest

from amoorion.daemon import Daemon, Service


class Sleeper(Service):
    name = "sleeper"

    def __init__(self):

        super().__init__()

        self.stopped = asyncio.Event()

    async def run(self):

        await self.stopped.wait()

    async def stop(self):

        self.stopped.set()


class Quick(Service):
    name = "quick"

    async def run(self):

        await asyncio.sleep(0)


class Broken(Service):
    name = "broken"

    async def run(self):

        raise RuntimeError("boom")


def test_one_service_ending_stops_the_others():

    sleeper = Sleeper()

    asyncio.run(
        asyncio.wait_for(
            Daemon(
                [
                    sleeper,
                    Quick(),
                ]
            ).run(),
            1,
        )
    )

    assert sleeper.stopped.is_set()


def test_failing_service_fails_the_daemon():

    sleeper = Sleeper()

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(
            asyncio.wait_for(
                Daemon(
                    [
                        sleeper,
                        Broken(),
                    ]
                ).run(),
                1,
            )
        )

    assert sleeper.stopped.is_set()
