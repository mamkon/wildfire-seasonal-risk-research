import json
import sqlite3

import pandas as pd

from src.config import ROOT

R = ROOT
P = R / "data/processed"
checks = json.loads((P / "internal_reconciliation.json").read_text())
with sqlite3.connect(R / "data/warehouse/wildfire.db") as db:
    k = pd.read_sql_query(
        "SELECT reported_records,area_ha,mean_size_ha,median_size_ha,large_fire_records,large_fire_share FROM vw_kpi_summary",
        db,
    ).iloc[0]
    rows = db.execute("SELECT COUNT(*) FROM fact_fire").fetchone()[0]
    nfd = db.execute("SELECT COUNT(*) FROM fact_nfd_annual").fetchone()[0]
    dims = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'dim_%' ORDER BY name", db
    ).name.tolist()
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def write(p, s):
    (R / p).write_text(s, encoding="utf-8")


write(
    "docs/sql_stage_review.md",
    f"""# SQL warehouse review

I used the approved fixed-reporting-agency window. The warehouse retains {rows:,} source records, with {int(k.reported_records):,} eligible records selected for analysis. The selected period and exclusions are recorded in the load batch. I have not loaded Power BI or built the analytical notebooks.

## Checked reference results
| Measure | SQL result |
|---|---:|
| Selected reported records | {int(k.reported_records):,} |
| Sum of selected reported sizes, hectares | {k.area_ha:,.4f} |
| Mean reported size, hectares | {k.mean_size_ha:,.4f} |
| Median reported size, hectares | {k.median_size_ha:,.4f} |
| Large-fire records under the declared threshold | {int(k.large_fire_records):,} |
| Observed large-fire share | {k.large_fire_share:.4%} |

These are reference calculations for pooled reporting records, not a complete national census, geographic provincial totals or population fire risk. Summed sizes can include land affected by separate events or years. Repeated identifiers remain visible.

## Model and grain
fact_fire has one row per source record and a scope flag. The dimensions are {", ".join(dims)}. Every dimension has an Unknown member. I use separate year and month dimensions because a missing day must not remove a valid year or month from a total. The date dimension only represents valid source calendar dates; it does not manufacture dates for incomplete records.

fact_nfd_annual is an empty aggregate fact for verified external reference imports. Its grain is jurisdiction, year, reporting category and source release. It currently contains {nfd:,} rows; that means pending evidence, not agreement.

## Internal verification
All {len(checks)} reference views reconcile with separate pandas calculations, using relative tolerance and absolute tolerance recorded in src/reconcile.py. The comparison covers every output column and row, including shares, medians, concentration, Pareto totals, annual changes, full rolling windows, decades, sensitivity results, season, cause, segments, quality, grids and top records.

Fixture tests also check valid constraints, Unknown members, rerunnable loads and both even- and odd-sized medians. Database integrity and foreign-key checks pass. An interrupted build leaves the prior database intact because a fresh temporary database replaces it only after validation.

## Reproduce
From the project folder after preparation:
```
python -m src.load_warehouse
python -m src.reconcile
python -m pytest tests -q
python -m ruff check src tests
```
The loader exports facts, dimensions and reference views under data/processed/warehouse_exports. Later Power BI work will import facts and dimensions only. The view CSVs are evidence for checking DAX, not the Power BI data model.

## What remains unverified
NFD totals and scope footnotes remain unavailable. DAX results, Power BI visuals and analytical interpretations have not been built or validated. No numerical external reconciliation or operational effect is claimed.

I am stopping at the SQL review checkpoint before the analytical notebooks.
""",
)
write(
    "docs/reconciliation_report.md",
    """# Reconciliation report

## Internal: passed
I compared every SQL reference view with separate pandas calculations. The machine-readable comparison results are in data/processed/internal_reconciliation.json. Fixture-based pytest checks repeat those comparisons without the full raw dataset. The full source check runs separately after the warehouse build.

I allow small floating-point differences using the explicit tolerances in src/reconcile.py. Record counts, keys and categories still have to agree. A meaningful difference fails the comparison rather than being explained away.

## External: pending, not a test failure or an agreement claim
I have not obtained the official NFD tables and their scope footnotes. fact_nfd_annual is empty. I have not invented totals or used CNFDB values as an independent reference. The reference extraction entry point is http://nfdp.ccfm.org/en/data/fires.php.

CNFDB reporting agencies are not geographic jurisdictions. Parks Canada spans jurisdictions. Before joining external totals, I need either verified matching reporting scope or a justified allocation method. I will not add Parks Canada to provincial figures without checking whether those figures already include it.

Once comparable exports are available, I will report the count and area differences and percentage gaps for each matched jurisdiction, year and category. Scope, minimum size, revisions, mapping and Parks Canada treatment could explain differences, but I have not diagnosed a cause without the reference data. External discrepancies will be reported, not forced to zero.
""",
)
write(
    "docs/sql_dax_mapping.md",
    """# KPI reference mapping

DAX is not implemented yet. These measure names define the later Power BI checks. Every DAX measure must apply the selected scope flag; removing that filter changes the population. Source-wide data-quality measures are deliberately separate.

| Planned DAX measure | SQL reference | Independent pandas calculation |
|---|---|---|
| Total Fires, labelled reported records | vw_kpi_summary.reported_records | selected row count |
| Total Area | vw_kpi_summary.area_ha | sum of selected size_ha |
| Mean Size | vw_kpi_summary.mean_size_ha | selected size_ha.mean |
| Median Size | vw_kpi_summary.median_size_ha | selected size_ha.median |
| Large Fire Count | vw_kpi_summary.large_fire_records | sum of selected is_large_fire |
| Large Fire Share | vw_kpi_summary.large_fire_share | selected is_large_fire.mean |
| Area Share Top Three Percent | vw_concentration.area_share, national ALL group | largest ceiling-defined record count, divided by selected area |
| YoY Area Change | vw_annual_trend.yoy_area_change | annual difference divided by prior year |
| Rolling Area | vw_annual_trend.five_year_mean_area | full-window rolling annual mean |
| Lightning Area Share | vw_cause.area_share, Natural/lightning class | class area divided by reporting-agency area |
| Human-Caused Fire Share | vw_cause.count_share, Human class | class records divided by reporting-agency records |
| Unknown Cause | vw_kpi_summary.unknown_cause_share | selected unknown_cause.mean |
| Missing Date | vw_kpi_summary.missing_report_date_share | selected missing_report_date.mean |
| Agency scorecard | vw_agency | grouped selected counts, size summaries and shares |
| Seasonal counts and area | vw_seasonality | grouped selected reporting agency and source month |
| Data-quality trends | vw_quality_trend | all source rows grouped by reporting agency and source year |

The national concentration group means all selected reporting agencies, not complete geographic coverage. Ties at a top-share boundary are resolved by the local source-row key; the number of selected records is rounded upward. Mean annual area and rolling values are averages of annual area, not averages of individual fire sizes.
""",
)
decision_path = R / "docs/decision_log.md"
decision_path.write_text(
    decision_path.read_text(encoding="utf-8").split("\n## Approved window and SQL choices")[0],
    encoding="utf-8",
)
with decision_path.open("a", encoding="utf-8") as f:
    f.write("""
## Approved window and SQL choices

I use the modern fixed-agency candidate selected by the reviewer. The load batch records its actual start, end and source hash. PE is excluded from this fixed series because its documented coverage starts later. The wider recent candidate remains a sensitivity option, not an unlabelled addition.

I retain all source rows in fact_fire and expose the selected scope explicitly. I do not use fire identifiers as unique incident keys. Every dimension has an Unknown member. Separate source-year and source-month dimensions preserve valid partial dates without inventing calendar days.

I use a provisional minimum segment size recorded in src/load_warehouse.py and the segment view. Below-minimum and unknown-month segments are flagged and must not be ranked. This is a reporting rule, not a statistical guarantee; it can be revised transparently during the analysis review. Exact concentration cutoffs use ceiling record counts and deterministic source-row tie breaking.

The first rolling values remain missing until the full declared window is available. Missing annual area is not filled as zero. Partial decades are labelled with their observed-year count. No significance tests or causal interpretations are introduced.
""")
qpath = P / "quality_summary.json"
q = json.loads(qpath.read_text())
q["selected_window"] = "modern_fixed_agencies"
qpath.write_text(json.dumps(q, indent=2), encoding="utf-8")
write(
    "data/analysis_scope.json",
    json.dumps(
        {
            "selected_window": "modern_fixed_agencies",
            "start_year": 2000,
            "end_year": 2025,
            "excluded_reporting_agencies": ["PE"],
            "eligible_records_verified": int(k.reported_records),
            "minimum_segment_records": 30,
        },
        indent=2,
    ),
)
print("SQL review and reconciliation documentation generated.")
