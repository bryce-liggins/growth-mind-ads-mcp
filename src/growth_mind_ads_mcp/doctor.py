"""Local configuration check. Never reads secret contents or calls Google."""
import json
import os
import stat
from pathlib import Path


def check():
    problems = []
    reference = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    path = Path(reference).expanduser() if reference else None
    exists = bool(path and path.is_file())
    if not exists:
        problems.append("Set GOOGLE_APPLICATION_CREDENTIALS to an existing private credential file.")
    elif os.name != "nt" and stat.S_IMODE(path.stat().st_mode) & 0o077:
        problems.append("Credential file is accessible beyond its owner; restrict it to mode 600.")
    manager = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()
    digits = manager.replace("-", "")
    if manager and (not digits.isdigit() or len(digits) != 10):
        problems.append("Login manager must contain ten digits, optionally separated by hyphens.")
    return {"configuration_ok": not problems, "credential_file_present": exists,
            "manager_header_configured": bool(manager),
            "legacy_developer_token_configured": bool(os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")),
            "google_access_tested": False, "problems": problems}


def main():
    result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["configuration_ok"] else 1)
