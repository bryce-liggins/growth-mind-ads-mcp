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

Unsupported types are rejected locally. Google may impose additional field, account or version restrictions. Limits: nonempty batch, at most 2,000 operations; exactly one action per operation; same-customer resource strings; positive daily budget within the owner-configured cap; explicit removal policy.

## Paused defaults and live effects

Creates for campaigns, ad groups and ads are forced paused. Positive ad-group criteria are forced paused; negative criteria are not. Budgets, assets, shared sets and other allowed resource types are not covered by a universal paused rule. Updates can enable existing objects, change budgets and alter targeting. Removals may not be reversible. Read the summary and exact operations.

## Conversion-action exceptions

A create must contain name (1–100 printable characters), type WEBPAGE, category BOOK_APPOINTMENT, countingType ONE_PER_CLICK, status ENABLED and primaryForGoal false. Optional clickThroughLookbackWindowDays is an integer from 1–90. Additional fields are rejected.

An update may contain only resourceName and boolean primaryForGoal, with updateMask exactly `primary_for_goal`. Removal is rejected. No customer-data uploads, enhanced-conversion settings or terms acceptance are implemented.

Creating an action does not install its website event or prove a conversion arrived. Making an action primary can affect bidding; inspect the account goal setup and get explicit approval.

## Audit and errors

Successful validation/application records include timestamp, customer, operation count, payload hash and result. Tickets are omitted from the saved validation result. Logs can contain account payloads; keep them private. Attempts and failures, including local rejection, are logged with an error class and sanitized outcome; raw exception text and approval phrases are omitted. If the initial audit write fails, no API call begins. If the disk fails later, the failed event may itself be unwritable; the caller receives an explicit error. Apply failures are conservatively marked unconfirmed and require readback. After a timeout or audit failure, use readback to establish state before deciding whether to retry.

## Campaign-level phrase negative

Use [campaign-phrase-negative.json](../examples/campaign-phrase-negative.json) as the validation input. Replace the fictional customer and campaign with verified resource names. The central operation is:

```json
{"campaignCriterionOperation":{"create":{
  "campaign":"customers/1234567890/campaigns/123",
  "negative":true,
  "keyword":{"text":"example competitor","matchType":"PHRASE"}
}}}
```

A phrase negative excludes searches containing those terms in that order, including extra words. It is broader than excluding one exact long-tail query. Check whether competitor traffic is deliberately targeted and whether the phrase could exclude valuable searches. Negative keywords do not automatically cover every close variant; review variants deliberately. This is an owner judgment, not a rule to block every competitor. [Google's negative-keyword explanation](https://support.google.com/google-ads/answer/2453972).

Read existing campaign criteria first and suppress duplicates. Validate the exact candidate, present its affected campaign and match scope, get the host's human approval, apply the prepared batch, then read `campaign_criterion` to verify the text, PHRASE match type and negative flag. Never feed the fictional example directly to a real account.

## Shared negative list

[shared-negative-list.json](../examples/shared-negative-list.json) illustrates three ordered operations in one batch: create a NEGATIVE_KEYWORDS shared set with temporary resource ID `-1`, create its phrase-negative criterion, and attach the set to one campaign. Temporary names connect resources within the same `GoogleAdsService.Mutate` request; they are not permanent IDs. [Google's mutate guide](https://developers.google.com/google-ads/api/docs/mutating/overview).

Inspect `shared_set`, `shared_criterion` and `campaign_shared_set` first. If a suitable set exists, use its real resource name and omit the create. If it is already attached, omit that attachment. Adding a criterion to an existing set affects **every campaign attached to it**; list all attachments in the approval summary. For multiple new attachments, add one verified campaignSharedSet operation per campaign. Do not put `negative:true` on sharedCriterion; exclusion comes from the shared set's NEGATIVE_KEYWORDS type.

Both examples pass local preparation tests. They have not been submitted as live mutations or validate-only calls in the public release. Google's validation remains required on each actual account. After apply, read the created set, criteria and campaign attachments; save real resource names privately. After timeout, read before retrying so you do not create duplicate lists.

## Budget and removal policy in 0.2.0

Budget create/update operations are disabled until the operator sets `GROWTH_MIND_ADS_MAX_BUDGET_MICROS` to a positive integer. The cap is the maximum **configured daily amount per budget**, in the target account's currency micros (one currency unit = 1,000,000 micros). Choose it with the owner. It is not a percentage-change limit, total-account cap, actual-spend cap or guarantee against Google's daily overdelivery. Shared budgets and campaign budget reassignment need separate review. Lifetime/total budgets and wildcard budget masks are rejected by this policy.

Removals default to disabled. Only deliberately permitted exact types in `GROWTH_MIND_ADS_ALLOWED_REMOVE_TYPES` can be removed, for example `campaignCriterionOperation` to remove a negative. Enabling that type does not enable campaign removal. Conversion-action removal remains unsupported. Never change local policy as a way to bypass a rejected proposed batch; obtain the owner's policy decision first. Restart and revalidate after policy changes.

## Scheduled proposal to interactive approval

The scheduled run has no management bridge and saves only the review queue. In the owner's session, reread current state, deduplicate the proposal, validate again, inspect the prepared payload, approve via the host, apply, and read back. Tickets are process-memory objects; a new session/server loses them even before the eight-hour maximum. Do not transfer tickets across sessions or extend their lifetime to solve scheduling.
