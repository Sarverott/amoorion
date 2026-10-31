"""What arrives is answered by a language model; here a fake server speaking its API.

For Ollama: `ollama serve`, then in the vault llm/url=http://localhost:11434/v1 and
llm/model=<a model you pulled>. Nothing else changes.
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from amoorion import Amoorion


# Instead of Ollama: answers every request with one sentence.
class FakeModel(BaseHTTPRequestHandler):
    def do_POST(self):

        asked = json.loads(self.rfile.read(int(self.headers["Content-Length"])))

        answer = {
            "choices": [
                {
                    "message": {
                        "content": "Thanks! About: "
                        + asked["messages"][-1]["content"][-30:]
                    }
                }
            ]
        }

        self.send_response(200)

        self.end_headers()

        self.wfile.write(json.dumps(answer).encode())

    def log_message(
        self,
        *args,
    ):

        pass


# Port 0 asks the system for a free port.
server = HTTPServer(
    (
        "127.0.0.1",
        0,
    ),
    FakeModel,
)
threading.Thread(
    target=server.serve_forever,
    daemon=True,
).start()
# What the vault holds in real use: where the model is, and its name.
os.environ |= {
    "AMOORION_SECRET_LLM_URL": f"http://127.0.0.1:{server.server_port}/v1",
    "AMOORION_SECRET_LLM_MODEL": "fake",
}

amo = Amoorion().use("dryrun")
# A question arrives…
[published] = amo.publish(text="Does this work offline?")
# …and reading puts it into the inbox.
amo.read(limit=1)
# Questions get answered: the model writes, `$last` goes on to the reply.
rule = {
    "name": "answer",
    "platform": "dryrun",
    "contains": "?",
    "steps": [
        {
            "method": "compose",
            "params": {
                "prompt": "Answer briefly: $text",
                "system": "You answer our community.",
            },
        },
        {
            "method": "reply",
            "params": {
                "platform": "$platform",
                "to": "$id",
                "text": "$last",
            },
        },
    ],
}
# Run this from a timer: each message is handled only once.
[done] = amo.workflow(rules=[rule])
print(
    done["ok"],
    "|",
    done["steps"][1]["result"]["text"],
)
server.shutdown()
