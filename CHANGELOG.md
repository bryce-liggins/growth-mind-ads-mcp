# Changelog

## 0.2.0 — 2026-11-03

- Add sanitized attempt/failure auditing and fail closed when the initial audit record cannot be written.
- Require owner-configured per-budget daily cap; make removal types opt-in (breaking defaults).
- Add authentication health command; no fabricated fixed refresh-token lifetime.
- Add verified reporting-only configuration, both Claude registrations, human ask rules and isolated scheduling recipes.
- Add live-read-tested query shapes, fictional negative examples, own-app setup and v25 sunset month.


## 0.1.0 — 2026-11-03

Initial public package derived from Growth Mind's local Google Ads management bridge.

- Portable Python package, locked dependencies and stdio entry point.
- Fictional test fixtures and generic account-owner approval instructions.
- Optional legacy developer-token header and optional manager header for current Cloud-project onboarding/direct-account access.
- Private configurable audit location, restrictive creation permissions and approval-ticket redaction.
- Configuration doctor, unit regressions and local MCP smoke check.
- Google, client, operator, privacy, security and workflow documentation.

The running private plugin was not replaced. No live Google mutation was performed as part of preparing this release.

