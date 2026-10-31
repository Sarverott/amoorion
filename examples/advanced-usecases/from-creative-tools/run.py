"""A real local server and a real HTTP call, as a Blender script would make it."""

import os
import socket
import threading
import time

import uvicorn

from amoorion import Amoorion
from amoorion_post import post

# The API wants a token; made up, as is everything here.
os.environ["AMOORION_SECRET_API_TOKEN"] = "example"

# Port 0 asks the system for a free port.
with socket.socket() as probe:
    probe.bind(
        (
            "127.0.0.1",
            0,
        )
    )
    port = probe.getsockname()[1]
# The API on a real port, in the background, as `amoorion api` would run it.
server = uvicorn.Server(
    uvicorn.Config(
        Amoorion().api(),
        host="127.0.0.1",
        port=port,
        log_level="error",
    )
)
thread = threading.Thread(
    target=server.run,
    daemon=True,
)
thread.start()
# Wait until it listens.
while not server.started:
    time.sleep(0.05)

# This is all a script in Blender has to call; see amoorion_post.py.
[result] = post(
    "render finished",
    ["dryrun"],
    "example",
    f"http://127.0.0.1:{port}",
)
print(
    result["platform"],
    result["ok"],
    result["message"]["text"],
)
# Ask the server to finish, and wait until it has.
server.should_exit = True
thread.join()
