import asyncio
import json

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from amoorion.mcp import create_server
from amoorion.vault import VaultLink, open_vault


def server():

    return create_server(open_vault(VaultLink(kind="env")))


def test_every_method_is_a_tool():

    tools = {tool.name: tool for tool in asyncio.run(server().list_tools())}

    assert {"plugins", "publish", "read"} <= set(tools)

    assert tools["publish"].input_schema["required"] == ["text", "to"]

    assert (
        tools["read"].annotations.read_only_hint
        and not tools["publish"].annotations.read_only_hint
    )


def test_call_publish():

    result = asyncio.run(
        server().call_tool(
            "publish",
            {
                "text": "from an agent",
                "to": ["dryrun"],
            },
        )
    )

    assert not result.is_error

    # A list comes back as one content block per item.
    [published] = [json.loads(block.text) for block in result.content]

    assert published["ok"] and published["message"]["text"] == "from an agent"


def test_failing_call_raises_tool_error():

    with pytest.raises(ToolError, match="no plugin named 'nope'"):
        asyncio.run(
            server().call_tool(
                "read",
                {"platform": "nope"},
            )
        )


def test_resources_through_a_client():

    from amoorion import Amoorion

    async def talk():

        amo = Amoorion().use("dryrun")

        amo.publish(text="seen")

        amo.read(limit=1)

        async with amo.mcp_client() as client:
            methods = await client.read_resource("amoorion://methods")

            inbox = await client.read_resource("amoorion://inbox/5")

            return methods.contents[0].text, inbox.contents[0].text

    methods, inbox = asyncio.run(talk())

    assert any(
        method["name"] == "publish" and not method["read_only"]
        for method in json.loads(methods)
    )

    assert "seen" in inbox
