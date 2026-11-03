# Exact-batch operations

## Tools

| Tool | Arguments | Effect |
| --- | --- | --- |
| get_write_capabilities | customer_id | Local description only; no Google request |
| validate_mutation_batch | customer_id, operations | Prepare and Google-validate a batch; return prepared operations, summary and ticket |
| apply_approved_mutation_batch | customer_id, operations, approval_phrase | Consume ticket, revalidate, apply, write successful result; caller must read back |
| validate_create_batch | customer_id, operations | Compatibility route restricted to creates |
| create_paused_batch | customer_id, operations, approval_phrase | Compatibility apply route for creates; not every resource is pausable |

All customer examples use fictional `1234567890`; do not submit example IDs to Google. Select your actual account deliberately.

## Workflow

1. Read current state through the reporting connector. Record exact resource names and pre-change values.
2. Prepare the smallest coherent batch. Each operation has one allowed operation type and one create/update/remove action. Updates require a nonempty REST `updateMask`; use the current Google API field specification.
3. Validate. Save `prepared_operations`, customer, payload hash and operation summary. The server can normalize create statuses, so review the returned prepared payload, not only your input.
4. Present exact scope, expected effect, costs/live consequences and rollback limits to the account owner. Wait for explicit approval of this specific batch.
5. Apply the unchanged prepared payload with its returned approval phrase. Do not synthesize a phrase from the example format. A changed customer/payload, expired ticket, consumed ticket or restarted server requires validation and a new review.
6. Read the affected account resources and compare with the approved result. Save evidence. A response saying `readback_required` is a reminder, not a completed verification.

No automatic retries after uncertain application; inspect state first. The Google request uses `partialFailure: false`, but this does not turn logging, owner review, remote state and retries into one transaction.

## Fictional example: pause an existing campaign

```json
{
  "customer_id": "1234567890",
  "operations": [
    {
      "campaignOperation": {
        "update": {
          "resourceName": "customers/1234567890/campaigns/123",
          "status": "PAUSED"
        },
        "updateMask": "status"
      }
    }
  ]
}
```

This illustrates the validation input shape only. A pause affects live delivery. Obtain actual resource names from reads and approval from the owner before application.

## Allowed operation types

campaignBudgetOperation, campaignOperation, adGroupOperation, adGroupAdOperation, adGroupCriterionOperation, campaignCriterionOperation, assetOperation, customerAssetOperation, campaignAssetOperation, adGroupAssetOperation, sharedSetOperation, sharedCriterionOperation, campaignSharedSetOperation, customerNegativeCriterionOperation, conversionActionOperation.

Unsupported types are rejected locally. Google may impose additional field, account or version restrictions. Limits: nonempty batch, at most 2,000 operations; exactly one action per operation; same-customer resource strings; positive create budget.

## Paused defaults and live effects

Creates for campaigns, ad groups and ads are forced paused. Positive ad-group criteria are forced paused; negative criteria are not. Budgets, assets, shared sets and other allowed resource types are not covered by a universal paused rule. Updates can enable existing objects, change budgets and alter targeting. Removals may not be reversible. Read the summary and exact operations.

## Conversion-action exceptions

A create must contain name (1–100 printable characters), type WEBPAGE, category BOOK_APPOINTMENT, countingType ONE_PER_CLICK, status ENABLED and primaryForGoal false. Optional clickThroughLookbackWindowDays is an integer from 1–90. Additional fields are rejected.

An update may contain only resourceName and boolean primaryForGoal, with updateMask exactly `primary_for_goal`. Removal is rejected. No customer-data uploads, enhanced-conversion settings or terms acceptance are implemented.

Creating an action does not install its website event or prove a conversion arrived. Making an action primary can affect bidding; inspect the account goal setup and get explicit approval.

## Audit and errors

Successful validation/application records include timestamp, customer, operation count, payload hash and result. Tickets are omitted from the saved validation result. Logs can contain account payloads; keep them private. Errors and pre-validation rejection are not guaranteed to be logged. After a timeout or audit failure, use readback to establish state before deciding whether to retry.

