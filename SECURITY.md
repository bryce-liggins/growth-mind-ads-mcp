# Security and trust boundaries

This is a local, single-operator stdio server. Do not expose it as a public HTTP service or share its process across untrusted users without building and reviewing independent authentication, tenant isolation and authorization.

## What the code checks

- Only allowlisted operation types/actions are accepted. Budget edits require a configured per-budget daily cap; removals are disabled unless the operator explicitly allows their exact operation type.
- Resource strings beginning with `customers/` must match the selected customer.
- New campaigns, ad groups, ads and positive ad-group criteria are forced paused.
- A normalized customer/payload ticket is required, expires after eight hours and can be consumed once.
- Google validateOnly runs before ticket issuance and immediately before a live apply.
- Attempted, successful and failed validation/application outcomes are recorded locally; approval ticket text is excluded from the audit record.

## What it does not guarantee

The ticket does **not** authenticate a human. An agent able to call both tools can obtain and use it. The user/host must enforce approval for both apply tools. This is not a separate signed approval service or a complete multi-party control.

Credentials determine which accounts the process can access; the server does not maintain an additional customer allowlist. Cross-resource checks do not stop an authorized credential from being used on another target customer. Bind the host's workflow to the intended account.

Google validation checks API validity, not business wisdom, budget affordability or statistical significance. Negative keywords, updates, removals, assets and shared resources can affect live campaigns. Paused defaults cover only the documented create types.

Audit writing is not transactional with Google. A remote write may succeed and then local logging fail. Network timeouts can also leave outcome uncertain. Read state before retrying. No automatic rollback or idempotency key is supplied. Failures are logged with sanitized error classes. An unavailable audit file blocks API work before it begins; disk failure after a remote call can still prevent its failure/success receipt from being saved.

## Credentials and data

The public repository must never contain credential JSON, OAuth secrets, access/refresh tokens, developer-token values, real client identifiers, reports or runtime logs. Environment-variable names and fictional fixtures are not credentials.

New audit directories/files use restrictive POSIX modes, but existing directory/file permissions are not automatically repaired. Audit records may include prepared account operations and Google response metadata. Treat them as private client data. Keep their location outside any public repository and define retention/deletion.

The server sends requests to Google; it does not itself call an LLM API. Your agent host can send tool inputs/results to its provider. Document that actual data flow. Neither this server nor its license makes a promise about the host's retention or training policies.

## Reporting a vulnerability

Do not open a public issue containing secrets, client data or an exploitable confidential account example. Use GitHub's private vulnerability reporting if enabled on this repository; otherwise contact the maintainer through an established private channel. Ordinary reproducible bugs can use sanitized fictional fixtures.

If a real credential leaks, revoke/rotate it and address exposed files/history/copies. Deleting the latest file does not undo disclosure. [GitHub guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).


## Concrete host controls

Follow [CLIENTS.md](docs/CLIENTS.md) for Claude ask rules covering both apply tools, and [SCHEDULING.md](docs/SCHEDULING.md) for reporting-only scheduled runs with no management bridge. These rules do not sandbox arbitrary shell code that has access to write credentials.
