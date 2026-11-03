#!/usr/bin/env python3
"""Approval-gated Google Ads MCP mutation bridge."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request as UrlRequest, urlopen

import google.auth
from fastmcp import FastMCP
from google.auth.transport.requests import Request as AuthRequest


API_VERSION = "v25"
API_ROOT = f"https://googleads.googleapis.com/{API_VERSION}"
ADWORDS_SCOPE = "https://www.googleapis.com/auth/adwords"
AUDIT_DIR = Path(os.environ.get("GROWTH_MIND_ADS_AUDIT_DIR", str(Path.home() / ".local" / "share" / "growth-mind-ads-mcp"))).expanduser()
AUDIT_FILE = AUDIT_DIR / "audit.jsonl"
MAX_OPERATIONS = 2_000
# Long enough for an owner to approve during a normal working session without
# weakening the other guarantees: tickets remain payload-bound, single-use,
# process-local, and are revalidated immediately before application.
APPROVAL_TTL_SECONDS = 8 * 60 * 60
PENDING_APPROVALS: dict[str, dict[str, Any]] = {}

ALLOWED_OPERATION_TYPES = {
    "campaignBudgetOperation",
    "campaignOperation",
    "adGroupOperation",
    "adGroupAdOperation",
    "adGroupCriterionOperation",
    "campaignCriterionOperation",
    "assetOperation",
    "customerAssetOperation",
    "campaignAssetOperation",
    "adGroupAssetOperation",
    "sharedSetOperation",
    "sharedCriterionOperation",
    "campaignSharedSetOperation",
    "customerNegativeCriterionOperation",
    "conversionActionOperation",
}

MUTATION_ACTIONS = {"create", "update", "remove"}

# Narrow owner-approved extension: manual website completed-booking actions only.
# New actions are secondary, so adding one cannot silently opt it into bidding.
CONVERSION_CREATE_REQUIRED_FIELDS = {
    "name", "type", "category", "countingType", "primaryForGoal", "status"
}
CONVERSION_CREATE_OPTIONAL_FIELDS = {"clickThroughLookbackWindowDays"}


def _validate_conversion_create(payload: dict[str, Any], index: int) -> None:
    fields = set(payload)
    missing = CONVERSION_CREATE_REQUIRED_FIELDS - fields
    unexpected = fields - CONVERSION_CREATE_REQUIRED_FIELDS - CONVERSION_CREATE_OPTIONAL_FIELDS
    if missing or unexpected:
        raise ValueError(
            f"Operation {index} website booking create has missing fields {sorted(missing)} "
            f"or unsupported fields {sorted(unexpected)}"
        )
    name = payload["name"]
    if not isinstance(name, str) or not name.strip() or len(name) > 100 or any(
        ord(character) < 32 for character in name
    ):
        raise ValueError(f"Operation {index} conversion name must be 1-100 printable characters")
    expected = {
        "type": "WEBPAGE", "category": "BOOK_APPOINTMENT",
        "countingType": "ONE_PER_CLICK", "status": "ENABLED"
    }
    for field, value in expected.items():
        if payload[field] != value:
            raise ValueError(f"Operation {index} conversion create requires {field}={value}")
    if payload["primaryForGoal"] is not False:
        raise ValueError(f"Operation {index} new conversion actions must be secondary (primaryForGoal=false)")
    window = payload.get("clickThroughLookbackWindowDays", 30)
    if type(window) is not int or not 1 <= window <= 90:
        raise ValueError(f"Operation {index} click-through window must be an integer from 1 to 90 days")

# New servable entities remain paused unless they are exclusions. Existing entities
# may be updated (including enabled) only through the exact-payload approval flow.
ALWAYS_FORCE_PAUSED_ON_CREATE = {
    "campaignOperation",
    "adGroupOperation",
    "adGroupAdOperation",
}

mcp = FastMCP(
    "google-ads-write",
    instructions=(
        "Approval-gated Google Ads management bridge. Always validate the exact mutation batch "
        "first, show the customer, prepared operations, and risk summary to the account owner, and wait for "
        "their explicit approval. Only then call apply_approved_mutation_batch with the unchanged "
        "payload and exact payload-bound approval phrase returned by validation. New campaigns, "
        "ad groups, ads, and positive ad-group criteria are forced to PAUSED. Negative criteria "
        "may be created live. Successful validations and applications are audit logged."
    ),
)


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _normalize_customer_id(customer_id: str) -> str:
    normalized = "".join(ch for ch in str(customer_id) if ch.isdigit())
    if len(normalized) != 10:
        raise ValueError("customer_id must contain exactly 10 digits")
    return normalized


def _access_token() -> str:
    credentials_path = _required_env("GOOGLE_APPLICATION_CREDENTIALS")
    credentials, _ = google.auth.load_credentials_from_file(
        credentials_path,
        scopes=[ADWORDS_SCOPE],
    )
    credentials.refresh(AuthRequest())
    if not credentials.token:
        raise RuntimeError("Google authentication returned no access token")
    return credentials.token


def _canonical_operations(operations: list[dict[str, Any]]) -> str:
    return json.dumps(operations, sort_keys=True, separators=(",", ":"))


def _payload_sha256(operations: list[dict[str, Any]]) -> str:
    return hashlib.sha256(_canonical_operations(operations).encode()).hexdigest()


def _approval_digest(customer_id: str, operations: list[dict[str, Any]]) -> str:
    digest = _payload_sha256(operations)[:16].upper()
    return f"{customer_id}:{digest}"


def _issue_approval_phrase(customer_id: str, operations: list[dict[str, Any]]) -> str:
    digest = _approval_digest(customer_id, operations)
    nonce = secrets.token_hex(4).upper()
    phrase = f"APPROVE GOOGLE ADS MUTATION {customer_id} {digest.split(':')[1]} {nonce}"
    PENDING_APPROVALS[phrase] = {
        "digest": digest,
        "expires_at": time.time() + APPROVAL_TTL_SECONDS,
    }
    return phrase


def _consume_approval_phrase(
    approval_phrase: str, customer_id: str, operations: list[dict[str, Any]]
) -> None:
    ticket = PENDING_APPROVALS.pop(approval_phrase, None)
    if ticket is None:
        raise ValueError(
            "Approval phrase is unknown or already used. Validate the exact batch again."
        )
    if ticket["expires_at"] < time.time():
        raise ValueError("Approval phrase expired. Validate the exact batch again.")
    if ticket["digest"] != _approval_digest(customer_id, operations):
        raise ValueError(
            "Approval phrase mismatch. The customer or prepared payload changed; validate again."
        )


def _assert_customer_owned_resource_names(value: Any, customer_id: str, path: str) -> None:
    """Reject cross-account resource names anywhere in a mutation payload."""
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_customer_owned_resource_names(child, customer_id, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_customer_owned_resource_names(child, customer_id, f"{path}[{index}]")
        return
    if isinstance(value, str) and value.startswith("customers/"):
        expected_prefix = f"customers/{customer_id}/"
        if not value.startswith(expected_prefix):
            raise ValueError(
                f"{path} references a different customer; expected prefix {expected_prefix}"
            )


def _force_safe_create_status(operation_type: str, create_payload: dict[str, Any]) -> bool:
    if operation_type in ALWAYS_FORCE_PAUSED_ON_CREATE:
        create_payload["status"] = "PAUSED"
        return True
    if operation_type == "adGroupCriterionOperation" and not create_payload.get("negative", False):
        create_payload["status"] = "PAUSED"
        return True
    return False


def _prepare_for_customer(
    customer_id: str,
    operations: list[dict[str, Any]],
    *,
    create_only: bool = False,
) -> tuple[list[dict[str, Any]], int]:
    if not operations:
        raise ValueError("operations must contain at least one mutation")
    if len(operations) > MAX_OPERATIONS:
        raise ValueError(f"A single batch may not exceed {MAX_OPERATIONS:,} operations")

    prepared: list[dict[str, Any]] = []
    forced_paused_count = 0
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict) or len(operation) != 1:
            raise ValueError(f"Operation {index} must contain exactly one operation type")

        operation_type, body = next(iter(operation.items()))
        if operation_type not in ALLOWED_OPERATION_TYPES:
            raise ValueError(f"Operation {index} uses disallowed type: {operation_type}")
        if not isinstance(body, dict):
            raise ValueError(f"Operation {index} body must be an object")

        action_keys = MUTATION_ACTIONS.intersection(body)
        if len(action_keys) != 1:
            raise ValueError(
                f"Operation {index} must contain exactly one of create, update, or remove"
            )
        action = next(iter(action_keys))
        if create_only and action != "create":
            raise ValueError(f"Operation {index} must be create-only")
        if operation_type == "conversionActionOperation" and action == "remove":
            raise ValueError(f"Operation {index} conversion action removal is not allowed")

        allowed_body_keys = {action, "updateMask"} if action == "update" else {action}
        unexpected = set(body) - allowed_body_keys
        if unexpected:
            raise ValueError(
                f"Operation {index} contains unsupported fields: {sorted(unexpected)}"
            )

        clean_body = json.loads(json.dumps(body))
        if action == "create":
            create_payload = clean_body["create"]
            if not isinstance(create_payload, dict):
                raise ValueError(f"Operation {index} create payload must be an object")
            if operation_type == "conversionActionOperation":
                _validate_conversion_create(create_payload, index)
            if _force_safe_create_status(operation_type, create_payload):
                forced_paused_count += 1
            if operation_type == "campaignBudgetOperation":
                amount = int(create_payload.get("amountMicros", 0))
                if amount <= 0:
                    raise ValueError(
                        f"Operation {index} campaign budget must be greater than zero"
                    )
        elif action == "update":
            update_payload = clean_body["update"]
            if not isinstance(update_payload, dict):
                raise ValueError(f"Operation {index} update payload must be an object")
            resource_name = update_payload.get("resourceName")
            if not isinstance(resource_name, str) or not resource_name:
                raise ValueError(f"Operation {index} update requires resourceName")
            update_mask = clean_body.get("updateMask")
            if not isinstance(update_mask, str) or not update_mask.strip():
                raise ValueError(f"Operation {index} update requires a non-empty updateMask")
            if operation_type == "conversionActionOperation":
                if set(update_payload) != {"resourceName", "primaryForGoal"}:
                    raise ValueError(
                        f"Operation {index} conversion action update permits only "
                        "resourceName and primaryForGoal"
                    )
                if not re.fullmatch(
                    rf"customers/{customer_id}/conversionActions/[1-9][0-9]*",
                    resource_name,
                ):
                    raise ValueError(
                        f"Operation {index} conversion action requires a resourceName "
                        "in this customer"
                    )
                if type(update_payload["primaryForGoal"]) is not bool:
                    raise ValueError(f"Operation {index} primaryForGoal must be a boolean")
                if update_mask != "primary_for_goal":
                    raise ValueError(
                        f"Operation {index} conversion action updateMask must be "
                        "exactly primary_for_goal"
                    )
        else:
            remove_resource = clean_body["remove"]
            if not isinstance(remove_resource, str) or not remove_resource:
                raise ValueError(f"Operation {index} remove must be a resource name")

        prepared_operation = {operation_type: clean_body}
        _assert_customer_owned_resource_names(
            prepared_operation, customer_id, f"operations[{index}]"
        )
        prepared.append(prepared_operation)

    return prepared, forced_paused_count


def _operation_summary(
    operations: list[dict[str, Any]], forced_paused_count: int
) -> dict[str, Any]:
    action_counts: Counter[str] = Counter()
    operation_type_counts: Counter[str] = Counter()
    status_updates: Counter[str] = Counter()
    negative_keyword_creates = 0
    budget_operations = 0
    conversion_goal_updates: Counter[str] = Counter()
    conversion_action_creates = 0

    for operation in operations:
        operation_type, body = next(iter(operation.items()))
        action = next(iter(MUTATION_ACTIONS.intersection(body)))
        action_counts[action] += 1
        operation_type_counts[operation_type] += 1
        if operation_type == "campaignBudgetOperation":
            budget_operations += 1
        payload = body.get(action)
        if action == "update" and isinstance(payload, dict) and "status" in payload:
            status_updates[str(payload["status"])] += 1
        if operation_type == "conversionActionOperation":
            if action == "create":
                conversion_action_creates += 1
            elif action == "update":
                conversion_goal_updates[
                    "PRIMARY" if payload["primaryForGoal"] else "SECONDARY"
                ] += 1
        if action == "create" and isinstance(payload, dict):
            if operation_type in {
                "campaignCriterionOperation",
                "adGroupCriterionOperation",
                "customerNegativeCriterionOperation",
            } and payload.get("negative", False) and "keyword" in payload:
                negative_keyword_creates += 1

    return {
        "action_counts": dict(sorted(action_counts.items())),
        "operation_type_counts": dict(sorted(operation_type_counts.items())),
        "forced_paused_creates": forced_paused_count,
        "negative_keyword_creates": negative_keyword_creates,
        "status_updates": dict(sorted(status_updates.items())),
        "budget_operations": budget_operations,
        "conversion_goal_updates": dict(sorted(conversion_goal_updates.items())),
        "secondary_website_booking_creates": conversion_action_creates,
        "remove_operations": action_counts["remove"],
    }


def _audit(
    event: str, customer_id: str, operations: list[dict[str, Any]], result: Any
) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "customer_id": customer_id,
        "operation_count": len(operations),
        "payload_sha256": _payload_sha256(operations),
        "result": {key: value for key, value in result.items() if key != "approval_phrase"}
        if isinstance(result, dict) else result,
    }
    fd = os.open(AUDIT_FILE, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, separators=(",", ":")) + "\n")


def _mutate(
    customer_id: str, operations: list[dict[str, Any]], validate_only: bool
) -> dict[str, Any]:
    payload = {
        "mutateOperations": operations,
        "partialFailure": False,
        "validateOnly": validate_only,
        "responseContentType": "RESOURCE_NAME_ONLY",
    }
    headers = {
        "Authorization": f"Bearer {_access_token()}",
        "Content-Type": "application/json",
    }
    # Cloud-project access replaces developer tokens for current Google onboarding.
    # Keep the optional legacy header for existing configurations.
    developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip()
    if developer_token:
        headers["developer-token"] = developer_token
    login_customer = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()
    if login_customer:
        headers["login-customer-id"] = _normalize_customer_id(login_customer)
    request = UrlRequest(
        f"{API_ROOT}/customers/{customer_id}/googleAds:mutate",
        data=json.dumps(payload).encode(),
        method="POST",
        headers=headers,
    )
    try:
        with urlopen(request, timeout=120) as response:
            raw = response.read().decode()
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"Google Ads API error {error.code}: {detail}") from error


def _validate_batch(
    customer_id: str,
    operations: list[dict[str, Any]],
    *,
    create_only: bool = False,
) -> dict[str, Any]:
    customer = _normalize_customer_id(customer_id)
    prepared, forced_paused_count = _prepare_for_customer(
        customer, operations, create_only=create_only
    )
    result = _mutate(customer, prepared, validate_only=True)
    summary = {
        "validated": True,
        "applied": False,
        "customer_id": customer,
        "operation_count": len(prepared),
        "payload_sha256": _payload_sha256(prepared),
        "approval_phrase": _issue_approval_phrase(customer, prepared),
        "approval_expires_in_seconds": APPROVAL_TTL_SECONDS,
        "operation_summary": _operation_summary(prepared, forced_paused_count),
        "prepared_operations": prepared,
        "google_response": result,
        "next_step": (
            "Show the account owner the exact customer, prepared_operations, and operation_summary. Wait for "
            "explicit approval, then apply this unchanged payload with the returned approval_phrase."
        ),
    }
    _audit("validate_mutation", customer, prepared, summary)
    return summary


def _apply_batch(
    customer_id: str,
    operations: list[dict[str, Any]],
    approval_phrase: str,
    *,
    create_only: bool = False,
) -> dict[str, Any]:
    customer = _normalize_customer_id(customer_id)
    prepared, forced_paused_count = _prepare_for_customer(
        customer, operations, create_only=create_only
    )
    _consume_approval_phrase(approval_phrase, customer, prepared)
    validation = _mutate(customer, prepared, validate_only=True)
    result = _mutate(customer, prepared, validate_only=False)
    summary = {
        "validated_first": True,
        "applied": True,
        "customer_id": customer,
        "operation_count": len(prepared),
        "payload_sha256": _payload_sha256(prepared),
        "operation_summary": _operation_summary(prepared, forced_paused_count),
        "validation_response": validation,
        "google_response": result,
        "readback_required": True,
    }
    _audit("apply_mutation", customer, prepared, summary)
    return summary


@mcp.tool()
def get_write_capabilities(customer_id: str) -> dict[str, Any]:
    """Describe the bridge's management scope and non-bypassable approval workflow."""
    customer = _normalize_customer_id(customer_id)
    return {
        "customer_id": customer,
        "api_version": API_VERSION,
        "mode": "approval-gated-management",
        "allowed_operation_types": sorted(ALLOWED_OPERATION_TYPES),
        "allowed_actions": sorted(MUTATION_ACTIONS),
        "conversion_action_limit": (
            "conversionActionOperation may create only secondary WEBPAGE/BOOK_APPOINTMENT "
            "actions with ONE_PER_CLICK and ENABLED status; optional click-through window "
            "is 1-90 days. Existing actions may update only primaryForGoal with updateMask "
            "primary_for_goal. Removal, other fields, enhanced-data settings, customer-data "
            "uploads and customer-data terms acceptance are not supported."
        ),
        "forced_paused_create_types": sorted(ALWAYS_FORCE_PAUSED_ON_CREATE),
        "positive_ad_group_criteria_forced_paused": True,
        "live_negative_criterion_creates_allowed": True,
        "approval_flow": [
            "Read current account state with the read-only Google Ads connector.",
            "Call validate_mutation_batch with the complete proposed batch.",
            "Show the account owner the exact customer, prepared operations, and risk summary.",
            "Wait for the account owner's explicit approval.",
            "Call apply_approved_mutation_batch with the unchanged batch and validation phrase.",
            "Read the changed resources back and reconcile them.",
        ],
        "approval_phrase_note": (
            "Approval phrases are issued only after successful validation, expire after 8 "
            "hours, are single-use, and are bound to the exact customer and normalized payload."
        ),
        "audit_file": str(AUDIT_FILE),
    }


@mcp.tool()
def validate_mutation_batch(
    customer_id: str, operations: list[dict[str, Any]]
) -> dict[str, Any]:
    """Validate an exact create/update/remove batch without changing Google Ads.

    Present the returned prepared_operations and operation_summary to the account owner and wait for their
    explicit approval. Do not call the apply tool in the same turn unless the account owner had already
    approved this exact customer and payload.
    """
    return _validate_batch(customer_id, operations)


@mcp.tool()
def apply_approved_mutation_batch(
    customer_id: str,
    operations: list[dict[str, Any]],
    approval_phrase: str,
) -> dict[str, Any]:
    """Apply an exact batch only after the account owner explicitly approves the validated payload.

    The phrase is bound to the normalized customer and prepared operations. Any payload change
    invalidates it. The bridge reruns validateOnly immediately before the live mutation.
    """
    return _apply_batch(customer_id, operations, approval_phrase)


@mcp.tool()
def validate_create_batch(
    customer_id: str, operations: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compatibility tool: validate a create-only batch and return a payload-bound phrase."""
    return _validate_batch(customer_id, operations, create_only=True)


@mcp.tool()
def create_paused_batch(
    customer_id: str,
    operations: list[dict[str, Any]],
    approval_phrase: str,
) -> dict[str, Any]:
    """Compatibility tool: apply an approved create-only batch with safe paused defaults."""
    return _apply_batch(customer_id, operations, approval_phrase, create_only=True)


def main() -> None:
    """Start the local stdio MCP server; no HTTP listener is exposed."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
