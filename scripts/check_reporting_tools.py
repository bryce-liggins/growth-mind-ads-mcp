"""Discover a reporting process and fail unless its tool set is exactly read-only.

Run using the bridge environment: python scripts/check_reporting_tools.py COMMAND [ARGS...]
Environment is inherited; tool discovery makes no Google account request.
"""
import asyncio
import os
import sys
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def main():
    if len(sys.argv) < 2:
        raise SystemExit("Supply the reporting executable and arguments")
    transport = StdioTransport(command=sys.argv[1], args=sys.argv[2:], env=dict(os.environ))
    async with Client(transport) as client:
        names = {t.name for t in await client.list_tools()}
        expected = {"customers_list_accessible_customers", "metadata_get_resource_metadata", "search_search"}
        if names != expected:
            raise SystemExit("FAIL: reporting tool set differs: " + repr(sorted(names)))
        print({"reporting_only": True, "tools": sorted(names), "google_calls": False})

if __name__ == "__main__":
    asyncio.run(main())
