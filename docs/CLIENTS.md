# Connect an agent client

This server is a local stdio process. These instructions register that process; they do not deploy a remotely accessible service. Browser-only chat support must be checked separately.

Complete installation, private configuration and the no-credential tests first. In every example, replace paths with your own absolute paths. Use the absolute path to uv if your client cannot find it. Keep all secret values in the private env file.

## Codex

```sh
codex mcp add growth-mind-ads -- \
  uv run --project /absolute/path/to/growth-mind-ads-mcp \
  --frozen --env-file /absolute/path/to/private/ads.env growth-mind-ads-mcp
codex mcp list
```

The registration syntax was checked against local `codex mcp add --help`. Restart/reconnect the relevant Codex session. Check [current Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) for the product surface you use.

## Claude Code

```sh
claude mcp add --transport stdio growth-mind-ads -- \
  uv run --project /absolute/path/to/growth-mind-ads-mcp \
  --frozen --env-file /absolute/path/to/private/ads.env growth-mind-ads-mcp
claude mcp get growth-mind-ads
```

Open Claude Code and inspect `/mcp`. The command uses the default local registration scope. See [Claude Code's official instructions](https://code.claude.com/docs/en/mcp) if you need a different scope. Don't commit real configuration into a project shared with others.

## Other local MCP clients

The equivalent process configuration is:

```json
{
  "mcpServers": {
    "growth-mind-ads": {
      "command": "/absolute/path/to/uv",
      "args": [
        "run", "--project", "/absolute/path/to/growth-mind-ads-mcp",
        "--frozen", "--env-file", "/absolute/path/to/private/ads.env",
        "growth-mind-ads-mcp"
      ]
    }
  }
}
```

This is an illustrative configuration, not a universal settings-file location. Use your client's supported configuration schema.

## First session and acceptance

1. Discover the five tools listed in OPERATIONS.md.
2. Request capabilities for the intended customer. This particular tool describes scope locally; it does not prove Google access.
3. Use your separate reporting connector for the account identity and small-report checks.
4. Load your brand workbench and the [operator instructions](../examples/OPERATOR_INSTRUCTIONS.md).
5. Require explicit human approval for `apply_approved_mutation_batch` and legacy `create_paused_batch` at the host/client level where supported.
6. Complete a separately authorized validation/application/readback exercise before claiming end-to-end acceptance.

Record client/version, server commit, connection result and read result. This repository's stdio smoke test is not a substitute for testing your actual client login. Neither the installed Codex configuration nor any existing live plugin is automatically replaced by cloning this repository.

## Remove

`codex mcp remove growth-mind-ads` or `claude mcp remove growth-mind-ads` removes the registration in that client. Revoke Google access separately when retiring the integration.

