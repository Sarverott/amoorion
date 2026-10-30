"""A release on GitHub becomes a press note: hook -> inbox -> rule -> publish."""

import hashlib
import hmac
import json
import os
import tempfile

from fastapi.testclient import TestClient

from amoorion import Amoorion

os.environ |= {"AMOORION_VAULT": "env", "AMOORION_INBOX": tempfile.mktemp(), "AMOORION_DATASET": tempfile.mkdtemp()}
os.environ["AMOORION_SECRET_HOOKS_GITHUB_SECRET"] = "example"

amo = Amoorion()
body = json.dumps({"action": "published", "repository": {"full_name": "me/tool"}, "release": {"name": "v1.0", "html_url": "https://example.org/v1"}}).encode()
signature = "sha256=" + hmac.new(b"example", body, hashlib.sha256).hexdigest()
TestClient(amo.api()).post("/hooks/github", content=body, headers={"X-GitHub-Event": "release", "X-Hub-Signature-256": signature, "Content-Type": "application/json"})

rule = {
    "name": "press",
    "platform": "hook:github",
    "contains": "release published",
    "steps": [{"method": "publish", "params": {"text": "New: $text $url", "to": ["dryrun"]}}],
}
for done in amo.automate(rules=[rule]) + amo.automate(rules=[rule]):  # the second finds nothing new
    print(done["rule"], done["ok"], done["steps"][0]["result"][0]["message"]["text"])
