"""
UK Public Procurement Enriched OCDS Pipeline - LlamaIndex Integration
Defines a function tool for LlamaIndex agents querying the
uk-public-procurement-ocds-enricher Actor on the Apify platform.
"""

import os
from typing import List, Optional
from apify_client import ApifyClient

# Acquire your token from https://console.apify.com/account/integrations
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)


def search_uk_public_contracts(
    sources: Optional[List[str]] = None,
    notice_type: str = "award",
    min_value_gbp: int = 50000,
    cpv_codes: Optional[List[str]] = None,
    enrich_companies_house: bool = True,
    max_records: int = 25,
) -> List[dict]:
    """
    Search UK government contracts and tenders across Find a Tender, Contracts Finder,
    and Public Contracts Scotland, enriched with Companies House corporate verification.
    
    Args:
        sources: List of platforms ('find_a_tender', 'contracts_finder', 'public_contracts_scotland').
        notice_type: Lifecycle type ('tender', 'award', 'modification', 'all').
        min_value_gbp: Minimum contract threshold in GBP.
        cpv_codes: CPV category classification codes.
        enrich_companies_house: Enable corporate intelligence enrichment.
        max_records: Maximum records to return (first 25 free).
    """
    if sources is None:
        sources = ["find_a_tender", "contracts_finder", "public_contracts_scotland"]

    run_input = {
        "sources": sources,
        "notice_type": notice_type,
        "min_value_gbp": min_value_gbp,
        "cpv_codes": cpv_codes or [],
        "enrich_companies_house": enrich_companies_house,
        "max_records": max_records,
    }

    run = client.actor("jamestyas/uk-public-procurement-ocds-enricher").call(run_input=run_input)
    items = client.dataset(run["defaultDatasetId"]).list_items().items
    return items


if __name__ == "__main__":
    print("Testing LlamaIndex query wrapper...")
    notices = search_uk_public_contracts(
        sources=["contracts_finder"],
        notice_type="award",
        min_value_gbp=100000,
        max_records=5,
    )
    print(f"Retrieved {len(notices)} contract awards.")
