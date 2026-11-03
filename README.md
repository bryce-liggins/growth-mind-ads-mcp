# Growth Mind Ads MCP

Manage supported Google Ads changes from an AI agent through a local MCP server. Built from Growth Mind's operating workflow: read the account, prepare a specific change, validate it, get the account owner's approval, apply the unchanged batch, and read the result back.

**This is the management bridge, not a complete marketing platform.** Pair it with a [reporting-only configuration](docs/REPORTING.md) of a connector such as [Google's Google Ads MCP](https://github.com/googleads/google-ads-mcp). Your brand workbench supplies the customer, offer, voice and goals. Separate tools provide your website, CRM, analytics and keyword data.

## Start here

- **Installing with an agent?** Give it [docs/AGENT_SETUP.md](docs/AGENT_SETUP.md).
- **Installing yourself?** Follow [installation](docs/INSTALLATION.md), [Google access](docs/GOOGLE_SETUP.md), then [Codex/Claude configuration](docs/CLIENTS.md).
- **Using the tools?** Read [the exact change protocol](docs/OPERATIONS.md) and [workflow recipes](docs/WORKFLOWS.md).
- **Writing application documents?** Use [the privacy and app-description worksheet](docs/PRIVACY.md).
- **Checking the trust boundary?** Read [SECURITY.md](SECURITY.md) before allowing writes.

## Quick local check (no Google credentials needed)

Requires Git, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+. The repository selects Python 3.12.

```sh
git clone https://github.com/bryce-liggins/growth-mind-ads-mcp.git
cd growth-mind-ads-mcp
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python scripts/smoke_mcp.py
```

The tests mock Google calls. The smoke test starts a real local MCP process, discovers its five tools and requests capabilities using a fictional customer ID. It neither authenticates to Google nor changes an account.

After [Google setup](docs/GOOGLE_SETUP.md), check configuration without exposing values:

```sh
uv run --frozen --env-file /absolute/path/to/private/ads.env growth-mind-ads-doctor
```

Then register the server in your chosen agent client. The server speaks **stdio**, not HTTP; it does not open a public listener.

## Supported operations

Supported operation families cover budgets, campaigns, ad groups, ads, criteria, assets/associations and shared negative sets. Budget edits require an owner-configured daily amount cap per budget. Removals are disabled unless the owner explicitly allows their operation type. New campaigns, ad groups, ads and positive ad-group criteria are forced paused. Negatives and some other resources can affect live delivery immediately after application.

Conversion actions are deliberately narrow: create a secondary completed-booking website action, or change an existing action's primary/secondary role. No offline customer-data uploads, conversion-action removal, billing or account-user management. [Full operation reference](docs/OPERATIONS.md).

## Approval is a workflow, not an independent human signature

Validation produces a single-use, eight-hour ticket bound to the normalized customer and payload. Application consumes that ticket and validates with Google again before writing.

**The server cannot prove that a human approved. An agent with both tools can request and consume a ticket.** Use the [concrete client permission recipe](docs/CLIENTS.md) to require the account owner's approval before either apply tool, and don't give untrusted agents unrestricted credentials. Paused-create defaults do not protect against every live effect. See [SECURITY.md](SECURITY.md).

## Reports, recurring reviews and maintenance

Use the [starter queries](docs/QUERIES.md), [negative-keyword examples](docs/OPERATIONS.md#campaign-level-phrase-negative) and [twice-daily schedule recipes](docs/SCHEDULING.md). Scheduled runs are reporting-only and save proposals; the human session validates again before approval. Create your own Google app and complete [the production authorization checkpoint](docs/GOOGLE_SETUP.md#production-authorization-checkpoint-avoid-weekly-sign-in-failures). The included authentication health command can signal failures and known expiry warnings to your scheduler.

The bridge uses Google Ads API v25, scheduled to sunset **August 2027** (exact day not yet announced). [Maintenance instructions](docs/INSTALLATION.md#version-maintenance-and-policy-changes).

## What is verified

This release includes mocked operation/approval tests, configuration/header/audit tests, and a real local stdio discovery test. See [VALIDATION.md](docs/VALIDATION.md) for recorded results and limits. Automated tests do not establish live Google access, a successful account mutation, marketing performance, or successful sign-in inside every agent product.

The package does not install a scheduler, deploy a website, connect a CRM, or provision your Google application. The documentation walks through those boundaries and the evidence to collect.

## License and attribution

MIT, copyright 2026 Bryce Liggins. Dependencies retain their own licenses; see [THIRD_PARTY.md](docs/THIRD_PARTY.md). This is an independent Growth Mind project, not an official Google, OpenAI or Anthropic product.

