/**
 * UK Public Procurement Enriched OCDS Pipeline - TypeScript Quickstart
 * Queries the uk-public-procurement-ocds-enricher Actor on the Apify platform
 * using the official apify-client SDK.
 */

import { ApifyClient } from 'apify-client';

// Initialise the Apify client with your API token.
// Acquire your token from https://console.apify.com/account/integrations
const apifyToken = process.env.APIFY_TOKEN || 'YOUR_APIFY_TOKEN';
const client = new ApifyClient({ token: apifyToken });

async function runProcurementPipeline(): Promise<void> {
  console.log('Dispatching Actor execution to Apify platform...');

  // Configure run input parameters
  // The first 25 records on every run are free under the Pay-Per-Event evaluation tier.
  const runInput = {
    sources: ['find_a_tender', 'contracts_finder', 'public_contracts_scotland'],
    notice_type: 'award',
    min_value_gbp: 100000,
    cpv_codes: ['72000000'], // IT services classification
    enrich_companies_house: true,
    max_records: 25,
  };

  // Execute the Actor and wait for completion
  const run = await client.actor('jamestyas/uk-public-procurement-ocds-enricher').call(runInput);

  console.log(`Actor run finished with status: ${run.status}`);
  console.log(`Default Dataset ID: ${run.defaultDatasetId}`);

  // Fetch output items from the default dataset
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  console.log(`Retrieved ${items.length} procurement notices.\n`);

  for (const item of items.slice(0, 5) as any[]) {
    console.log(`OCID: ${item.ocid}`);
    console.log(`Title: ${item.title}`);
    console.log(`Buyer: ${item.buyer_name} (${item.buyer_region ?? 'N/A'})`);
    const awardVal = typeof item.award_value_gbp === 'number'
      ? `£${item.award_value_gbp.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      : 'N/A';
    console.log(`Award Value: ${awardVal}`);

    if (item.enriched && item.supplier?.companies_house_match) {
      const match = item.supplier.companies_house_match;
      console.log(`Supplier: ${item.supplier_name} (CRN: ${match.company_number})`);
      console.log(`Status: ${match.status} | Postcode: ${match.registered_postcode}`);
      if (Array.isArray(match.sic_codes) && match.sic_codes.length > 0) {
        console.log(`SIC Codes: ${match.sic_codes.join(', ')}`);
      }
      if (Array.isArray(match.active_directors) && match.active_directors.length > 0) {
        const directors = match.active_directors
          .map((d: any) => `${d.name} (${d.officer_role ?? 'director'})`)
          .join('; ');
        console.log(`Active Officers: ${directors}`);
      }
    }
    console.log('------------------------------------------------------------');
  }
}

runProcurementPipeline().catch(console.error);
