"""Live tests: every platform tried against its real account (Q13).

They talk to real platforms, so they never run on their own:

- `task test:connect [-- <platform>…]`: read-only. Logs in, tells the
  profile and reads a few posts; posts nothing.
- `task test:live [-- <platform>…]`: the same, then per platform one
  marked test post through the `publish` method; when the plugin can read,
  the post is looked for; when it can reply, it is answered; when it can
  delete, the reply and the post are deleted again (`delete` keeps a copy
  in the dataset), else their links are printed for deleting by hand.

Without names, every platform whose secrets are in the vault is tried and
the others are skipped; a platform named but without its secrets fails.
The secrets come from the vault that `.env` links to (`task vault:login`).
"""

import os
import re
import time
import uuid
from datetime import UTC, datetime

import pytest

from amoorion.core import AmoorionError
from amoorion.methods import Delete, Publish
from amoorion.methods.base import profile_of
from amoorion.plugins import Capability, load_plugins, open_plugin
from amoorion.vault import open_vault

pytestmark = pytest.mark.live

# Platforms that can read, but never see their own posts.
READS_ONLY_OTHERS = {"telegram": "getUpdates never shows the bot's own messages"}
TRIES, PAUSE = 5, 3.0


def wanted() -> set[str]:
    """The platforms named; empty: all."""
    return set(filter(None, re.split(r"[\s,]+", os.environ.get("AMOORION_LIVE", ""))))


def platforms() -> list[str]:
    return [name for name in load_plugins().names() if name != "dryrun"]


@pytest.fixture
def vault():
    return open_vault()


def ready(platform: str, vault):
    """The plugin, when it is to be tried and has its secrets."""
    named = wanted()
    if named and platform not in named:
        pytest.skip(f"not named in AMOORION_LIVE (task test:live -- {platform})")
    plugin = open_plugin(platform, vault)
    missing, why = [], ""
    for key in plugin.secrets:
        try:
            vault.get(f"{platform}/{key}")
        except AmoorionError as error:
            missing.append(key)
            why = why or str(error)
    if missing:
        reason = f"{platform}: secrets missing in the vault: {', '.join(missing)} ({why})"
        if named:
            pytest.fail(reason)
        pytest.skip(reason)
    return plugin


@pytest.mark.parametrize("platform", platforms())
def test_connect(platform, vault):
    plugin = ready(platform, vault)
    print(f"\n{platform}: profile {profile_of(plugin)}")
    if Capability.READ in plugin.capabilities:
        read = plugin.read(5)
        print(f"{platform}: read {len(read)}" + "".join(f"\n  {m.id} {m.url or ''} {m.text[:60]!r}" for m in read))


@pytest.mark.parametrize("platform", platforms())
def test_live(platform, vault):
    plugin = ready(platform, vault)
    marker = f"amoorion live test {datetime.now(UTC):%Y-%m-%d %H:%M} {uuid.uuid4().hex[:8]}"
    [result] = Publish(vault).run(Publish.Params(text=marker, title=None, to=[platform]))
    assert result.ok, result.error
    posted = result.message
    print(f"\n{platform}: posted {posted.id} {posted.url or '(no link)'}")
    made = [posted]

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
        made.insert(0, answer)

    if Capability.DELETE in plugin.capabilities:
        for message in made:
            deleted = Delete(vault).run(Delete.Params(platform=platform, id=message.id))
            assert deleted.ok, deleted.error
            print(f"{platform}: deleted {message.id}")
    else:
        print(f"{platform}: can't delete; by hand: " + " ".join(m.url or m.id or "?" for m in made))
