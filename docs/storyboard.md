# Storyboard for review

Status: proposal only. Every candidate headline remains **DRAFT: verify**. I have not started Power BI. The supporting quantities are calculated from the approved warehouse; native visuals, DAX and filter behaviour still require verification.

## Navigation and build order

The main story has six pages: **Executive Summary → Concentration → Trust → Change → Cause → NT Response**.

An **Explore** button opens three optional pages: **Season → Agency Scorecard → Map**. Each Explore page has a **Back to main story** button. Explore does not interrupt the main reading path. Navigation names are functional labels; the candidate finding titles below are the proposed chart/page headlines.

**Build the Executive Summary last**, after the other pages and their filter states are verified. Its four answer cards summarize existing evidence, rather than introducing additional findings.

## Shared scope and display rules

I use the approved fixed-reporting-agency scope in `data/analysis_scope.json`. Reporting agency is not geographic province. Counts are reported records, not verified unique incidents. Every visual states its period and denominator.

**On-page percentages use whole numbers, except that nonzero values under 1% display “under 1%” and values over 99% but below 100% display “over 99%”. Display 0% or 100% only for exact endpoints. Tooltips retain precise values**, the numerator and denominator, the selected period and relevant scope note. Rounding is for display only; calculations and comparisons retain source precision. Rounded shares may not sum to the displayed total. Tables below distinguish proposed on-page labels from tooltip evidence.

Rust represents reported-area burden. Amber represents averages and reference lines. Teal marks a specific completed check, such as internal reconciliation; it never labels an entire agency trusted or a place safe. Grey represents context, missingness and unverified coverage. Colour is supported by labels.

Each detail page has one main message, one main visual and a callout on that visual. The **so what** is a plain decision position. Caveats sit beside the visual in a short line, not inside the so-what statement. NFD reconciliation is shown as a labelled placeholder until official matching totals are available. The 2023 reported-area total remains **pending NFD reconciliation** wherever displayed.

## Main story: Executive Summary, built last

- **Decision question:** What should I take into a planning discussion after reviewing the detail?
- **Candidate headline:** DRAFT: verify: Large events matter, and recording differences matter too.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land.
- **Main visual and why:** Four answer cards, for concentration, trust, cause and NT response, above the annual reported-area chart. This opening page is the deliberate summary exception to the single-main-visual detail-page layout. Remove the mean-versus-median opening design. The annual chart supplies time context; the cards link to their supporting pages.
- **Chart annotation:** On the annual chart, point to 2023: 17.61 million reported ha, pending NFD reconciliation. Use the card wording specified below only after verifying the detail pages.
- **So what:** I would plan for unusually large recorded events and review each agency’s recording context.
- **Caveat beside the visual:** “Selected reporting records; the 2023 total is pending NFD reconciliation.”
- **Look next:** Concentration, or use an answer card to open its supporting page.
- **Evidence and tooltip detail:** vw_kpi_summary, vw_concentration, vw_annual_trend and the NT classification table. Final wording is deferred until the other pages pass verification.

### Executive answer-card candidates, all provisional

| Card | Candidate text on the page | Tooltip evidence |
|---|---|---|
| Concentration | DRAFT: verify: The largest events account for 59% to over 99% of the area within each agency. | Precise range 59.46%–99.56%; pooled reference 96.21%; cutoff and denominator definitions. |
| Trust | DRAFT: verify: Small recorded-size patterns differ across agencies. | Strict counts and shares at the requested sizes; near-value diagnostics labelled separately. NFD reconciliation: pending. |
| Cause | DRAFT: verify: Natural causes account for 46% of recorded events and 87% of the area. | Exact shares 46.15% and 86.65%, with Unknown included in both denominators. |
| NT response | DRAFT: verify: Monitored and modified response classes together account for 90% of the area. | Exact combined share 90.06%; separate classes and all-NT area denominator, including Unknown. |

## Main story: Concentration

- **Decision question:** Does the pooled concentration figure describe each reporting agency?
- **Candidate headline:** DRAFT: verify: The largest events account for 59% to over 99% of the area within each agency.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land. Largest share: ceiling of 3% of records within each agency; source-row ties.
- **Main visual and why:** Horizontal bars of within-agency top-three-percent area shares, with the pooled share as an amber reference. This shows the range directly instead of presenting one pooled figure as universal.
- **Chart annotation:** Call out YT at 59% and Alberta’s reporting agency at over 99%; label the pooled reference 96%. State that each bar uses its own agency’s records and area.
- **So what:** I would use agency-specific large-event scenarios rather than one pooled concentration assumption.
- **Caveat beside the visual:** “Cutoffs round upward; reported-area sums are not unique land.”
- **Look next:** Trust: inspect the recording patterns behind the comparison.
- **Evidence and tooltip detail:** vw_concentration and pooling_comparison.csv. Precise range 59.46%–99.56%, pooled 96.21%. The notebook explains pooled membership versus the 86.37% area-weighted agency-specific selections.

## Main story: Trust

- **Decision question:** Are recorded small sizes comparable across reporting agencies?
- **Candidate headline:** DRAFT: verify: Small fire sizes appear differently across agencies.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land. Strict SIZE_HA equality at 0, 0.01 and 0.1 ha; near-values kept separate.
- **Main visual and why:** An agency comparison of shares at exactly 0, 0.01 and 0.1 ha, with labelled categories and distinct patterns or shades. These values are exact size definitions, not percentages to round. This directly exposes recording patterns. Move the coverage matrix into a tooltip or technical notes, not the main canvas.
- **Chart annotation:** Point to the strongest contrasting exact-value patterns in the checked agency table, and label their whole-number shares. Add “strict equality” on the chart; put separately labelled near-value checks in the tooltip.
- **So what:** I would check recording conventions before comparing typical fire sizes across agencies.
- **Caveat beside the visual:** “Heaping does not establish agency policy; near-values are separate diagnostics.”
- **Look next:** Change: read annual and decade comparisons with that recording context.
- **Evidence and tooltip detail:** review_tables/heaping.csv and the data-quality notebook. Tooltips show exact counts, denominators and unrounded percentages. Show “Jurisdiction-by-year NFD reconciliation: pending.” Beside it, add a grey note that the full 2023 source-year count and rounded area match the 2025 annual report. Keep the comparison fixed to 2023 and separate from chart filters. Teal is reserved for the completed internal SQL/pandas check.

## Main story: Change

- **Decision question:** How much of the recent-period difference depends on the largest year?
- **Candidate headline:** DRAFT: verify: Removing the largest year narrows the recent gap, but does not close it.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land. Decade means use observed years; 2023 total pending NFD reconciliation.
- **Main visual and why:** Annual reported-area columns with an amber rolling reference. A compact annotation compares observed-year decade means and the recent-period sensitivity. The main message is sensitivity of the recent comparison, not a statistical trend.
- **Chart annotation:** Point to 2023: 17.61 million reported ha, pending NFD reconciliation. Label the 2020–2025 mean 6.26M ha across six years and 3.99M ha across five years excluding 2023. Show the earlier decade means alongside them.
- **So what:** I would test plans against both ordinary-year and extreme-year workload scenarios.
- **Caveat beside the visual:** “Descriptive comparisons; reporting changes and unequal period lengths limit interpretation.”
- **Look next:** Cause: separate frequency from reported-area burden.
- **Evidence and tooltip detail:** vw_annual_trend, vw_decades and decade_sensitivity.csv. The 2000s and 2010s annual means are 1.74M and 2.91M reported ha, over ten years each; the 2020s comparison is partial. Do not imply a causal, significance-tested or reporting-adjusted trend. Initial incomplete rolling windows remain blank.

## Main story: Cause

- **Decision question:** Do frequent recorded causes carry the same share of reported area?
- **Candidate headline:** DRAFT: verify: Natural causes account for fewer events but most of the recorded area.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land. Source causes: H human, N natural/lightning, U unknown; unknown included.
- **Main visual and why:** Paired horizontal cause-class bars, grey for record-share context and rust for reported-area burden. The paired values show why count and area questions need different answers.
- **Chart annotation:** Point to Natural/lightning: 46% of records versus 87% of area. Retain Unknown as a separate labelled row.
- **So what:** I would separate prevention-frequency priorities from reported-area workload priorities.
- **Caveat beside the visual:** “Recorded classifications include unknowns; these shares are not causal effects.”
- **Look next:** NT Response, or Explore for optional season, agency and map detail.
- **Evidence and tooltip detail:** vw_cause. Tooltips retain 46.15% and 86.65%, plus counts, hectares and denominators. Reporting segments remain cause by month nationally; the full agency-level segment table stays in the notebook only.

## Main story: NT Response

- **Decision question:** How much selected NT reported area lies in MON and MOD response classifications?
- **Candidate headline:** DRAFT: verify: Monitored and modified response classes together account for 90% of the area.
- **Subtitle:** Northwest Territories reporting agency only | 2000–2025 | 1 reporting agency | Part of the fixed 12-agency series; record and area shares include Unknown. FUL: full, MOD: modified, MON: monitored.
- **Main visual and why:** A labelled combined MON + MOD area-share marker above paired share bars for FUL, MOD, MON and Unknown. The separate classes remain visible so the combined figure cannot conceal its components. Grey represents record-share context; rust represents reported-area burden.
- **Chart annotation:** Annotate MON + MOD at 90% of area; alongside it show the separate MON and MOD whole-number shares. The denominator is all selected NT reported area, including FUL and Unknown.
- **So what:** I would review monitored and modified response classifications together when discussing NT’s recorded workload.
- **Caveat beside the visual:** “Response classification does not measure suppression effectiveness or response effects.”
- **Look next:** Return to Executive Summary, or choose Explore.
- **Evidence and tooltip detail:** review_tables/nt_response.csv. Exact combined area share 90.06%; individual record and area shares remain available. Both denominators include Unknown. Whole-number displayed components may not sum to the displayed combined value because calculations use unrounded values.

## Explore: Season

- **Decision question:** When is the pooled reporting peak in the selected records?
- **Candidate headline:** DRAFT: verify: July has the most recorded events.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land. Month is the source month; valid-month chart excludes unknown months.
- **Main visual and why:** A pooled monthly record-count column chart, with July labelled. Agency variation is secondary, available through the agency filter or a tooltip; do not lead with the agency heatmap.
- **Chart annotation:** Point to July’s 42,235 selected records. Label the denominator as records with a valid source month; show the unknown-month count beside the chart.
- **So what:** I would use July as the first pooled seasonal workload scenario to examine.
- **Caveat beside the visual:** “3,418 selected records lack a valid month; source month is not burning duration.”
- **Look next:** Explore Agency Scorecard, or Back to main story.
- **Evidence and tooltip detail:** vw_seasonality. Whole-number counts stay exact. Any percentage labels on the page are whole numbers, with precise shares in tooltips. Agency variation remains secondary context.

## Explore: Agency Scorecard

- **Decision question:** Which reporting-agency submissions carry the largest reported-area totals?
- **Candidate headline:** DRAFT: verify: Saskatchewan’s reporting agency has the largest recorded area total.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land.
- **Main visual and why:** A reporting-agency scorecard with an in-cell rust area bar and labelled contextual columns for large-fire share, unknown cause and coverage status. Coverage status is text, not a synthetic trust grade.
- **Chart annotation:** Point to SK’s 17.10 million reported ha, and keep Parks Canada as a separate reporting-agency row.
- **So what:** I would start agency-level follow-up with the largest reported-area submissions.
- **Caveat beside the visual:** “Agencies are reporting units, not geographic provinces or performance rankings.”
- **Look next:** Explore Map, or Back to main story.
- **Evidence and tooltip detail:** vw_agency and vw_coverage. Percentages use whole numbers in the scorecard and precise values in tooltips. No exposure-adjusted rate or geographic allocation is implied.

## Explore: Map

- **Decision question:** Where do the source coordinates place reported area at the coarse display scale?
- **Candidate headline:** DRAFT: verify: A few coarse locations hold a small share of the recorded area.
- **Subtitle:** Fixed Canadian reporting-agency series | 2000–2025 | 12 reporting agencies | Counts: reported records; area: summed SIZE_HA in hectares, not unique land. Mapped subset only; rounded one-degree coordinates are not geographic provincial allocation.
- **Main visual and why:** A map of rounded grid-cell centres with rust symbols sized by reported area on a grey basemap. This shows coarse recorded locations without implying a verified province allocation or an equal-area density rate.
- **Chart annotation:** Outline the five highest-area cells and annotate their combined 6% mapped-area share. State the rounding rule and mapped denominator beside the map.
- **So what:** I would use the largest recorded-location clusters to choose follow-up data checks.
- **Caveat beside the visual:** “Approximate rounded locations; 207 selected records cannot be mapped.”
- **Look next:** Back to main story.
- **Evidence and tooltip detail:** vw_grid. The precise combined mapped-area share is 5.94% in the tooltip. Use rounded cell coordinates rather than mean-source coordinates; verify native map support and aggregation before implementation.

## Review gate

The main path is six pages, with three optional Explore pages reached by a button. Every candidate finding headline remains DRAFT: verify. The Executive Summary is built last. Privacy findings and replacements are reported separately in `docs/privacy_review.md`.

The storyboard is approved subject to its draft wording. Local Power BI preparation assets are now supplied; no native report pages have been built or published. Final headline wording remains with the reviewer.
