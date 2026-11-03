# Starter Google Ads reports

Both query shapes below were accepted by the connected Google Ads reporting service on November 3, 2026, with `LIMIT 1`, and each returned a row. No account data is published. This verifies those shapes on the tested account, not every account/version. The two `.gaql` files are runnable starting points; the JSON files show the corresponding `search_search` arguments with a fictional customer.

First discover resource metadata. For a new account, list accessible customers and inspect manager routing. If access fails, fix that route before changing a query that may already be valid.

## Search terms

```sql
SELECT campaign.id,
       search_term_view.ad_group,
       search_term_view.search_term,
       metrics.impressions,
       metrics.clicks,
       metrics.cost_micros,
       metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
LIMIT 1
```

Use [search-terms.gaql](../examples/queries/search-terms.gaql) or [the MCP arguments](../examples/queries/search-terms.json). `LAST_30_DAYS` is a finite window excluding today; record its resolved dates in the account timezone. For intraday reviews add an explicit today window and label it incomplete. After smoke acceptance, remove the one-row limit and verify returned row coverage/pagination. Never describe a limited response as a complete account review. Google withholds some search terms for privacy; “all returned rows” does not mean all searches.

Classify returned rows against the brand workbench, including low-impression rows. Separate clear intent mismatches from uncertain performance. Check existing campaign, ad-group and shared-list negatives before proposing additions.

## Responsive search ad assets

```sql
SELECT ad_group_ad_asset_view.ad_group_ad,
       ad_group_ad_asset_view.asset,
       asset.text_asset.text,
       ad_group_ad_asset_view.field_type,
       metrics.impressions,
       metrics.clicks,
       metrics.cost_micros,
       metrics.conversions
FROM ad_group_ad_asset_view
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
LIMIT 1
```

Use [rsa-assets.gaql](../examples/queries/rsa-assets.gaql) or [the MCP arguments](../examples/queries/rsa-assets.json). Retain asset/ad resource names and field type; group the same text only when its role, language, offer and intended audience are comparable. Remove the limit only after verifying the first response. Retrieve campaign/ad-group context separately when needed; do not silently combine unlike segments.

For a comparable message group, calculate CTR as sum(clicks)/sum(impressions), and CPA as sum(cost_micros)/1,000,000/sum(conversions). Return null when the denominator is zero. Do not average row-level CTR or CPA. Keep observed totals and the date window next to the ratios.

Several assets can share an ad impression or conversion. These are asset-associated signals, not isolated causal credit, and summing every asset will not reconstruct unduplicated account totals. Use them to choose a message hypothesis; test the next ad before declaring a causal winner. Account-level totals belong in a separate campaign/ad report.

## Saved review queue

Save account/timezone/currency, exact queries and windows, extraction time, coverage, source row/resource references, proposed action, match type, affected campaigns, reasoning, expected effect, uncertainty and current status. Use a stable key of customer + resource/scope + action + normalized proposed value to deduplicate repeated reviews. Do not save approval phrases in the queue.

Sources: [GAQL overview](https://developers.google.com/google-ads/api/docs/query/overview), [search-term fields](https://developers.google.com/google-ads/api/fields/v25/search_term_view), [RSA asset-view fields](https://developers.google.com/google-ads/api/fields/v25/ad_group_ad_asset_view).
