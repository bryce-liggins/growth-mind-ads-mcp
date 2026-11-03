# Release validation

## 0.2.0 — November 3, 2026

- CPython 3.12.13 on macOS; frozen lock install and source/wheel builds passed.
- **53 unit tests passed**. Google mutations and authentication refreshes in the tests are mocked. Added cases cover local/API failures, invalid tickets, timeouts, audit write failure, secret-safe errors, budget cap enforcement, removal policy, auth failure/expiry classification and both negative examples.
- Real management-server stdio discovery and local capabilities passed without Google authentication.
- Upstream reporting commit `7452a9d49e3d350403f2610cd7125c60f6d05264` installed separately. With the explicit YAML, real stdio discovery returned exactly the three reporting tools. Tested resolved Google Ads 35.0.0 / FastMCP 4.1.6.
- Claude Code 2.1.224 registered **both servers** with the documented local-scope `uv run --project ... --frozen --env-file ...` commands in an isolated temporary configuration. Both `claude mcp get` calls reported Connected. Initial restricted runs could not use the default cache; supplying a writable temporary uv cache resolved that environment-specific failure. The operator's real Claude configuration was not edited.
- The two QUERIES.md shapes each returned one row through the existing connected reporting service after metadata discovery and authorized-account routing. No Ads validation/mutation was performed and no account rows are included in this repository.
- Public-file checks and Git diff whitespace checks passed. Gitleaks 8.30.1 directory scan reported no leaks.

### Precisely what is not verified

No live management apply, fresh OAuth sign-in, real human-permission dialog, hosted deployment, native Windows acceptance, paid headless model invocation, scheduled execution or notification delivery was performed. The auth-health code was unit-tested with mocked refresh success/failures; no token-expiry date was invented or changed. Each installation must verify actual host prompts, access and scheduled run/notification delivery.

The live query check used an existing connected reporting service, not a fresh login through the isolated upstream checkout. Negative examples passed local preparation; they still require Google validate-only and exact owner approval on real resources. Configured budget limits concern budget amounts, not an account spending guarantee. A disk failure after a remote request can still leave outcome uncertain.

# Initial 0.1.0 validation (historical)

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
