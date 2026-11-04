# Connect Codex or Claude Code

Install the [management bridge](INSTALLATION.md), [Google credentials](GOOGLE_SETUP.md), and the separate [reporting connector](REPORTING.md) first. Use your own absolute paths and the absolute path to `uv` when a desktop app cannot find it. The commands below keep credential values in private env files. Both servers use local stdio.

## Claude Code: register both servers

Run from your private operator project. Local scope keeps these registrations tied to that project. Do not register the change bridge in a scheduled-review project.

```sh
claude mcp add --transport stdio --scope local google-ads -- \
  uv run --project /absolute/path/to/google-ads-mcp \
  --frozen --env-file /absolute/path/to/private/reporting.env google-ads-mcp
claude mcp add --transport stdio --scope local growth-mind-ads -- \
  uv run --project /absolute/path/to/growth-mind-ads-mcp \
  --frozen --env-file /absolute/path/to/private/ads.env growth-mind-ads-mcp
claude mcp get google-ads
claude mcp get growth-mind-ads
```

Use `/mcp` in a fresh Claude session and inspect the tools. MCP servers are registered through `claude mcp add`; do not put an `mcpServers` object in `~/.claude/settings.json`. Permissions, in contrast, do belong in a supported settings file. [Claude MCP documentation](https://code.claude.com/docs/en/mcp).

The registration and connection commands were exercised with Claude Code 2.1.224 in an isolated temporary profile, without changing the operator's real configuration. See [the validation record](VALIDATION.md) for the distinction between connection tests and human-prompt/live-write acceptance.

## Claude Code: require a human at both apply tools

Merge this fragment into your private operator project's `.claude/settings.local.json`, preserving existing settings. An example is also in [claude-approval-settings.json](../examples/claude-approval-settings.json).

```json
{
  "permissions": {
    "ask": [
      "mcp__growth-mind-ads__apply_approved_mutation_batch",
      "mcp__growth-mind-ads__create_paused_batch"
    ]
  }
}
```

These names assume the registration name `growth-mind-ads`. Rename the rules if you rename the server. Remove apply tools from allowlists. Keep normal interactive permissions; do not use `bypassPermissions`, `--dangerously-skip-permissions`, or an equivalent host bypass. Inspect `/permissions`; verify these two exact rules are present. Claude evaluates deny before ask before allow. [Permission rules](https://code.claude.com/docs/en/permissions).

Acceptance requires a real host permission prompt before execution of **each** apply route. Do not test a real account mutation just to check a dialog: use a disposable no-write mock server exposing the same tool names, or test as part of a separately approved account change. Registration tests do not prove this dialog appeared. If your host cannot guarantee the prompt, leave the change bridge disconnected and apply through a separately controlled operator process.

The host gate controls these MCP calls. It does not stop unrestricted shell code from using readable write credentials directly. Do not grant unattended or untrusted agents a shell plus write credentials. See [SECURITY.md](../SECURITY.md).

## Codex: register both servers

```sh
codex mcp add google-ads -- \
  uv run --project /absolute/path/to/google-ads-mcp \
  --frozen --env-file /absolute/path/to/private/reporting.env google-ads-mcp
codex mcp add growth-mind-ads -- \
  uv run --project /absolute/path/to/growth-mind-ads-mcp \
  --frozen --env-file /absolute/path/to/private/ads.env growth-mind-ads-mcp
codex mcp list
```

Restart/reconnect, inspect tools, and verify the read-only tool set. Use your installed Codex surface's tool-approval controls to require owner confirmation for both apply tools. Do not transplant Claude's settings schema into Codex. If the surface cannot enforce that boundary, use a read-only agent and a separately controlled apply session. [Current Codex MCP instructions](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Scheduled and headless clients

Do **not** register `growth-mind-ads`, including its validation tools. A schedule saves a review queue, not a ticket. Use [SCHEDULING.md](SCHEDULING.md) for an isolated reporting configuration and concrete twice-daily recipes. Inherited global/user/plugin registrations count: inspect actual discovery, not only a project file.

## First read and first change

1. List accessible accounts. Establish the intended target, manager route, timezone and currency; do not assume an old account ID remains accessible.
2. Run the small reports in [QUERIES.md](QUERIES.md).
3. Load [the brand workbench](../examples/brand-workbench/README.md) and [operator instructions](../examples/OPERATOR_INSTRUCTIONS.md).
4. For an owner-requested change, follow [OPERATIONS.md](OPERATIONS.md), verify the host approval prompt, and read back the result.
5. Record client/version, commit, permission configuration, read result and any untested step.

To remove a registration, use `claude mcp remove NAME` with the matching scope, or `codex mcp remove NAME`. Revoke Google access separately when retiring the integration.
