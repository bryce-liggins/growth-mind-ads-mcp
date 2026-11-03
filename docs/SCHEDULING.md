# Set up twice-daily Google Ads reviews

This is an installation recipe, not an already running schedule. Example times are 09:00 and 15:00, every day, in `America/New_York`. Have the owner choose timezone, working days, account scope and alert thresholds. This schedule reviews and proposes; it never applies account changes.

## Prepare a reporting-only review project

1. Create a private review directory with the brand workbench, approved account routing and KPI definitions. Keep write credentials and the management bridge out of the scheduled environment. Prefer a separate Ads user with Read-only access.
2. Install [REPORTING.md](REPORTING.md). Verify the three-tool discovery check. Inspect inherited client/plugin registrations too: the management bridge must not appear.
3. Run [authentication health](GOOGLE_SETUP.md#authentication-health-and-alerts) and one small [query](QUERIES.md) manually. Save the result without credential values. This separates authentication from account-access errors.
4. Copy the prompt below into the scheduler. Replace every bracketed value. Store outputs in a private persistent directory, not an ephemeral worktree that disappears between runs.
5. Run once manually before enabling recurrence. Confirm findings reach the task inbox. Test notification handling with a synthetic failed-health result; do not revoke working credentials to test it.

## Reusable review prompt

```text
Review Google Ads for [approved customer IDs and manager route].
Use [absolute brand-workbench path] and [absolute KPI/routing path].
Save output under [absolute private review directory].

First inspect available tools. Stop and report a configuration failure if
any Ads mutation tool or management bridge is available. Use only reporting.
Run the configured authentication health command, then a tiny account read.
If either fails, mark the run failed and report the sanitized cause; do not
label missing data as zero activity and do not change credentials yourself.

Review all returned search-term rows for yesterday and today, plus a rolling
30-day context window in the account timezone. Label today incomplete.
Confirm extraction coverage; do not silently use a one-row smoke limit.
Compare intent with the brand workbench and existing exclusions. Prepare
negative-keyword proposals with exact match type and campaign/shared-list
scope. Analyze comparable repeated RSA messages using weighted metrics.
Check the owner's pacing, conversion and destination-health thresholds.
Account for conversion lag and record missing integrations explicitly.

Save a timestamped receipt and update review-queue.md. Deduplicate by
customer + resource/scope + action + proposed value. Preserve owner decisions.
Do not validate changes, issue tickets, apply changes or deploy pages.
Flag stale proposals for rechecking in the owner's interactive session.

Notify in the task inbox only for new actionable findings, changed failures,
known refresh-expiry warnings, or recovery. Remain quiet when unchanged.
Never include tokens, credential contents or approval phrases in output.
```

The host must have a way to run the health command. In a shell-restricted headless deployment, have the scheduler wrapper run it before the agent instead. Use its JSON status and exit code. Persist last notified status privately; a first failure and recovery warrant notification, identical failures do not need duplicate alerts. Surface missed/failed scheduled runs in the scheduler's own run history as well.

## Codex desktop automation

In a dedicated reporting-only project/session, ask Codex:

```text
Create a standalone local scheduled task named Google Ads review.
Run every day at 09:00 and 15:00 America/New_York using the review prompt
and private paths we just tested. Use only the reporting connector;
the management bridge must be absent. Save the schedule ID, full prompt,
timezone, recurrence and notification behavior in schedule.md.
```

Confirm the saved recurrence corresponds to `FREQ=DAILY;BYHOUR=9,15;BYMINUTE=0;BYSECOND=0` in the chosen timezone. If the UI supports only one daily time, create two tasks and record both IDs. Test Run now, then inspect its actual output and tool list. Keep the machine awake and the desktop app running for local jobs. Availability and labels vary by product/workspace. [Official scheduled-task documentation](https://learn.chatgpt.com/docs/automations?surface=app).

## Claude Code Desktop scheduled task

Use a private reporting-only project. In Claude Code Desktop's scheduled-task interface, create a task using the tested prompt, project and local environment. Set daily 09:00 and 15:00 in the chosen timezone; if the form offers one time per task, create two tasks. Inspect effective MCP servers and permissions before enabling. Test a manual run, verify private outputs and inbox notifications, and record both task IDs/settings in `schedule.md`. Local execution requires the computer running.

Use [Claude's current scheduling guide](https://code.claude.com/docs/en/scheduled-tasks) and its linked Desktop instructions. `/loop` is session-scoped; it is not the durable twice-daily setup described here. Cloud tasks do not automatically have your local stdio processes or private files.

## Claude Code CLI: strict reporting-only invocation

For a host scheduler running Claude Code headlessly, create a private MCP JSON file containing **only** `google-ads`, with the same command/args as CLIENTS.md and reporting.env. Then the core agent invocation is:

```sh
claude -p --strict-mcp-config \
  --mcp-config /absolute/path/to/private/reporting-only.mcp.json \
  --tools "" \
  --allowedTools mcp__google-ads__customers_list_accessible_customers \
    mcp__google-ads__metadata_get_resource_metadata mcp__google-ads__search_search \
  --output-format text < /absolute/path/to/private/resolved-review-prompt.txt \
  > /absolute/path/to/private/current-review.txt
```

This disables built-in shell/file tools, loads only the named MCP config, and allows only the three reporting calls. The scheduler wrapper must supply the brand workbench/KPIs/previous queue in the input file, run the health check, check exit status, archive timestamped output, deduplicate the queue, and deliver permitted notifications. The command alone is not a full persistent scheduler. Avoid inherited plugins/hooks in this dedicated profile, and inspect effective settings. No paid model invocation was run as part of this release.

## Acceptance and handoff

Record provider/job ID, active/paused state, exact prompt, timezone/DST behavior, machine/runtime, credentials reference (not value), output paths, manual run and first scheduled run evidence, failure routing and deduplication. Configuration is not proof of execution. Retest after client/server updates. If a run is missed, report it and perform one catch-up review with explicit windows; do not blindly replay account changes.

Morning proposals do not carry approval tickets. The owner's later session rereads state and validates again under [OPERATIONS.md](OPERATIONS.md).
