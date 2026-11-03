# Google access and authorization

Documentation reviewed November 3, 2026. Google access requirements change; check the linked primary sources for your deployment. This repository contains no shared Google identity or account access.

## 1. Choose the account and access route

Record the target Ads customer ID, the authorizing user and, if using a manager, its login customer ID. Confirm that the user has permission to make the intended changes. A manager ID is not interchangeable with the target client ID.

## 2. Configure Cloud-project access

Create or select your own Google Cloud project, enable the Google Ads API and request the access level appropriate to test or production use. Verify approval in that project before assuming real accounts are accessible.

**Current onboarding differs from older guides:** Google's developer-token migration page says access moved to Cloud projects on September 9, 2026, and legacy token headers are optional/ignored. This public bridge accepts an optional token for old configurations. The private implementation from which it was derived required one. Do not apply through an obsolete onboarding flow merely because an old tutorial says so. [Google migration/access guide](https://developers.google.com/google-ads/api/docs/api-policy/developer-token).

## 3. Create an OAuth client and consent configuration

For the local user-authentication route, configure Google Auth Platform/consent for your actual audience, operator identity and domains; create a desktop OAuth client. Request the Ads scope, `https://www.googleapis.com/auth/adwords`. Add test users where applicable and complete the relevant publishing/verification requirements for the selected audience and scopes.

Download the client configuration into private storage, not this checkout. Do not copy Growth Mind's app identity. Use [the privacy worksheet](PRIVACY.md) for factual application documentation.

## 4. Obtain a credential file

Install Google's gcloud CLI, then use your own desktop client file to authorize the intended user. This example follows the ADC route documented by the upstream Google Ads MCP project:

```sh
gcloud auth application-default login \
  --client-id-file=/absolute/path/to/private/oauth-desktop-client.json \
  --scopes=https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
```

The owner completes the browser sign-in and consent. Record the credential-file location reported by gcloud, restrict it to the owner (`chmod 600` on macOS/Linux), and set `GOOGLE_APPLICATION_CREDENTIALS` to that absolute path in your private env file. Never print/copy its contents into chat.

This command changes the machine's default application credentials. If other work relies on those credentials, use an isolated gcloud configuration/environment or a separate credential generation flow. The server loads the explicitly configured file; it does not require replacing another application's credential file.

The OAuth client download and resulting authorized-user credential file are different files. The server needs the latter, which includes the refresh authorization. A bare desktop client-secret JSON is insufficient.

A service-account route is also supported by Google authentication libraries, but it requires its own explicit Ads access and private credentials. Follow Google's guide rather than assuming a Cloud role alone grants Ads access. The documented first-run path here is user OAuth.

## 5. Verify reads before writes

Configure a reporting MCP connector using its own versioned documentation. Start with [Google Ads MCP](https://github.com/googleads/google-ads-mcp). Its current version may expose capabilities beyond reporting; limit this initial exercise to account identity and reports.

Ask the agent to read the target customer's name, ID, timezone and currency, then retrieve a small campaign report with explicit dates. Compare the result to the intended account. Save the successful query and a private summary. Do not run a mutation to test authentication.

## 6. Validate and separately approve any first change

Follow [OPERATIONS.md](OPERATIONS.md). Google validate-only calls do not apply the batch, but they do require real access and can consume API quota. A successful validation is not authority to apply. Use a small, owner-selected change or a test account for first write acceptance, then read back the result.

## Primary sources

- [Google quick start](https://developers.google.com/google-ads/api/docs/get-started/make-first-call)
- [User authentication](https://developers.google.com/google-ads/api/docs/oauth/user-authentication)
- [Authorization and manager headers](https://developers.google.com/google-ads/api/rest/auth)
- [Brand verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification)
- [Sensitive-scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification)
- [Google Ads MCP setup](https://github.com/googleads/google-ads-mcp/blob/main/README.md)

Some Google page summaries still describe the old token requirement; the migration notice and current request-header guidance are the basis for this release. Record actual access results instead of assuming a configured project is approved.

## Production authorization checkpoint: avoid weekly sign-in failures

Create **your own** Cloud project and OAuth app. “Growth Mind Ads Operations” is Growth Mind's app name, not an app readers must connect to or copy.

Before enabling recurring reviews, inspect Google Auth Platform → Audience. For an External app using Ads scopes, finish the applicable requirements and publish **In production**, then authorize again and verify a refresh. An eligible Workspace organization-only app can use **Internal**; having a Workspace address alone does not make an external audience internal. Record the actual audience and publishing status.

External apps left in Testing issue refresh tokens that expire after seven days for this scope. Production removes that Testing restriction; it does **not** set a fixed 180-day lifetime. Six months of non-use is one revocation condition, not a guaranteed six-month validity period. User revocation, administrator policy and other conditions can invalidate access sooner. Do not assume an already issued Testing token is extended after publication. [Google's refresh-token lifecycle](https://developers.google.com/identity/protocols/oauth2#expiration).

Production publishing and brand verification are distinct from scope/access verification. Complete the requirements applicable to your audience; this checklist does not promise Google approval.

## Authentication health and alerts

After installation, run this with your private reporting credentials:

```sh
uv run --frozen --env-file /absolute/path/to/private/reporting.env \
  growth-mind-ads-auth-health
```

This refreshes authentication against Google; it does not query or modify Ads. It returns sanitized JSON and a nonzero exit on a warning/failure. `invalid_grant` becomes `reauthorization_required`; network problems become `connection_failed`. A successful refresh alone does not prove Ads account permissions: follow it with the tiny report.

Only if Google or your administrator supplies an actual refresh-authorization expiry, pass `--known-refresh-expiry` with its ISO timestamp including timezone. The checker warns within seven days. Never substitute the short-lived **access-token** expiry or an invented 180-day date. When refresh expiry is unknown, advance expiry prediction is unavailable; the next scheduled health check detects failure instead.

The command emits a notification signal; it does not send email or install a background job. The [schedule recipe](SCHEDULING.md) tells the host to surface changed failures, known-expiry warnings, and recovery in its task inbox. Verify host notifications during setup. An optional 180-day access review is an operator maintenance choice, not an OAuth lifetime change.
