"""
UK Public Procurement Enriched OCDS Pipeline - LangChain Integration
Defines a LangChain StructuredTool querying the uk-public-procurement-ocds-enricher
Actor on the Apify platform.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from apify_client import ApifyClient

# Acquire your token from https://console.apify.com/account/integrations
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)


class ProcurementQueryInput(BaseModel):
    sources: List[str] = Field(
        default=["find_a_tender", "contracts_finder", "public_contracts_scotland"],
        description="Public procurement platforms: find_a_tender, contracts_finder, public_contracts_scotland.",
    )
    notice_type: str = Field(
        default="award",
        description="Lifecycle notice type: tender, award, modification, or all.",
    )
    min_value_gbp: int = Field(
        default=0,
        description="Minimum contract monetary threshold in British Pounds (GBP).",
    )
    cpv_codes: Optional[List[str]] = Field(
        default=[],
        description="Common Procurement Vocabulary (CPV) codes, e.g. ['72000000'] for IT.",
    )
    enrich_companies_house: bool = Field(
        default=True,
        description="Whether to enrich winning suppliers with Companies House corporate intelligence.",
    )
    max_records: int = Field(
        default=25,
        description="Maximum records to retrieve (first 25 records are free per run).",
    )


def query_uk_procurement(
    sources: List[str] = ["find_a_tender", "contracts_finder", "public_contracts_scotland"],
    notice_type: str = "award",
    min_value_gbp: int = 0,
    cpv_codes: Optional[List[str]] = None,
    enrich_companies_house: bool = True,
    max_records: int = 25,
) -> dict:
    """Queries live UK public procurement notices and enriches winning suppliers with Companies House records."""
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

    return {
        "status": run["status"],
        "total_records": len(items),
        "dataset_id": run["defaultDatasetId"],
        "records": items,
    }


if __name__ == "__main__":
    print("Executing demonstration query via LangChain tool schema...")
    results = query_uk_procurement(
        sources=["find_a_tender"],
        notice_type="award",
        min_value_gbp=250000,
        cpv_codes=["72000000"],
        enrich_companies_house=True,
        max_records=5,
    )
    print(f"Retrieved {results['total_records']} notices successfully.")
