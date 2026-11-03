# Install a reporting-only Google Ads connection

Google's upstream connector includes asset and label mutations by default. In this guide, **reporting-only** means those tools have been disabled and the discovered tool set has been checked. A prompt that says “only report” is insufficient.

## Install a reviewed revision separately

The reporting connector and this management bridge need separate environments: they currently use different major versions of FastMCP. From your code directory:

```sh
git clone https://github.com/googleads/google-ads-mcp.git
cd google-ads-mcp
git checkout 7452a9d49e3d350403f2610cd7125c60f6d05264
uv sync --python 3.12
```

This upstream revision was inspected and locally started November 3, 2026. Upstream does not ship a lockfile at this revision; save the generated `uv.lock` privately and use `--frozen` subsequently. The tested resolution used Google Ads 35.0.0 and FastMCP 4.1.6. Review and retest before updating the source or lock. See [Google's source](https://github.com/googleads/google-ads-mcp/tree/7452a9d49e3d350403f2610cd7125c60f6d05264).

## Explicitly disable mutation namespaces

Copy [tools_config.yaml](../examples/tools_config.yaml) to a stable private configuration directory:

```yaml
namespaces:
  customers: true
  search: true
  metadata: true
  assets: false
  labels: false
```

In a separate private `reporting.env`, set:

```dotenv
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/private/reporting-credentials.json
GOOGLE_ADS_MCP_TOOLS_CONFIG=/absolute/path/to/private/tools_config.yaml
# Only for manager access:
GOOGLE_ADS_LOGIN_CUSTOMER_ID=
```

Keep files private. Prefer an Ads user with **Read-only** access for unattended reporting. Google's Ads OAuth scope itself is not a read-only scope; tool configuration limits exposed MCP tools, while account permissions also protect against direct API calls.

Do not set `GOOGLE_ADS_MCP_OAUTH_CLIENT_ID` or `GOOGLE_ADS_MCP_OAUTH_CLIENT_SECRET` for this stdio recipe: those settings select upstream's hosted HTTP mode.

## Verify the actual tool list

From the management bridge checkout:

```sh
uv run --frozen --env-file /absolute/path/to/private/reporting.env \
  python scripts/check_reporting_tools.py \
  /absolute/path/to/google-ads-mcp/.venv/bin/google-ads-mcp
```

It must discover exactly:

- `customers_list_accessible_customers`
- `metadata_get_resource_metadata`
- `search_search`

The script fails for a different tool set. Discovery does not call a Google account. Register both servers using [CLIENTS.md](CLIENTS.md), then verify an actual read using [QUERIES.md](QUERIES.md). An explicitly configured missing/invalid YAML file causes upstream startup to fail; an omitted variable can fall back to its mutation-enabled defaults. Keep the absolute config path explicit.
