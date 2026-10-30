"""One text, several platforms, in as few lines as it takes."""

import os
import tempfile

from amoorion import Amoorion, Plugins

os.environ |= {"AMOORION_VAULT": "env", "AMOORION_INBOX": tempfile.mktemp(), "AMOORION_DATASET": tempfile.mkdtemp()}

# With your accounts in the vault: .use(Plugins["mastodon"], Plugins["bluesky"], Plugins["x"])
amo = Amoorion().use(Plugins["dryrun"])
for result in amo.publish(text="We are live!", tags=["launch"]):
    print(result["platform"], "ok" if result["ok"] else result["error"])
