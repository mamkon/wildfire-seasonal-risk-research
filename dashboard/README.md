# Canada Wildfire Power BI report

Open `Canada_Wildfire.pbip` in Power BI Desktop. Extract the ZIP first and keep the Report and SemanticModel folders beside the project file. If Desktop displays **Refresh now**, select it to load the embedded tables. In Desktop edit mode, Ctrl+click the navigation buttons. The page tabs also open each view.

This review build uses the 2000–2025 CNFDB analysis of 12 reporting agencies. The latest valid report date in scope is December 21, 2025. Cards and gauges draw on the fixed-scope metrics. The July gauge shows the July count divided by the average for the 12 calendar months, with a 1× reference marker. The second gauge shows the pooled recorded-area share of the largest 3% of records on a 0–100% scale. The donut shows known and unknown cause coding, since the source supplies no confidence scores.

Fire Locations, Fire Hotspots and Fire Clusters use Azure Maps with 1,121 rounded coordinate cells. Marker size and heat intensity use recorded area. Cluster counts refer to grouped cells. There are 207 records outside the mapped set. Azure Maps availability depends on the tenant and its network access. The separate Map page ranks the 20 cells with the most recorded area.

Forest Watch and Carbon Flux identify the additional datasets needed to show those measures. Province or territory and Year dropdowns filter the three Azure Maps views. The executive KPIs retain the full study scope. Geographic labels use the original coordinates and Natural Earth province and territory boundaries, before locations are grouped into rounded cells. Unassigned means a point did not match those boundaries. Headlines are marked for review.

The Executive Summary layout draws on the [SAS Visual Analytics wildfire dashboard](https://communities.sas.com/t5/SAS-Visual-Analytics-Gallery/Fighting-the-Amazon-forest-fires-with-advanced-analytics/ta-p/784221). [Microsoft Azure Maps layer documentation](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-understanding-layers)

The Trust page records the comparison with the 2025 annual report. The full 2023 source-year count and rounded area match its published national table. The narrower chart scope still carries the pending NFD reconciliation label. See the [official annual report](https://prod-natural-resources.azure.cloud.nrcan-rncan.gc.ca/forests-forestry/state-canada-forests/state-canada-s-forests-annual-report-2025).

Natural Resources Canada, Canadian Forest Service, Canadian National Fire Database. Contains information licensed under the Open Government Licence – Canada.

## Executive gauge definitions

These Data Analysis Expressions (DAX) measures live in **Executive Metrics** in the GitHub model's `model.bim`. Both use audited fixed-scope inputs from the warehouse.

```dax
July Surge Ratio =
    DIVIDE([July records], [Average known month])

Top 3 Pct Area Share =
    DIVIDE([Area in largest 3% (million ha)], [Recorded area])
```

- **July Surge Ratio** is **3.07×**. July contributes 42,235 records. The benchmark is 164,858 known-month records divided by 12. The 3,418 records without a known month are excluded from this comparison.
- **Top 3 Pct Area Share** is **96.2%**. The warehouse ranks records by area descending and uses the unique record key to break ties. It sums the first 5,049 records, rounding the 3% cutoff up. The denominator sums recorded fire sizes for the full study scope.

## Proposed executive palette

This palette is a design specification for a future report styling pass.

| Colour | Use |
| --- | --- |
| Ember Ochre `#C2410C` | Recorded area, the July record count, and the largest-fire area share. |
| Boreal Forest `#0F382C` | Navigation, baseline comparisons, and mapped boundaries. |
| White `#FFFFFF` and Light Grey `#F8F9FA` | Canvas and supporting panels. |

Use labels and units alongside colour. The July gauge measures historical record volume, and the map shows recorded fire area by rounded location cell. Use the Trust page for recording and reconciliation caveats.
