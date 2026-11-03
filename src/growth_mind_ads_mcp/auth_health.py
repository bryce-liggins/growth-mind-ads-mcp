"""Refresh authentication without Ads mutations; emit sanitized monitoring JSON."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone, timedelta

import google.auth
from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport.requests import Request

SCOPE = "https://www.googleapis.com/auth/adwords"


def check(known_refresh_expiry: str | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    result = {"status": "healthy", "refresh_expiry_known": False,
              "notification_required": False, "ads_access_tested": False}
    if known_refresh_expiry:
        try:
            expiry = datetime.fromisoformat(known_refresh_expiry.replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                raise ValueError("timezone required")
            result["refresh_expiry_known"] = True
            result["known_refresh_expiry"] = expiry.isoformat()
            if expiry <= now + timedelta(days=7):
                result.update(status="expiry_warning", notification_required=True)
        except (TypeError, ValueError):
            return {**result, "status": "invalid_expiry_configuration", "notification_required": True}
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not path:
        return {**result, "status": "credentials_missing", "notification_required": True}
    try:
        credentials, _ = google.auth.load_credentials_from_file(path, scopes=[SCOPE])
        credentials.refresh(Request())
        if not credentials.token:
            raise RefreshError("no access token")
    except RefreshError as error:
        # Classify locally; never return error text (it can contain private data).
        status = "reauthorization_required" if "invalid_grant" in str(error) else "authentication_failed"
        result.update(status=status, notification_required=True)
    except TransportError:
        result.update(status="connection_failed", notification_required=True)
    except Exception:
        result.update(status="credential_configuration_failed", notification_required=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--known-refresh-expiry", help="Only a real provider/admin-supplied ISO timestamp with timezone; never an access-token expiry")
    args = parser.parse_args()
    result = check(args.known_refresh_expiry)
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "healthy" else 1)


if __name__ == "__main__":
    main()
