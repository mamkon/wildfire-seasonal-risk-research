"""Descriptive analysis from checked SQL reference views. No predictive modelling."""

import json
import sqlite3

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from src.config import PROCESSED, ROOT

COLORS = {
    "background": "#0E0E10",
    "card": "#1A1A1E",
    "grid": "#2C2C31",
    "rust": "#B4472B",
    "ember": "#D9622B",
    "amber": "#E8A33D",
    "sand": "#C8A99A",
    "teal": "#1F9E89",
    "text": "#F2E6D8",
    "muted": "#9C9690",
}


def query(sql):
    path = (ROOT / "data/warehouse/wildfire.db").as_posix()
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        return pd.read_sql_query(sql, db)


def style():
    plt.rcParams.update(
        {
            "figure.facecolor": COLORS["background"],
            "axes.facecolor": COLORS["card"],
            "text.color": COLORS["text"],
            "axes.labelcolor": COLORS["text"],
            "axes.edgecolor": COLORS["grid"],
            "xtick.color": COLORS["text"],
            "ytick.color": COLORS["text"],
            "font.size": 11,
            "savefig.facecolor": COLORS["background"],
        }
    )


def finish(name, title, xlabel, ylabel):
    plt.title(title, loc="left", pad=18)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis="y", color=COLORS["grid"])
    plt.tight_layout()
    (ROOT / "images").mkdir(exist_ok=True)
    plt.savefig(ROOT / "images" / f"{name}.png", dpi=150)
    plt.close()


def main():
    style()
    sequential = LinearSegmentedColormap.from_list("ember", [COLORS["card"], COLORS["rust"]])
    k = query(
        "SELECT reported_records,area_ha,mean_size_ha,median_size_ha,large_fire_share FROM vw_kpi_summary"
    ).iloc[0]
    concentration = query(
        "SELECT top_pct,selected_records,area_share FROM vw_concentration WHERE reporting_agency='ALL' ORDER BY top_pct"
    )
    pareto = query("SELECT position,cumulative_area_share FROM vw_pareto ORDER BY position")
    plt.figure(figsize=(10, 4.5))
    plt.plot(
        np.r_[0, pareto.position / k.reported_records * 100],
        np.r_[0, pareto.cumulative_area_share * 100],
        color=COLORS["rust"],
    )
    top = concentration.loc[concentration.top_pct.eq(3)].iloc[0]
    plt.scatter(
        top.selected_records / k.reported_records * 100,
        top.area_share * 100,
        color=COLORS["amber"],
        zorder=4,
    )
    plt.annotate(
        f"Top 3%: {top.area_share:.1%} of reported area",
        xy=(top.selected_records / k.reported_records * 100, top.area_share * 100),
        xytext=(23, 65),
        arrowprops={"arrowstyle": "->", "color": COLORS["amber"]},
    )
    finish(
        "concentration",
        "A small share of records accounts for most reported area",
        "Records ordered largest first (%)",
        "Cumulative reported area (%)",
    )
    sizes = query("SELECT size_ha FROM vw_analysis")
    plt.figure(figsize=(10, 4.5))
    plt.hist(np.log1p(sizes.size_ha), bins=45, color=COLORS["rust"])
    finish(
        "size_distribution",
        "Reported sizes vary widely; zeros remain in the distribution",
        "log(1 + reported size in hectares)",
        "Reported records",
    )
    annual = query(
        "SELECT year,reported_records,area_ha,five_year_mean_area FROM vw_annual_trend ORDER BY year"
    )
    plt.figure(figsize=(11, 4.5))
    ax = plt.gca()
    ax.axvspan(
        annual.year.min() - 0.5,
        annual.year.max() + 0.5,
        facecolor="none",
        edgecolor=COLORS["grid"],
        hatch="///",
        zorder=0,
    )
    plt.bar(
        annual.year,
        annual.area_ha / 1e6,
        color=COLORS["rust"],
        label="Annual reported area",
        zorder=2,
    )
    plt.plot(
        annual.year,
        annual.five_year_mean_area / 1e6,
        color=COLORS["amber"],
        label="Full five-year mean",
        zorder=3,
    )
    plt.legend(facecolor=COLORS["card"], labelcolor=COLORS["text"])
    peak_row = annual.loc[annual.area_ha.idxmax()]
    plt.annotate(
        f"{int(peak_row.year)}: {peak_row.area_ha / 1e6:.2f}M ha\npending NFD reconciliation",
        xy=(peak_row.year, peak_row.area_ha / 1e6),
        xytext=(2008, 14.5),
        arrowprops={"arrowstyle": "->", "color": COLORS["amber"]},
        color=COLORS["text"],
    )
    finish(
        "annual_burden",
        "Annual reported area | reporting completeness unverified throughout",
        "Source year",
        "Million reported hectares",
    )
    plt.figure(figsize=(11, 4))
    plt.bar(annual.year, annual.reported_records, color=COLORS["sand"])
    finish(
        "annual_records",
        "Annual selected reporting records | not verified unique incidents",
        "Source year",
        "Reported records",
    )
    season = query("SELECT reporting_agency,month_num,reported_records,area_ha FROM vw_seasonality")
    known = season.loc[season.month_num.between(1, 12)]
    matrix = (
        known.pivot(index="reporting_agency", columns="month_num", values="reported_records")
        .reindex(columns=range(1, 13))
        .fillna(0)
    )
    shares = matrix.div(matrix.sum(axis=1), axis=0) * 100
    plt.figure(figsize=(11, 6))
    plt.imshow(shares, aspect="auto", cmap=sequential, vmin=0)
    plt.xticks(
        range(12),
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    )
    plt.yticks(range(len(shares)), shares.index)
    plt.colorbar(label="Share of valid-month agency records (%)")
    finish(
        "seasonality",
        "Seasonal reporting patterns differ across reporting agencies",
        "Source month",
        "Reporting agency",
    )
    causes = query(
        "SELECT cause_class,SUM(reported_records) AS records,SUM(area_ha) AS area_ha FROM vw_cause GROUP BY cause_class"
    )
    pos = np.arange(len(causes))
    plt.figure(figsize=(10, 4.5))
    plt.bar(
        pos - 0.18,
        causes.records / causes.records.sum() * 100,
        0.36,
        color=COLORS["sand"],
        label="Record share",
    )
    plt.bar(
        pos + 0.18,
        causes.area_ha / causes.area_ha.sum() * 100,
        0.36,
        color=COLORS["rust"],
        label="Reported-area share",
    )
    plt.xticks(pos, causes.cause_class)
    plt.legend(facecolor=COLORS["card"], labelcolor=COLORS["text"])
    finish(
        "causes",
        "Count share and reported-area share answer different questions",
        "Recorded cause class",
        "Share (%)",
    )
    agencies = query(
        "SELECT reporting_agency,reported_records,area_ha,large_fire_share,unknown_cause_share FROM vw_agency ORDER BY area_ha"
    )
    plt.figure(figsize=(10, 5))
    plt.barh(agencies.reporting_agency, agencies.area_ha / 1e6, color=COLORS["rust"])
    finish(
        "agency_burden",
        "Reported-area burden by reporting agency | not geographic provinces",
        "Million reported hectares",
        "Reporting agency",
    )
    quality = query(
        "SELECT year,SUM(source_records) AS source_records,SUM(missing_report_date_share*source_records)/SUM(source_records) AS missing_date_share,SUM(unknown_cause_share*source_records)/SUM(source_records) AS unknown_cause_share FROM vw_quality_trend WHERE year BETWEEN 2000 AND 2025 AND reporting_agency<>'PE' GROUP BY year ORDER BY year"
    )
    plt.figure(figsize=(11, 4.5))
    plt.plot(
        quality.year,
        quality.missing_date_share * 100,
        label="Missing report date",
        color=COLORS["muted"],
    )
    plt.plot(
        quality.year,
        quality.unknown_cause_share * 100,
        label="Unknown cause",
        color=COLORS["sand"],
        linestyle="--",
    )
    plt.legend(facecolor=COLORS["card"], labelcolor=COLORS["text"])
    finish(
        "quality_trends",
        "Source-data gaps vary over time | before analytical exclusions",
        "Source year",
        "Share of source records (%)",
    )
    coverage = query(
        "SELECT reporting_agency,year,source_records,coverage_status FROM vw_coverage WHERE year BETWEEN 2000 AND 2025"
    )
    cm = coverage.pivot(index="reporting_agency", columns="year", values="source_records")
    outside = coverage.assign(
        outside=coverage.coverage_status.eq("Outside documented coverage")
    ).pivot(index="reporting_agency", columns="year", values="outside")
    color_map = LinearSegmentedColormap.from_list("context", [COLORS["card"], COLORS["sand"]])
    color_map.set_bad("#7A6F68")
    plt.figure(figsize=(12, 5))
    plt.imshow(np.log1p(cm).mask(outside), aspect="auto", cmap=color_map)
    plt.xticks(range(0, len(cm.columns), 2), cm.columns[::2], rotation=45)
    plt.yticks(range(len(cm)), cm.index)
    plt.colorbar(label="log(1 + source records)")
    finish(
        "coverage",
        "Source coverage | grey cells are outside documented agency years",
        "Source year",
        "Reporting agency (presence does not prove completeness)",
    )
    sensitivity = query(
        "SELECT scenario,years,reported_records,area_ha,mean_annual_area FROM vw_largest_year_sensitivity"
    )
    peak = annual.loc[annual.area_ha.idxmax()]
    monthly = season.groupby("month_num").reported_records.sum()
    valid_monthly = monthly.loc[monthly.index > 0]
    segments = query(
        "SELECT reporting_agency,cause_class,month_num,reported_records,large_fire_share,do_not_rank FROM vw_segments"
    )
    largest_agency = agencies.iloc[-1]
    metrics = {
        "reported_records": int(k.reported_records),
        "reported_area_ha": float(k.area_ha),
        "mean_size_ha": float(k.mean_size_ha),
        "median_size_ha": float(k.median_size_ha),
        "top_shares": {
            str(int(r.top_pct)): float(r.area_share) for r in concentration.itertuples()
        },
        "peak_area_year": int(peak.year),
        "peak_area_ha": float(peak.area_ha),
        "peak_area_status": "pending NFD reconciliation",
        "peak_record_month": int(valid_monthly.idxmax()),
        "peak_month_records": int(valid_monthly.max()),
        "invalid_month_records": int(monthly.get(-1, 0)),
        "largest_reporting_agency": largest_agency.reporting_agency,
        "largest_agency_reported_area_ha": float(largest_agency.area_ha),
        "unranked_segments": int(segments.do_not_rank.sum()),
        "total_segments": len(segments),
        "mean_annual_area_without_largest_year": float(
            sensitivity.loc[
                sensitivity.scenario.eq("Largest area year removed"), "mean_annual_area"
            ].iloc[0]
        ),
        "mean_annual_area_all_years": float(
            sensitivity.loc[sensitivity.scenario.eq("All selected years"), "mean_annual_area"].iloc[
                0
            ]
        ),
    }
    (PROCESSED / "analysis_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
