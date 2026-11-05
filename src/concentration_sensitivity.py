import json
import sqlite3

import pandas as pd

from src.config import ROOT

R = ROOT
with sqlite3.connect(
    f"file:{(R / 'data/warehouse/wildfire.db').resolve().as_posix()}?mode=ro", uri=True
) as db:
    annual = pd.read_sql_query("SELECT year,area_ha FROM vw_annual_trend ORDER BY year", db)
    x = pd.read_sql_query("SELECT fire_key,reporting_agency,size_ha FROM vw_analysis", db)
    shares = pd.read_sql_query(
        "SELECT reporting_agency,selected_records,area_share FROM vw_concentration WHERE top_pct=3 AND reporting_agency<>'ALL'",
        db,
    )
recent = annual.loc[annual.year.between(2020, 2025)]
sensitivity = pd.DataFrame(
    [
        {
            "period": "2020–2025",
            "excluded_year": "None",
            "years": len(recent),
            "total_area_ha": recent.area_ha.sum(),
            "mean_annual_area_ha": recent.area_ha.mean(),
        },
        {
            "period": "2020–2025 excluding 2023",
            "excluded_year": "2023",
            "years": int(recent.year.ne(2023).sum()),
            "total_area_ha": recent.loc[recent.year.ne(2023), "area_ha"].sum(),
            "mean_annual_area_ha": recent.loc[recent.year.ne(2023), "area_ha"].mean(),
        },
    ]
)
totals = (
    x.groupby("reporting_agency")
    .agg(agency_records=("fire_key", "size"), agency_area_ha=("size_ha", "sum"))
    .reset_index()
)
k = (len(x) * 3 + 99) // 100
pooled = x.sort_values(["size_ha", "fire_key"], ascending=[False, True]).head(k)
selected = (
    pooled.groupby("reporting_agency")
    .agg(pooled_top3_records=("fire_key", "size"), pooled_top3_area_ha=("size_ha", "sum"))
    .reset_index()
)
comparison = (
    totals.merge(shares, on="reporting_agency")
    .merge(selected, on="reporting_agency", how="left")
    .fillna(0)
)
comparison["within_agency_top3_area_ha"] = comparison.agency_area_ha * comparison.area_share
comparison["agency_record_share_in_pooled_cutoff"] = (
    comparison.pooled_top3_records / comparison.agency_records
)
baseline = comparison.within_agency_top3_area_ha.sum() / x.size_ha.sum()
national = pooled.size_ha.sum() / x.size_ha.sum()
out = R / "data/processed/review_tables"
sensitivity.to_csv(out / "decade_sensitivity.csv", index=False)
comparison.to_csv(out / "pooling_comparison.csv", index=False)
metrics = {
    "within_agency_min": float(shares.area_share.min()),
    "within_agency_max": float(shares.area_share.max()),
    "pooled_top3_share": float(national),
    "area_weighted_within_agency_top3_share": float(baseline),
    "pooled_cutoff_records": int(k),
    "sum_within_agency_cutoff_records": int(shares.selected_records.sum()),
    "mean_annual_2020s": float(sensitivity.iloc[0].mean_annual_area_ha),
    "mean_annual_2020s_without_2023": float(sensitivity.iloc[1].mean_annual_area_ha),
}
(out / "sensitivity_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(sensitivity.to_string(index=False))
print(json.dumps(metrics, indent=2))
print(
    comparison[["reporting_agency", "agency_record_share_in_pooled_cutoff"]].to_string(index=False)
)
