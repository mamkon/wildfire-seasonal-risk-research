# Reconciliation report

## Internal: passed
I compared every SQL reference view with separate pandas calculations. The machine-readable comparison results are in data/processed/internal_reconciliation.json. Fixture-based pytest checks repeat those comparisons without the full raw dataset. The full source check runs separately after the warehouse build.

I allow small floating-point differences using the explicit tolerances in src/reconcile.py. Record counts, keys and categories still have to agree. A meaningful difference fails the comparison rather than being explained away.

## External: pending, not a test failure or an agreement claim
I have not obtained the official NFD tables and their scope footnotes. fact_nfd_annual is empty. I have not invented totals or used CNFDB values as an independent reference. The current reference extraction entry point is https://national-forestry-database.ca/en/data/fires.php. No manually downloaded NFD exports were found in data/reference/ on November 5, 2026.

CNFDB reporting agencies are not geographic jurisdictions. Parks Canada spans jurisdictions. Before joining external totals, I need either verified matching reporting scope or a justified allocation method. I will not add Parks Canada to provincial figures without checking whether those figures already include it.

Once comparable exports are available, I will report the count and area differences and percentage gaps for each matched jurisdiction, year and category. Scope, minimum size, revisions, mapping and Parks Canada treatment could explain differences, but I have not diagnosed a cause without the reference data. External discrepancies will be reported, not forced to zero.

## Secondary published-summary check: 2023

The official 2024 report's online indicator lists 6,811 fires and 17,197,201 hectares. Against the approved project scope of 6,825 records and 17,606,408.222897924 hectares, the differences are 14 records and 409,207.222897924 hectares, or approximately 2.3795% of that published area. The 2025 report lists 6,837 fires and 17,606,547 hectares instead. Both are retained as distinct publication vintages. The reasons for changes between those publications have not been established here.

The full CNFDB source-year total, before project exclusions, matches the 2025 report's count and rounded area. This is a national published-summary comparison. It does not complete independent NFD jurisdiction-by-year reconciliation or justify a general claim that the database is accurate because its totals are close. The 2023 label remains “pending NFD reconciliation”.

- 2024 online indicator: https://prod-natural-resources.azure.cloud.nrcan-rncan.gc.ca/forests-forestry/state-canada-forests/disturbance-canadas-forests
- 2025 report: https://prod-natural-resources.azure.cloud.nrcan-rncan.gc.ca/forests-forestry/state-canada-forests/state-canada-s-forests-annual-report-2025
