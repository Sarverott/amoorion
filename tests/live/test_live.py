"""Live tests: every platform tried against its real account (Q13).

They post for real, so they never run on their own: `task test:live --
<platform>…` runs them for the platforms named, with the secrets of the
vault that `.env` links to. Per platform: one marked test post through the
`publish` method; when the plugin can read, the post is looked for; when it
can reply, it is answered. The links of what was posted are printed, for
deleting by hand (no plugin deletes yet).
"""

import os
import re
import time
import uuid
from datetime import UTC, datetime

import pytest

from amoorion.core import AmoorionError
from amoorion.methods import Publish
from amoorion.plugins import Capability, load_plugins, open_plugin
from amoorion.vault import open_vault

pytestmark = pytest.mark.live

# Platforms that can read, but never see their own posts.
READS_ONLY_OTHERS = {"telegram": "getUpdates never shows the bot's own messages"}
TRIES, PAUSE = 5, 3.0


def wanted() -> set[str]:
    return set(filter(None, re.split(r"[\s,]+", os.environ.get("AMOORION_LIVE", ""))))


def platforms() -> list[str]:
    return [name for name in load_plugins().names() if name != "dryrun"]


@pytest.fixture
def vault():
    return open_vault()


@pytest.mark.parametrize("platform", platforms())
def test_live(platform, vault):
    if platform not in wanted():
        pytest.skip(f"not named in AMOORION_LIVE (task test:live -- {platform})")
    plugin = open_plugin(platform, vault)
    missing = []
    for key in plugin.secrets:
        try:
            vault.get(f"{platform}/{key}")
        except AmoorionError:
            missing.append(key)
    if missing:
        pytest.fail(f"{platform}: secrets missing in the vault: {', '.join(missing)}")

    marker = f"amoorion live test {datetime.now(UTC):%Y-%m-%d %H:%M} {uuid.uuid4().hex[:8]}"
    [result] = Publish(vault).run(Publish.Params(text=marker, title=None, to=[platform]))
    assert result.ok, result.error
    posted = result.message
    print(f"\n{platform}: posted {posted.id} {posted.url or '(no link)'}")

    if Capability.READ in plugin.capabilities and platform not in READS_ONLY_OTHERS:
        for _ in range(TRIES):
            if any(marker in message.text for message in plugin.read(20)):
                break
            time.sleep(PAUSE)
        else:
            pytest.fail(f"{platform}: the test post is not among the last 20 read")

    if Capability.REPLY in plugin.capabilities:
        answer = plugin.reply(posted, f"reply to {marker}")
        print(f"{platform}: replied {answer.id} {answer.url or '(no link)'}")
        assert answer.reply_to == posted.id
