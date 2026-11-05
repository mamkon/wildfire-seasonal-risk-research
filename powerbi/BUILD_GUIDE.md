# Power BI Desktop build guide

These are preparation assets, not a PBIX, an executed DAX model or a published report. I prepared the detail-page assets first and the Executive Summary specification last. Final headlines belong to the reviewer; every supplied headline is DRAFT: verify.

## Import and model

Use the CSV route first. From the project root, rebuild exports with `python -m src.export_powerbi`. The package includes the exported CSVs in `powerbi/data` and executed notebooks in `notebooks`; the analysis tables are under `data/processed/review_tables`. Raw source data and Git object history are not included in the public review package. The full project is needed to rerun the notebooks; all supporting modules and the local research database are included in that package.

In Desktop, create a text parameter named pDataFolder, pointing privately to the exported data folder. The saved M template intentionally contains no absolute path or username. Use the labelled query blocks in power_query.m separately: parameter, function, then table queries. Keep source size as Decimal Number, not Fixed Decimal Number, and do not round it: the strict-equality Trust measures depend on the original numeric values.

Import base fact/dimension tables and size_points only. Never import the reference CSVs in validation or warehouse view exports as the report model. fact_nfd_annual is empty and disconnected until external scope is verified. size_points is a disconnected display-definition table.

Apply every relationship in model.json as one-to-many, single direction from dimension to fact. Do not add relationships between dim_year, dim_month and dim_date: that would introduce competing paths. Use dim_year for annual axes and period slicers, and its decade_label sorted by decade_start for the decade comparison, dim_month for monthly axes, and dim_date only for genuine source calendar dates. Hide keys and technical flags from report consumers. Sort month_name by month_key; exclude the Unknown month from the main season chart while retaining its explicit count.

The warehouse date dimension contains a null-date Unknown member. Do not invent a sentinel date merely to satisfy Mark as date table. If Desktop rejects marking because of that null, leave it unmarked; the supplied annual measures use integer-year logic and require no date-table time intelligence. A separate marked calendar can be considered later if a real need arises.

Report scope: years in the approved analysis_scope.json, fixed reporting agencies excluding PE. All analytical measures explicitly enforce in_analysis = 1. Do not globally filter fact_fire[in_analysis]: source-quality measures deliberately remove that flag to inspect the broader source population. Use reporting_agency_name for visible labels. These are source-agency names, not a geographic province allocation.

## Measures and display

Create measures in the order in measures.dax, keeping helpers hidden where appropriate. The manifest records expressions, intended model formats and SQL references. Numeric share measures remain numeric and unrounded; precise tooltips use them directly. The matching Label measures provide text for cards, adjacent tables and callouts.

Exact zero displays 0%; exact one displays 100%. Positive fractions below one percent display “under 1%”; fractions above ninety-nine percent and below one display “over 99%”. Alberta’s concentration share therefore displays “over 99%”, never a rounded false endpoint. The Executive range card uses “59% to over 99%” at the default scope. Negative change labels retain their direction, and missing values say Not available. Test the cases in validation/display_cases.csv.

Do not use a default numeric percentage format for on-page data labels if it can round a non-endpoint to 0% or 100%. Where a native visual cannot use the text Label measure as its data label, turn those data labels off and place the Label measure in an aligned table/card or a chart annotation. Keep precise numbers in the tooltip. Numeric axis endpoints are real scale endpoints, not rounded data claims.

Top-three-percent measures use a ceiling count and source-row key tie breaking. A bar is calculated within its agency; the pooled line uses ALLSELECTED(dim_agency), preserving explicit agency selections while removing the current bar row. MIN/MAX range helpers include only agencies with records. Pooling changes which records enter the cutoff; it is not an average of percentages.

YoY saves the single integer year, clears year/date/month filters for a full-year comparison, calculates the adjacent calendar year and returns blank for a missing/zero prior denominator or the first approved year. Rolling area averages annual sums over a complete consecutive window; incomplete initial windows and missing annual sums remain blank. It never averages individual fire sizes. Agency, cause and size filters remain active. Do not add DATEADD or SAMEPERIODLASTYEAR.

The decade mean divides full-year area by observed-year count. The no-2023 version excludes that year from both numerator and year count. Use the decade grouping and observed-year counts from the validation tables as the reference, with the recent partial period clearly labelled. Every displayed 2023 area total must carry “pending NFD reconciliation”.

Cause shares remove the cause filter from their denominator so Unknown remains in the full class denominator. NT response shares remove response-class filters from the denominator; the combined marker sums MON and MOD area over all selected NT area, including Unknown. The NT measures keep other context filters and return blank if the current agency selection excludes NT. Do not combine the classes into a treatment-outcome label.

## Layout and shared controls

Use a 1280 × 720 canvas, an eight-pixel layout grid, sixteen-pixel gutters, fifteen-pixel rounded corners, one-pixel borders and twelve-pixel inner padding. These are design choices, not dataset statistics. Use a plain-language DRAFT: verify headline, then the page-specific subtitle in pages.json. The subtitle states scope, period, agency count and definitions; codes and technical terms belong there and in tooltips, not headlines. Use Scope Subtitle and NT Scope Subtitle to expose current filter context, followed by the page-specific definition text from pages.json. These are scope labels, not dynamic headline sentences.

Use the exact dark palette in theme.json. Text must sit on the page/card background, not inside coloured bars where the contrast table fails. The light print theme uses darker variants of amber, sand and other accents to retain semantic meaning on a light background. Keep horizontal gridlines subtle; never rely on a faint grid or colour alone to convey a result. Theme JSON defaults do not guarantee every visual honours padding, shadows or corners: verify those settings in each native visual, slicer and button.

Keep a thin rust accent under the header, no photos. Navigation has a six-page main path plus an Explore button. Explore opens the three optional pages, each with Back to main story. Add Reset filters on every page and sync year, reporting agency, cause and size slicers on the detail pages. Use one Agency Detail drill-through and one report-page tooltip with a coverage warning. The coverage matrix belongs in that tooltip/technical notes, not the Trust page’s main canvas.

The NT page fixes its reporting agency and does not sync the general agency slicer. Year/cause/size filters may remain synced if their scope is stated. Headline candidates containing numeric assertions describe the default snapshot only: do not publish them as filter-responsive claims. Final wording should remain true under supported filters, or the page must be kept at the stated fixed scope. The Executive Summary uses static reviewed answer wording, not dynamic DAX headline sentences; numeric answer-card values may use measures with visible filter context.

## Detail build order, following the approved reading path

### Concentration
Use reporting_agency_name on a horizontal bar axis, Area Share Top 3 Percent as the numeric value and Pooled Top 3 Reference as the amber reference. Use the boundary-aware Label values beside bars. Annotate the within-agency range and the two endpoints, not only the pooled figure. Tooltip: precise share, records selected, total records and total agency area. Confirm the default values against validation/vw_concentration.csv. So what: use agency-specific large-event scenarios. Caveat beside the bars: ceiling cutoffs; summed reported area is not unique land.

### Trust
Use the disconnected size_points legend/columns, reporting_agency_name and Exact Size Share. Labels must say “exactly” at the small size definitions; Near Size Records is tooltip-only and separately labelled. These are recording patterns, not proof of an official agency policy. Move the coverage matrix into the technical tooltip/notes. Place a visible NFD Reconciliation Status placeholder and no numeric zero gap. Teal may mark the completed internal SQL/pandas check only. So what: check recording conventions before comparing typical sizes.

Add a compact grey evidence note beside the reconciliation placeholder: **2023 national total matches the 2025 annual report at published precision. Jurisdiction-by-year NFD reconciliation is pending.** Link to the 2023 comparison in the technical notes. Keep the recording-conventions visual as the main chart. The comparison is a fixed 2023 reference and must not respond to slicers. `validation/2023_published_summary.csv` is supporting evidence only, not a model import or a substitute for `fact_nfd_annual`.

### Change
Use dim_year on the annual area columns, Five Year Rolling Area Ha as the amber reference, and a callout for the peak year. Label that year’s area pending NFD reconciliation. Put the recent-period mean and the no-2023 mean in the callout, retaining the observed-year counts and the earlier decade means. Reference validation/vw_annual_trend.csv and the analysis CSVs for decade sensitivity. No trend-significance or causal claim. So what: test ordinary-year and extreme-year scenarios. Caveat: reporting changes and unequal periods limit interpretation.

On the 2023 tooltip, distinguish the 12-agency analysis total from the full source-year total. The full source-year count and area rounded to whole hectares match the 2025 annual report. The project excludes seven Prince Edward Island records and five Ontario records flagged as prescribed fires for that year. Do not add the official figure as a series or extrapolate the match to other years. See `../docs/reconciliation_report.md` for the separate 2024 publication figure and the remaining NFD work.

### Cause
Use paired record-share and area-share bars by cause_class, grey and rust respectively. Keep Unknown visible. Use the Label companions for page percentages; precise numeric values and denominators go in the tooltip. Validate pooled and agency-filtered contexts separately. Reporting segments are cause by month nationally; do not surface the full agency-by-cause-by-month notebook table. So what: separate frequency priorities from area-workload priorities.

### NT Response
Use the fixed Northwest Territories page, a combined NT Monitored Modified Area Share marker and separate class bars for full, modified, monitored and unknown classifications. The visible labels use full words; codes are defined in the subtitle and tooltip. Both denominators include Unknown. Validate against the NT analysis CSV, including the combined figure rather than summing rounded labels. So what: review monitored and modified classes together for the recorded workload discussion. Caveat: classifications do not measure suppression effects.

### Explore: Season
Lead with pooled monthly counts, not the agency heatmap. Use dim_month, Total Records and a filter restricting the chart to valid month keys. Annotate the highest pooled month and show Unknown Month Records beside it. Agency variation belongs in a tooltip or a secondary filtered view. So what: begin pooled seasonal workload scenarios with the peak month. Caveat: source month is not burning duration.

### Explore: Agency Scorecard
Use full reporting-agency labels, Total Area Ha, Large Fire Share and Unknown Cause Share with coverage status as explicit text. Do not create a synthetic trust or risk rank. The largest area bar is a follow-up cue, not agency performance. Percentages follow the boundary-aware display rule. So what: start follow-up with the largest submissions. Caveat: reporting agencies are not geographic provinces.

### Explore: Map
Use dim_grid rounded latitude and longitude, Total Area Ha for symbol size and a grey basemap. Do not use the reference view’s mean-source coordinates. Hide Unknown coordinates from the map and show Unmappable Records beside it. A top-five-cell callout uses Mapped Top Five Cell Share, retaining the mapped-area denominator. Do not infer risk zones, equal-area rates or provincial allocation. Map activation and native rendering remain unverified at this assets stage. So what: choose clusters for data follow-up.

### Executive Summary, last
Only after every preceding page and supported filter context is checked, create four answer cards: concentration range, recording-convention context with NFD placeholder, cause contrast and combined NT classification share. Add the annual area chart below them. Link each card to its detail page. Use the plain draft headline and scope subtitle from pages.json until the reviewer supplies final wording. No mean-versus-median opening design. Keep the 2023 pending-reconciliation note beside its chart total. Add the mobile Executive layout only after the desktop layout is checked.

## Verification before claiming the report complete

The CSV exports are checked against the warehouse, and both theme files are validated against Microsoft’s published schema. These checks do not execute DAX or prove native import/rendering. Run validation/native_checks.dax after assembly, compare every intended KPI with its SQL/pandas reference, then test slicers, Reset, navigation, drill-through, tooltips, missing categories and the display boundary cases. Record actual values and pass/fail status in validation/native_results.csv; it is currently an explicitly unexecuted template.

Add alt text and a useful tab order to every visual. Use Performance Analyzer after actual rendering; investigate any visual over the declared performance target before delivering. Before any public PBIX release, check its saved query parameters and connection metadata for private paths as well; the current assets deliberately leave the folder parameter blank. Export native screenshots into images and export the complete report using theme_light.json only after inspecting every page. No screenshot, PBIX, report.pdf, Service publication or GitHub deployment is claimed by this asset package.

## Source references for implementation

- Microsoft theme schema and release mapping: https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema
- Microsoft custom theme guidance: https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom
- DAX ALLSELECTED: https://learn.microsoft.com/en-us/dax/allselected-function-dax
- DAX TOPN and tie behaviour: https://learn.microsoft.com/en-us/dax/topn-function-dax
- DAX AVERAGEX: https://learn.microsoft.com/en-us/dax/averagex-function-dax
- Power Query CSV import: https://learn.microsoft.com/en-us/powerquery-m/csv-document

## Calculated contrast checks

Normal text requires at least 4.5:1 and essential data marks at least 3:1 in this check. Failing inside-bar pairs are deliberately not approved placements; use outside labels. Decorative container/grid contrast is not used to convey a data distinction. The requested original amber and sand had contrast below the essential-mark threshold on the print background, so the light theme uses darker print variants; the dark palette is unchanged.

| Theme | Use | Foreground | Background | Ratio | Requirement | Result |
|---|---|---|---|---:|---:|---|
| dark | title/value text | #F2E6D8 | #1A1A1E | 14.12 | 4.5 | Pass |
| dark | subtitle/axis text | #9C9690 | #1A1A1E | 5.93 | 4.5 | Pass |
| dark | data colour | #B4472B | #1A1A1E | 3.20 | 3 | Pass |
| dark | data colour | #E8A33D | #1A1A1E | 8.04 | 3 | Pass |
| dark | data colour | #1F9E89 | #1A1A1E | 5.21 | 3 | Pass |
| dark | data colour | #C8A99A | #1A1A1E | 7.93 | 3 | Pass |
| dark | data colour | #D9622B | #1A1A1E | 4.74 | 3 | Pass |
| dark | data colour | #7A6F68 | #1A1A1E | 3.55 | 3 | Pass |
| dark | inside-bar text; avoid if fails | #F2E6D8 | #B4472B | 4.41 | 4.5 | Fail: use outside labels |
| dark | inside-bar text; avoid if fails | #F2E6D8 | #E8A33D | 1.75 | 4.5 | Fail: use outside labels |
| dark | inside-bar text; avoid if fails | #F2E6D8 | #1F9E89 | 2.71 | 4.5 | Fail: use outside labels |
| dark | inside-bar text; avoid if fails | #F2E6D8 | #C8A99A | 1.78 | 4.5 | Fail: use outside labels |
| dark | inside-bar text; avoid if fails | #F2E6D8 | #D9622B | 2.98 | 4.5 | Fail: use outside labels |
| dark | inside-bar text; avoid if fails | #F2E6D8 | #7A6F68 | 3.97 | 4.5 | Fail: use outside labels |
| light | title/value text | #1A1A1E | #F7F5F2 | 15.94 | 4.5 | Pass |
| light | subtitle/axis text | #59534F | #F7F5F2 | 6.95 | 4.5 | Pass |
| light | data colour | #B4472B | #F7F5F2 | 4.98 | 3 | Pass |
| light | data colour | #8A5A00 | #F7F5F2 | 5.45 | 3 | Pass |
| light | data colour | #147865 | #F7F5F2 | 4.94 | 3 | Pass |
| light | data colour | #80685B | #F7F5F2 | 4.77 | 3 | Pass |
| light | data colour | #AC451F | #F7F5F2 | 5.32 | 3 | Pass |
| light | data colour | #6B625C | #F7F5F2 | 5.47 | 3 | Pass |
| light | inside-bar text; avoid if fails | #1A1A1E | #B4472B | 3.20 | 4.5 | Fail: use outside labels |
| light | inside-bar text; avoid if fails | #1A1A1E | #8A5A00 | 2.93 | 4.5 | Fail: use outside labels |
| light | inside-bar text; avoid if fails | #1A1A1E | #147865 | 3.23 | 4.5 | Fail: use outside labels |
| light | inside-bar text; avoid if fails | #1A1A1E | #80685B | 3.35 | 4.5 | Fail: use outside labels |
| light | inside-bar text; avoid if fails | #1A1A1E | #AC451F | 3.00 | 4.5 | Fail: use outside labels |
| light | inside-bar text; avoid if fails | #1A1A1E | #6B625C | 2.91 | 4.5 | Fail: use outside labels |
