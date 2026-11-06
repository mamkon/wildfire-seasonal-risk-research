# Power BI model review

Use the aggregate exports to add a **Model Evaluation** report page. These exports have no fire identifiers or point coordinates. Keep the existing historical dashboard figures on their own pages and label the evaluation period **2023–2025**.

| File | Grain | Purpose |
| --- | --- | --- |
| [Test policies](results/test_policies.csv) | One row per alert policy | Compare missed large fires, extra reviews and review volume. |
| [Test by year](results/test_by_year.csv) | One row per test year at the chosen cutoff | Check whether missed fires and review workload vary by season. |
| [Evaluation record](results/evaluation.json) | One full run | Audit source fingerprint, split sizes, model settings, fold results and calibration policies. |

1. Import both comma-separated values files in Power BI Desktop. Keep the tables disconnected because they have different grains. Assign counts a whole-number type, and assign rates a decimal type with percentage display. Preserve null metrics as blank. Cutoff and area-under-curve scores are decimals.
2. Put a single-select policy slicer above four native cards for **Recall**, **Missed large fires**, **Extra reviews**, and **Alert share**. Save the report with the chosen miss-cost policy selected. Use a two-by-two matrix with actual outcome on rows and alert decision on columns. Use rust for missed large fires and amber for extra reviews.
3. Use the yearly table for a line or column chart of recall. Show counts and year-level alert share in tooltips. Label the yearly chart as the frozen chosen policy so readers can distinguish it from policy comparisons.
4. Before publication, match the report values against the evaluation record. Use the “Alert no records” row to check that precision stays blank and that every actual large fire is counted as a miss. Match the selected policy’s count totals against the sum of the three yearly rows.

The miss cost is a planning assumption. A false positive represents an extra manual review. The output supports retrospective discussion of alert workload and missed cases. Live use would require verified information available at report time, external validation, approved staffing limits, and operating procedures.
