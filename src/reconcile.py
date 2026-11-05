"""Independent pandas calculations for every SQL reference view."""

import json
import sqlite3

import numpy as np
import pandas as pd

from src.config import AGENCY_STARTS, END_YEAR, PROCESSED, ROOT


def expected_views(d):
    x = d.loc[
        d.eligible_for_analysis & d.year.between(2000, 2025) & d.reporting_agency.ne("PE")
    ].copy()
    x["fire_key"] = x.source_row
    x["fire_id"] = x.NFDBFIREID
    x["month_num"] = x.month_num.where(~x.invalid_month, -1)
    out = {}
    out["vw_analysis"] = x[
        [
            "fire_key",
            "fire_id",
            "year",
            "month_num",
            "reporting_agency",
            "cause_class",
            "size_ha",
            "is_large_fire",
            "missing_report_date",
            "grid_cell",
            "latitude",
            "longitude",
        ]
    ].copy()
    # Coordinates failing checks are NULL in the warehouse, not imputed points.
    out["vw_analysis"].loc[x.invalid_coordinates, ["latitude", "longitude"]] = np.nan
    n = len(x)
    total = x.size_ha.sum()
    out["vw_kpi_summary"] = pd.DataFrame(
        [
            dict(
                reported_records=n,
                area_ha=total,
                mean_size_ha=x.size_ha.mean(),
                median_size_ha=x.size_ha.median(),
                large_fire_records=int(x.is_large_fire.sum()),
                large_fire_share=x.is_large_fire.mean(),
                unknown_cause_share=x.unknown_cause.mean(),
                missing_report_date_share=x.missing_report_date.mean(),
            )
        ]
    )
    conc = []
    for agency, g in [("ALL", x), *list(x.groupby("reporting_agency"))]:
        for pct in [1, 3, 5]:
            k = int(np.ceil(len(g) * pct / 100))
            denom = g.size_ha.sum()
            conc.append(
                dict(
                    reporting_agency=agency,
                    top_pct=pct,
                    selected_records=k,
                    area_share=g.size_ha.nlargest(k).sum() / denom if denom else np.nan,
                )
            )
    out["vw_concentration"] = pd.DataFrame(conc)
    p = x.sort_values(["size_ha", "fire_key"], ascending=[False, True]).copy()
    p["position"] = np.arange(1, len(p) + 1)
    p["cumulative_area_share"] = p.size_ha.cumsum() / total
    out["vw_pareto"] = p[["fire_key", "size_ha", "position", "cumulative_area_share"]]
    a = (
        x.groupby("year")
        .agg(reported_records=("fire_key", "size"), area_ha=("size_ha", "sum"))
        .reindex(range(2000, 2026))
    )
    a.index.name = "year"
    a["reported_records"] = a.reported_records.fillna(0)
    a["yoy_area_difference"] = a.area_ha.diff()
    a["yoy_area_change"] = a.area_ha.diff() / a.area_ha.shift(1).replace(0, np.nan)
    a["five_year_mean_area"] = a.area_ha.rolling(5, min_periods=5).mean()
    out["vw_annual_trend"] = a.reset_index()
    z = (
        x.assign(decade=x.year // 10 * 10)
        .groupby("decade")
        .agg(
            years_observed=("year", "nunique"),
            reported_records=("fire_key", "size"),
            area_ha=("size_ha", "sum"),
        )
    )
    z["mean_annual_area"] = z.area_ha / z.years_observed
    out["vw_decades"] = z.reset_index()
    annual = x.groupby("year").agg(
        reported_records=("fire_key", "size"), area_ha=("size_ha", "sum")
    )
    peak = annual.area_ha.idxmax()
    rows = []
    for label, g in [
        ("All selected years", annual),
        ("Largest area year removed", annual.drop(index=peak)),
    ]:
        rows.append(
            dict(
                scenario=label,
                years=len(g),
                reported_records=g.reported_records.sum(),
                area_ha=g.area_ha.sum(),
                mean_annual_area=g.area_ha.mean(),
            )
        )
    out["vw_largest_year_sensitivity"] = pd.DataFrame(rows)
    out["vw_seasonality"] = (
        x.groupby(["reporting_agency", "month_num"])
        .agg(reported_records=("fire_key", "size"), area_ha=("size_ha", "sum"))
        .reset_index()
    )
    g = (
        x.groupby(["reporting_agency", "cause_class"])
        .agg(reported_records=("fire_key", "size"), area_ha=("size_ha", "sum"))
        .reset_index()
    )
    g["count_share"] = g.reported_records / g.groupby(
        "reporting_agency"
    ).reported_records.transform("sum")
    g["area_share"] = g.area_ha / g.groupby("reporting_agency").area_ha.transform("sum").replace(
        0, np.nan
    )
    out["vw_cause"] = g
    g = (
        x.groupby("reporting_agency")
        .agg(
            reported_records=("fire_key", "size"),
            area_ha=("size_ha", "sum"),
            mean_size_ha=("size_ha", "mean"),
            median_size_ha=("size_ha", "median"),
            large_fire_share=("is_large_fire", "mean"),
            unknown_cause_share=("unknown_cause", "mean"),
        )
        .reset_index()
    )
    out["vw_agency"] = g
    g = (
        x.groupby(["reporting_agency", "cause_class", "month_num"])
        .agg(reported_records=("fire_key", "size"), large_fire_records=("is_large_fire", "sum"))
        .reset_index()
    )
    g["large_fire_share"] = g.large_fire_records / g.reported_records
    g["do_not_rank"] = (g.reported_records.lt(30) | g.month_num.eq(-1)).astype(int)
    out["vw_segments"] = g
    out["vw_threshold_sensitivity"] = pd.DataFrame(
        [
            dict(
                threshold_ha=t,
                large_fire_records=int(x.size_ha.ge(t).sum()),
                record_share=x.size_ha.ge(t).mean(),
                area_share=x.loc[x.size_ha.ge(t), "size_ha"].sum() / total,
            )
            for t in [100, 200, 1000]
        ]
    )
    quality = d.copy()
    quality["year"] = quality.year.where(~quality.invalid_year, -1)
    quality["selected"] = (
        quality.eligible_for_analysis
        & quality.year.between(2000, 2025)
        & quality.reporting_agency.ne("PE")
    ).astype(int)
    quality["unknown_response"] = quality.response_code.isna().astype(int)
    quality["unknown_calendar"] = quality.calendar_date.isna().astype(int)
    out["vw_quality_trend"] = (
        quality.groupby(["reporting_agency", "year"])
        .agg(
            source_records=("source_row", "size"),
            selected_records=("selected", "sum"),
            missing_report_date_share=("missing_report_date", "mean"),
            missing_size_share=("missing_size", "mean"),
            invalid_size_share=("invalid_size", "mean"),
            unknown_cause_share=("unknown_cause", "mean"),
            unknown_response_records=("unknown_response", "sum"),
            unknown_calendar_date_records=("unknown_calendar", "sum"),
        )
        .reset_index()
    )
    out["vw_grid"] = (
        x.groupby("grid_cell")
        .agg(
            reported_records=("fire_key", "size"),
            area_ha=("size_ha", "sum"),
            mean_source_latitude=("latitude", "mean"),
            mean_source_longitude=("longitude", "mean"),
        )
        .reset_index()
    )
    p = x[
        ["fire_key", "fire_id", "reporting_agency", "year", "month_num", "cause_class", "size_ha"]
    ].copy()
    p["area_rank"] = p.size_ha.rank(method="min", ascending=False)
    out["vw_top_fires"] = p
    quality_index = out["vw_quality_trend"].set_index(["reporting_agency", "year"])
    coverage = []
    for agency, start in AGENCY_STARTS.items():
        for year in range(min(AGENCY_STARTS.values()), END_YEAR + 1):
            key = (agency, year)
            present = key in quality_index.index
            coverage.append(
                dict(
                    reporting_agency=agency,
                    year=year,
                    source_records=int(quality_index.loc[key, "source_records"]) if present else 0,
                    selected_records=int(quality_index.loc[key, "selected_records"])
                    if present
                    else 0,
                    coverage_status="Outside documented coverage"
                    if year < start
                    else (
                        "Records present; completeness unverified"
                        if present
                        else "No records; completeness unknown"
                    ),
                )
            )
    out["vw_coverage"] = pd.DataFrame(coverage)
    return out


def reconcile(d, db):
    checks = []
    for view, expected in expected_views(d).items():
        cols = list(expected.columns)
        # View names and columns are internal constants from expected_views.
        actual = pd.read_sql_query(f"SELECT {','.join(cols)} FROM {view}", db)
        # Normalize numeric extension dtypes before tolerance comparisons.
        for col in cols:
            if pd.api.types.is_numeric_dtype(expected[col].dtype) or pd.api.types.is_bool_dtype(
                expected[col].dtype
            ):
                expected[col] = pd.to_numeric(expected[col]).astype(float)
                actual[col] = pd.to_numeric(actual[col]).astype(float)
        expected = expected.sort_values(cols, na_position="first").reset_index(drop=True)
        actual = actual.sort_values(cols, na_position="first").reset_index(drop=True)
        pd.testing.assert_frame_equal(
            actual, expected, check_dtype=False, check_exact=False, rtol=1e-9, atol=1e-6
        )
        checks.append({"view": view, "rows_compared": len(actual), "status": "pass"})
    return checks


def main():
    d = pd.read_csv(PROCESSED / "cnfdb_flagged.csv", low_memory=False)
    with sqlite3.connect(ROOT / "data/warehouse/wildfire.db") as db:
        results = reconcile(d, db)
    (PROCESSED / "internal_reconciliation.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print(
        f"All {len(results)} SQL reference views reconcile to independently calculated pandas outputs."
    )


if __name__ == "__main__":
    main()
