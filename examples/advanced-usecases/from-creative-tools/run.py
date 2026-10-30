"""A real local server and a real HTTP call, as a Blender script would make it."""

import os
import socket
import threading
import time

import uvicorn

from amoorion import Amoorion
from amoorion_post import post

os.environ["AMOORION_SECRET_API_TOKEN"] = "example"

with socket.socket() as probe:
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
server = uvicorn.Server(uvicorn.Config(Amoorion().api(), host="127.0.0.1", port=port, log_level="error"))
thread = threading.Thread(target=server.run, daemon=True)
thread.start()
while not server.started:
    time.sleep(0.05)

[result] = post("render finished", ["dryrun"], "example", f"http://127.0.0.1:{port}")
print(result["platform"], result["ok"], result["message"]["text"])
server.should_exit = True
thread.join()
