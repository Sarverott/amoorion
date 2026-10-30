"""What arrives is answered by a language model; here a fake server speaking its API.

For Ollama: `ollama serve`, then in the vault llm/url=http://localhost:11434/v1 and
llm/model=<a model you pulled>. Nothing else changes.
"""

import json
import os
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from amoorion import Amoorion
from amoorion.models import Message


class FakeModel(BaseHTTPRequestHandler):
    def do_POST(self):
        asked = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        answer = {"choices": [{"message": {"content": "Thanks! About: " + asked["messages"][-1]["content"][-30:]}}]}
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(answer).encode())

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), FakeModel)
threading.Thread(target=server.serve_forever, daemon=True).start()
os.environ |= {
    "AMOORION_VAULT": "env",
    "AMOORION_INBOX": tempfile.mktemp(),
    "AMOORION_DATASET": tempfile.mkdtemp(),
    "AMOORION_SECRET_LLM_URL": f"http://127.0.0.1:{server.server_port}/v1",
    "AMOORION_SECRET_LLM_MODEL": "fake",
}

amo = Amoorion().use("dryrun")
[published] = amo.publish(text="Does this work offline?")
amo.read(limit=1)
rule = {
    "name": "answer",
    "platform": "dryrun",
    "contains": "?",
    "steps": [
        {"method": "compose", "params": {"prompt": "Answer briefly: $text", "system": "You answer our community."}},
        {"method": "reply", "params": {"platform": "$platform", "to": "$id", "text": "$last"}},
    ],
}
[done] = amo.automate(rules=[rule])
print(done["ok"], "|", done["steps"][1]["result"]["text"])
server.shutdown()
