"""
UK Public Procurement Enriched OCDS Pipeline - Python Quickstart
Queries the uk-public-procurement-ocds-enricher Actor on the Apify platform
using the official apify-client SDK.
"""

import os
from apify_client import ApifyClient

# Initialise the Apify client with your API token.
# Acquire your token from https://console.apify.com/account/integrations
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN")

client = ApifyClient(APIFY_TOKEN)

# Configure run input parameters
# The first 25 records on every run are free under the Pay-Per-Event evaluation tier.
run_input = {
    "sources": [
        "find_a_tender",
        "contracts_finder",
        "public_contracts_scotland",
    ],
    "notice_type": "award",
    "min_value_gbp": 100000,
    "cpv_codes": ["72000000"],  # IT services classification
    "enrich_companies_house": True,
    "max_records": 25,
}

print("Dispatching Actor execution to Apify platform...")
run = client.actor("jamestyas/uk-public-procurement-ocds-enricher").call(run_input=run_input)

print(f"Actor run finished with status: {run['status']}")
print(f"Default Dataset ID: {run['defaultDatasetId']}")

# Fetch output items from the default dataset
dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
print(f"Retrieved {len(dataset_items)} procurement notice records.\n")

for item in dataset_items[:5]:
    print(f"OCID: {item.get('ocid')}")
    print(f"Title: {item.get('title')}")
    print(f"Buyer: {item.get('buyer_name')} ({item.get('buyer_region', 'N/A')})")
    award_val = item.get("award_value_gbp")
    if award_val is not None:
        print(f"Award Value: £{award_val:,.2f}")
    else:
        print("Award Value: N/A")

    if item.get("enriched"):
        ch_match = item.get("supplier", {}).get("companies_house_match", {})
        print(f"Supplier: {item.get('supplier_name')} (CRN: {ch_match.get('company_number')})")
        print(f"Status: {ch_match.get('status')} | Postcode: {ch_match.get('registered_postcode')}")
        sic_codes = ch_match.get("sic_codes", [])
        if sic_codes:
            print(f"SIC Codes: {', '.join(sic_codes)}")
        directors = [d.get("name") for d in ch_match.get("active_directors", []) if d.get("name")]
        if directors:
            print(f"Active Directors: {'; '.join(directors)}")
    print("-" * 60)
