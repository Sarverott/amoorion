"""One text, several platforms, in as few lines as it takes."""

from amoorion import Amoorion, Plugins

# With your accounts in the vault: .use(Plugins["mastodon"], Plugins["bluesky"], Plugins["x"])
# Add your platforms to `use`, and an env file to `Amoorion(...)`, for real posts.
amo = Amoorion().use(Plugins["dryrun"])
for result in amo.publish(text="We are live!", tags=["launch"]):
    print(
        result["platform"],
        "ok" if result["ok"] else result["error"],
    )
