"""A release on GitHub becomes a press note: hook -> inbox -> rule -> publish."""

import hashlib
import hmac
import json
import os

from fastapi.testclient import TestClient

from amoorion import Amoorion

# The secret set on the webhook at GitHub; made up here.
os.environ["AMOORION_SECRET_HOOKS_GITHUB_SECRET"] = "example"

amo = Amoorion()
# What GitHub sends when a release is published.
body = json.dumps(
    {
        "action": "published",
        "repository": {"full_name": "me/tool"},
        "release": {
            "name": "v1.0",
            "html_url": "https://example.org/v1",
        },
    }
).encode()
# GitHub signs the body with the secret; the hook refuses anything else.
signature = "sha256=" + hmac.new(b"example", body, hashlib.sha256).hexdigest()
# The call GitHub would make; it ends up in the inbox.
TestClient(amo.api()).post(
    "/hooks/github",
    content=body,
    headers={
        "X-GitHub-Event": "release",
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json",
    },
)

# Which of the inbox's messages become a press note, and how.
rule = {
    "name": "press",
    "platform": "hook:github",
    "contains": "release published",
    "steps": [
        {
            "method": "publish",
            "params": {
                "text": "New: $text $url",
                "to": ["dryrun"],
            },
        }
    ],
}
# Run twice: the second run finds nothing to do.
for done in amo.automate(rules=[rule]) + amo.automate(
    rules=[rule]
):  # the second finds nothing new
    print(
        done["rule"],
        done["ok"],
        done["steps"][0]["result"][0]["message"]["text"],
    )
