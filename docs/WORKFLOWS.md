# Workflow recipes

These are instructions for an agent with the appropriate connected tools, not scheduled jobs or integrations automatically installed by this package. Start with the [multi-file brand workbench](BRAND_WORKBENCH.md) and its task-specific [reading map](../examples/brand-workbench/README.md#read-only-what-the-job-needs). Save findings and proposed actions; retain human judgment.

## Search-term mining

Input: account/campaign scope, date range, current negatives, offering.md demand policy, goals.md priorities, brand-foundations.md customer context, performance.md definitions and applicable decisions.md entries.

Ask the reporting connector for all available rows/pages. Classify intent and flag business mismatches; distinguish low-volume uncertainty from obvious irrelevance. Output query, metrics, classification, reason, proposed negative/match/scope, conflicts and demand at risk. Do not automatically exclude competitor demand unless the workbench supports it. Review twice daily only if that is the owner's chosen cadence.

Acceptance: a fictional competitor query is flagged under an exclude-competitor policy but not automatically excluded under a competitor-acquisition strategy. Repeated reviews don't duplicate decisions.

## Responsive search ad analysis

Input: asset observations, dates, ad/ad-group/campaign IDs, field type, text, pinning and available metrics. Discover valid fields for the chosen API version; never fabricate missing metrics.

Group identical messages in comparable contexts, deduplicate rows and preserve original sources. Calculate CTR as total clicks / total impressions and CPA as total cost / total conversions. Do not average row-level ratios or sum overlapping different assets into campaign totals.

Fictional arithmetic check: 100 impressions/10 clicks/$20/2 conversions plus 300 impressions/15 clicks/$30/1 conversion gives 400 impressions, 25 clicks, $50, 3 conversions, 6.25% CTR and $16.67 CPA. Zero conversions means undefined CPA. These are directional observations; assets appear together. [Google asset reporting](https://support.google.com/google-ads/answer/9564897?hl=en).

Load goals.md and performance.md for interpretation; use offering.md, brand-foundations.md and taste.md for the challenger. Output: message review table, evidence limits and a proposed test linked to the owner's direction and creative examples. The operator writes/reviews the challenger.

## Landing-page production

Input: intent, proposed ad, offering.md, goals.md, brand-foundations.md, taste.md, visual-system.md, creative-library.md, asset-inventory.md, performance.md measurement requirements, repository and hosting project. Read current status and applicable decisions. Link selected proof, approved assets and the owner's strategic direction in the page brief.

Prepare a matching page, mobile behavior, crawlability, semantic/accessibility markup, performance and conversion path. Include behavior capture, completed-conversion tracking and permitted attribution. Respect consent and targeted sensitive-data protections. Test the completed action and its real destination within authorized scope. A build pass alone isn't conversion evidence. Release requires the owner's deployment authority.

## Conversion and destination monitoring

Use Ads status, destination checks and analytics diagnostics to investigate broken pages, disapproved ads, missing events and attribution changes. A quiet conversion period is not proof of broken tracking. Corroborate with technical evidence. Alert on new actionable findings; don't send repetitive unchanged updates.

## Budget pacing and allocation

Compare spend with the owner's plan, account timezone and delivery window. Inspect budget/rank constraints and mature conversion evidence. Prepare scenarios and tradeoffs. Google Smart Bidding already handles auction-time bidding; this workflow supports higher-level analysis and owner choices, not an invented competing bidder. Never apply reallocations without exact approval.

## Lead quality and revenue

Connect the correct analytics project and CRM. Define stages, revenue, currency, lag and join keys. Reconcile sample journeys before aggregate reporting. Show unmatched records. Do not assume every customer can be joined to a keyword. Offline conversion uploads are not supported by this management bridge.

## Change-impact review

Record date, affected entities, before/after values, hypothesis and owner decision for each change. Review subsequent comparable periods with conversion lag, seasonality and concurrent changes. Distinguish a plausible explanation from causal proof.

## Scheduling

Only create a schedule on request. Record provider/job ID, host, trigger, timezone, account scope, reporting windows, instruction version, output, overlap prevention, checkpoint and notification behavior. Run a real trigger and save a receipt. Configuration is not execution evidence.

## Extra connections

DataForSEO supplies market/language-specific keyword estimates; Search Console supplies organic property/query/page performance; PostHog supplies website events; a CRM supplies downstream outcomes. Each needs its own access, schema, privacy review and acceptance. They are not bundled in this repository.

## Executable starting points

- [Two verified report query shapes](QUERIES.md), including JSON MCP arguments and weighted RSA aggregation guidance.
- [Campaign phrase negative and shared-negative-list examples](OPERATIONS.md#campaign-level-phrase-negative).
- [Twice-daily schedule recipes](SCHEDULING.md), with reporting-only isolation, health alerts and durable review queues.

Scheduled runs save proposals, not tickets. Revalidate in the human's interactive session before approval/application.
