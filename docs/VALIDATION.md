# Release validation

Release 0.1.0, November 3, 2026.

## Recorded checks

- macOS Apple Silicon, CPython 3.12.13.
- Locked installation with uv succeeded. Direct versions: FastMCP 2.14.7, google-auth 2.62.1 and requests 2.34.2; complete graph in uv.lock.
- 35 unit tests passed. Google mutations were mocked. Coverage includes prepared statuses, cross-account references, conversion restrictions, ticket binding/reuse/expiry, revalidation, optional authentication headers, audit-ticket redaction and local configuration checks.
- Real stdio subprocess discovery returned all five tools; get_write_capabilities returned successfully for a fictional ID without a Google request.
- Source distribution and wheel built successfully.
- A second clean directory installed the frozen lock successfully, then passed all 35 tests and the real stdio smoke check.
- Gitleaks 8.30.1 scanned the release files and found no leaks; the downloaded official scanner archive matched its published checksum.
- The public-file check found no private file names, personal home paths, non-fixture account IDs or broken relative documentation links. Explicit checks against the original private fixture identifiers and client labels found no matches. These checks reduce risk; they are not a guarantee against every possible secret.

## Limits

No live Google authorization, validate-only request or mutation was performed for this public release. Neither Codex nor Claude Code's actual user configuration was overwritten or used for a fresh login. Their setup syntax is documented; each installer must verify their own route. No native Windows verification, hosted/multi-user deployment, production penetration test, or performance/ROI claim.

The tests cover the described behaviors, not every possible Google operation or provider outage. FastMCP's pinned dependency tree emits upstream Authlib deprecation notices; tests and stdio discovery still pass. Revisit compatible dependency updates deliberately rather than removing the version constraint without testing.
