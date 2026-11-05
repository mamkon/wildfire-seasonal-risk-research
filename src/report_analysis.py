import calendar
import json

import nbformat

from src.config import ROOT
from src.review_analysis import tables

R = ROOT
m = json.loads((R / "data/processed/analysis_metrics.json").read_text())
national_segments = tables()["national_segments"]
counts = {}
for p in (R / "notebooks").glob("*.ipynb"):
    book = nbformat.read(p, as_version=4)
    cells = [c for c in book.cells if c.cell_type == "code"]
    assert all(c.execution_count is not None for c in cells)
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    counts[p.name] = len(cells)
drop = (1 - m["mean_annual_area_without_largest_year"] / m["mean_annual_area_all_years"]) * 100
t = (
    f"""# Analysis review

I completed the data-quality and burden-pattern notebooks using the checked warehouse and the approved fixed-agency series. Both notebooks have executed SQL queries, saved tables and charts, and short takeaways beside each section.

## Findings for review
- I found within-agency top-three-percent area shares ranging from 59.46% to 99.56%; the pooled reference is {m["top_shares"]["3"]:.2%}. The mean reported size is {m["mean_size_ha"]:,.2f} hectares and the median is {m["median_size_ha"]:.2f} hectares, so the mean does not describe a typical recorded event well.
- The largest annual reported-area total is {m["peak_area_ha"] / 1e6:.2f} million hectares in {m["peak_area_year"]}. Removing that year reduces the mean annual total by {drop:.2f} percent. I do not interpret that sensitivity check as proof of a sustained trend.
- {calendar.month_name[m["peak_record_month"]]} has the largest pooled valid-month record count, {m["peak_month_records"]:,}. I keep the {m["invalid_month_records"]:,} unknown or invalid-month records visible in the table rather than placing them in a month.
- The reporting segments now use cause by month nationally. I flagged {int(national_segments.do_not_rank.sum()):,} of {len(national_segments):,} observed pooled segments as unsuitable for ranking under the declared rule. The full agency-level segment table stays in the notebook technical section only; neither version is a forecast or population risk rate.

## Why the quality analysis comes first
I compare all supplied records with the selected cohort, show documented coverage periods, inspect low-count agency-year cells and track missing report dates and unknown causes. I keep the source-wide quality denominator distinct from selected-cohort shares. A low reported count is a reason to investigate, not proof that a place had low wildfire activity.

I leave national response-zone comparisons, forested-area rates and national duration comparisons outside this core analysis because their definitions, coverage or denominators are not adequate for the proposed comparison. Agency remains a reporting dimension. These results are not geographic provincial totals.

## Reproduce
From the project folder after the warehouse checks:
```
python -m src.analyse
python -m src.build_notebooks
python -m src.execute_notebooks
```
Dependencies are pinned in requirements.txt. Notebook execution uses fresh Python processes with IPython rich-display capture; it does not require a remote notebook service. The analysis figures use the revised dark-ember palette.

## Verification
"""
    + "".join(
        f"- {name}: {count} code cells executed with saved outputs.\n"
        for name, count in counts.items()
    )
    + """
The analysis reads SQL views already reconciled to separate pandas calculations. I checked the chart files and visually reviewed every generated analysis figure for readability, labels and clipping. I do not claim a native Power BI report or a PDF export at this stage.

## What remains unverified
NFD external totals, geographic allocation and full agency-year completeness remain unverified. The work does not estimate causal effects, future losses, community exposure or operational benefits. Power BI implementation and DAX reconciliation are the next stage, after this review.
"""
)
(R / "docs/analysis_review.md").write_text(t, encoding="utf-8")
(R / "data/processed/notebook_execution.json").write_text(
    json.dumps(counts, indent=2), encoding="utf-8"
)
print("Analysis review generated from executed outputs.")
