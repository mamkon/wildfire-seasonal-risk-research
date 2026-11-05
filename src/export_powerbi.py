"""Export the Power BI star-model CSVs and separate reference evidence."""

import hashlib
import json
import sqlite3

import pandas as pd

from src.config import ROOT

R = ROOT
P = R / "powerbi"
P.mkdir(exist_ok=True)
DATA = P / "data"
DATA.mkdir(exist_ok=True)
# Export facts and dimensions, not analytical reference views.
names = [
    "load_batch",
    "fact_fire",
    "fact_nfd_annual",
    "dim_agency",
    "dim_cause",
    "dim_size_class",
    "dim_response",
    "dim_date",
    "dim_year",
    "dim_month",
]
manifest = []
with sqlite3.connect(
    f"file:{(R / 'data/warehouse/wildfire.db').resolve().as_posix()}?mode=ro", uri=True
) as db:
    for name in names:
        t = pd.read_sql_query(f"SELECT * FROM {name}", db)
        if name == "fact_fire":
            t["grid_cell"] = t.grid_cell.fillna("Unknown")
        if name == "dim_agency":
            labels = {
                "AB": "Alberta",
                "BC": "British Columbia",
                "MB": "Manitoba",
                "NB": "New Brunswick",
                "NL": "Newfoundland and Labrador",
                "NS": "Nova Scotia",
                "NT": "Northwest Territories",
                "ON": "Ontario",
                "PC": "Parks Canada",
                "PE": "Prince Edward Island",
                "QC": "Quebec",
                "SK": "Saskatchewan",
                "YT": "Yukon",
                "Unknown": "Unknown",
            }
            t["reporting_agency_name"] = t.agency_code.map(labels).fillna("Unknown")
        if name == "dim_year":
            t["decade_start"] = t.year_key.map(lambda y: int(y // 10 * 10) if y >= 0 else -1)
            t["decade_label"] = t.decade_start.map(lambda y: str(y) + "s" if y >= 0 else "Unknown")
        f = DATA / f"{name}.csv"
        t.to_csv(f, index=False)
        manifest.append(
            {
                "table": name,
                "rows": len(t),
                "columns": list(t.columns),
                "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            }
        )
    cells = pd.read_sql_query(
        "SELECT DISTINCT grid_cell FROM fact_fire WHERE grid_cell IS NOT NULL", db
    )
    rows = [{"grid_cell": "Unknown", "latitude": None, "longitude": None}]
    for cell in cells.grid_cell:
        lat, lon = cell.split("_")
        rows.append({"grid_cell": cell, "latitude": int(lat), "longitude": int(lon)})
    grid = pd.DataFrame(rows)
    grid.to_csv(DATA / "dim_grid.csv", index=False)
    manifest.append(
        {
            "table": "dim_grid",
            "rows": len(grid),
            "columns": list(grid.columns),
            "sha256": hashlib.sha256((DATA / "dim_grid.csv").read_bytes()).hexdigest(),
        }
    )
    # These disconnected choices are display definitions, not precomputed KPIs.
    small = pd.DataFrame(
        {
            "size_value": [0, 0.01, 0.1],
            "size_label": ["Exactly 0 ha", "Exactly 0.01 ha", "Exactly 0.1 ha"],
        }
    )
    small.to_csv(DATA / "size_points.csv", index=False)
    checks = pd.read_sql_query(
        "SELECT reported_records,area_ha,mean_size_ha,median_size_ha,large_fire_records,large_fire_share,unknown_cause_share,missing_report_date_share FROM vw_kpi_summary",
        db,
    )
    checks.to_csv(P / "reference_kpis.csv", index=False)
    for name in [
        "vw_concentration",
        "vw_annual_trend",
        "vw_cause",
        "vw_agency",
        "vw_seasonality",
        "vw_coverage",
    ]:
        target = P / "validation" / f"{name}.csv"
        target.parent.mkdir(exist_ok=True)
        pd.read_sql_query(f"SELECT * FROM {name}", db).to_csv(target, index=False)
(P / "export_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


print("Power BI CSV exports and reference evidence rebuilt.")
