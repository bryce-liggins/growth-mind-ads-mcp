"""Exercise real stdio discovery without Google credentials or account calls."""
import asyncio
import os
import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    safe_env = {key: value for key, value in os.environ.items()
                if key not in {"GOOGLE_APPLICATION_CREDENTIALS",
                               "GOOGLE_ADS_DEVELOPER_TOKEN",
                               "GOOGLE_ADS_LOGIN_CUSTOMER_ID"}}
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "growth_mind_ads_mcp"],
        env=safe_env,
    )
    async with Client(transport) as client:
        names = {tool.name for tool in await client.list_tools()}
        expected = {"get_write_capabilities", "validate_mutation_batch",
                    "apply_approved_mutation_batch", "validate_create_batch",
                    "create_paused_batch"}
        assert names == expected, names
        result = await client.call_tool("get_write_capabilities",
                                        {"customer_id": "1234567890"})
        assert not result.is_error
        print({"tools": sorted(names), "google_calls": False,
               "capabilities_call": "passed"})


if __name__ == "__main__":
    asyncio.run(main())

