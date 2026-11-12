"""Call the local MCP after an upgrade without restarting unrelated agents.

Only nonsecret arguments or private file paths belong in --arguments.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call(tool: str, arguments: dict):
    parameters = StdioServerParameters(
        command=sys.executable, args=[str(Path(__file__).with_name("server.py"))],
    )
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=["authenticate", "op_command", "write_item", "run_with_secrets"])
    parser.add_argument("--arguments", default="{}", help="JSON with nonsecret arguments and private file paths only")
    options = parser.parse_args()
    result = asyncio.run(call(options.tool, json.loads(options.arguments)))
    for block in result.content:
        if block.type == "text":
            print(block.text)
    raise SystemExit(1 if result.isError else 0)
