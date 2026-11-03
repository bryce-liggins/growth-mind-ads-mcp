# Installation and maintenance

## Supported baseline

Python 3.11+; the lock and initial local test use Python 3.12. The instructions use macOS/Linux shell syntax. Windows users can use WSL or adapt paths and access controls; native Windows has not been verified. No Docker, Railway or paid hosting is needed for this local server.

Install Git and uv from their official documentation. Clone the repository and run `uv sync --frozen` from its directory. This creates an isolated `.venv` and installs the exact resolved versions in `uv.lock`. The server package is installed locally; no PyPI publication is required.

Run the two no-credential checks in the README. Expected results: all unit tests pass; smoke test prints the five expected tool names and `google_calls: false`.

## Private configuration

Keep credentials outside the repository. Example on macOS/Linux:

```sh
mkdir -p "$HOME/.config/growth-mind-ads"
chmod 700 "$HOME/.config/growth-mind-ads"
cp .env.example "$HOME/.config/growth-mind-ads/ads.env"
chmod 600 "$HOME/.config/growth-mind-ads/ads.env"
```

Edit that file locally. Replace the credential path with an absolute path to your authorized-user or supported service-account credential JSON from [Google setup](GOOGLE_SETUP.md). Set a login manager only when using manager access.

| Variable | Purpose |
| --- | --- |
| GOOGLE_APPLICATION_CREDENTIALS | Required absolute path to the credential JSON; not the JSON text |
| GOOGLE_ADS_LOGIN_CUSTOMER_ID | Optional manager ID, required for the manager-access route |
| GOOGLE_ADS_DEVELOPER_TOKEN | Optional legacy header; current Google onboarding uses Cloud-project API access |
| GROWTH_MIND_ADS_AUDIT_DIR | Optional private audit directory; defaults to ~/.local/share/growth-mind-ads-mcp |

The target customer is a tool argument, not the login manager. Do not put real values into an example file, chat message, screenshot, issue or public commit.

Run the doctor command from the README. It checks file existence/permissions and manager-ID shape without reading the credential contents or calling Google. A passing doctor does not prove account authorization.

## Launch

```sh
uv run --project /absolute/path/to/growth-mind-ads-mcp \
  --frozen --env-file /absolute/path/to/private/ads.env growth-mind-ads-mcp
```

A manually launched stdio server can appear idle because it is waiting for an MCP client. Use [CLIENTS.md](CLIENTS.md) to register it. Keep diagnostics on stderr; stdout belongs to the MCP protocol.

## Update

Review changes, back up private configuration separately, then pull the intended revision and run `uv sync --frozen`, tests and smoke check again. Restart the MCP connection. Restarting clears pending approval tickets; revalidate and review rather than attempting to reuse them. Record the commit and lockfile for reproducibility. Do not casually upgrade FastMCP across a major version.

## Uninstall and revoke

Remove the MCP registration from the client and stop its process. Removing a connector does not revoke Google access. Revoke the app's authorization in your Google account or remove the relevant account permission; separately remove service-account access if that was your route. Delete private credentials and logs according to your retention requirements. Delete the checkout/virtual environment when no longer needed.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| uv not found in a desktop client | Use its absolute executable path from `command -v uv`; desktop apps may have a different PATH |
| Credential file missing | Expand the path before putting it in the env file; use an absolute path |
| Google rejects authentication | User, credential type, Ads scope, consent state and revoked/expired refresh token |
| Google rejects access | Cloud-project API access, intended target, user permission and manager header |
| Tools list but report fails | Tool discovery is local; it does not verify Google access |
| Approval unknown/expired | Restart, prior use or time limit; validate and obtain approval again |
| Google response times out | Read the account state before retrying; a write may have succeeded remotely |
| Audit write fails after apply | Reconcile Google state before retrying. Local logging is not a distributed transaction |
| API version rejected | v25 is pinned in server.py; review Google's sunset schedule before migrating and retest operation schemas |

Do not post raw credentials, approval phrases or account responses in public issues.

