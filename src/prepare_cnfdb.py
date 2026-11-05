"""Flag source records without silently discarding or correcting evidence."""

import hashlib
import json

import numpy as np
import pandas as pd

from src.config import (
    AGENCY_STARTS,
    END_YEAR,
    LARGE_FIRE_HA,
    PROCESSED,
    RAW,
    ROOT,
    SELECTED_WINDOW,
    SIZE_BINS,
    SIZE_LABELS,
    SOURCE_FILE,
    SOURCE_VERSION,
    WINDOW_OPTIONS,
)


def text_values(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().replace("", pd.NA)


def prepare_frame(raw: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    required = {
        "NFDBFIREID",
        "SRC_AGENCY",
        "YEAR",
        "MONTH",
        "DAY",
        "SIZE_HA",
        "CAUSE",
        "CAUSE2",
        "LATITUDE",
        "LONGITUDE",
        "REP_DATE",
        "ATTK_DATE",
        "OUT_DATE",
        "RESPONSE",
        "PROTZONE",
        "PRESCRIBED",
        "FIRE_TYPE",
    }
    if not required.issubset(raw.columns):
        raise ValueError(f"Missing fields: {sorted(required - set(raw.columns))}")
    if mapping.cause_code.duplicated().any():
        raise ValueError("Cause mapping codes must be unique")
    d = raw.copy()
    d.insert(0, "source_row", np.arange(1, len(d) + 1))
    d["source_version"] = SOURCE_VERSION
    d["exact_duplicate_row"] = raw.duplicated()
    d["repeated_fire_id"] = text_values(raw.NFDBFIREID).duplicated(keep=False)
    d["reporting_agency"] = text_values(raw.SRC_AGENCY).str.upper().replace({"PEI": "PE"})
    d["unknown_reporting_agency"] = ~d.reporting_agency.isin(AGENCY_STARTS)
    # Agency is never assigned to a geographic province in this case study.
    for source, target in [
        ("YEAR", "year"),
        ("MONTH", "month_num"),
        ("DAY", "day_num"),
        ("SIZE_HA", "size_ha"),
        ("LATITUDE", "latitude"),
        ("LONGITUDE", "longitude"),
    ]:
        d[target] = pd.to_numeric(raw[source], errors="coerce")
    d["invalid_year"] = ~(d.year.between(1, END_YEAR) & d.year.mod(1).eq(0))
    d["invalid_month"] = ~(d.month_num.between(1, 12) & d.month_num.mod(1).eq(0))
    d["missing_size"] = d.size_ha.isna()
    d["invalid_size"] = ~(d.size_ha.ge(0) & np.isfinite(d.size_ha))
    d["zero_size"] = d.size_ha.eq(0)
    d["invalid_coordinates"] = ~(
        d.latitude.between(41, 84)
        & d.longitude.between(-141, -52)
        & np.isfinite(d.latitude)
        & np.isfinite(d.longitude)
    )
    d["outside_documented_agency_years"] = (
        d.year.lt(d.reporting_agency.map(AGENCY_STARTS))
        | d.invalid_year
        | d.unknown_reporting_agency
    )
    date_fields = {"REP_DATE": "report_date", "ATTK_DATE": "attack_date", "OUT_DATE": "out_date"}
    for field, target in date_fields.items():
        raw_dates = text_values(raw[field])
        d[target] = pd.to_datetime(raw_dates, format="mixed", errors="coerce")
        d[f"missing_{target}"] = raw_dates.isna()
        d[f"invalid_{target}"] = raw_dates.notna() & d[target].isna()
    calendar = pd.to_datetime(
        pd.DataFrame({"year": d.year, "month": d.month_num, "day": d.day_num}), errors="coerce"
    )
    d["invalid_calendar_date"] = calendar.isna() | d.invalid_year
    d["report_calendar_conflict"] = (
        d.report_date.notna() & calendar.notna() & d.report_date.dt.normalize().ne(calendar)
    )
    d["out_before_report"] = (
        d.out_date.notna() & d.report_date.notna() & d.out_date.lt(d.report_date)
    )
    d["attack_before_report"] = (
        d.attack_date.notna() & d.report_date.notna() & d.attack_date.lt(d.report_date)
    )
    # Keep every parsed date. The separate calendar date is never imputed.
    d["calendar_date"] = calendar.mask(d.invalid_calendar_date)
    d["cause_code"] = text_values(raw.CAUSE).str.upper()
    mapper = mapping.set_index("cause_code").cause_class.to_dict()
    d["cause_class"] = d.cause_code.map(mapper).fillna("Unknown")
    d["unmapped_cause"] = ~d.cause_code.isin(mapper)
    d["unknown_cause"] = d.cause_class.eq("Unknown")
    d["response_code"] = text_values(raw.RESPONSE)
    d["response_class"] = d.response_code.str.upper().map(
        {"FUL": "Full response", "MOD": "Modified response", "MON": "Monitored"}
    )
    d["response_class"] = d.response_class.fillna(
        d.response_code.map(lambda x: "Unknown" if pd.isna(x) else "Unmapped local code")
    )
    d["known_prescribed"] = text_values(raw.PRESCRIBED).str.upper().isin(["PB", "1", "YES", "Y"])
    for field in ["CAUSE", "CAUSE2", "FIRE_TYPE", "PROTZONE"]:
        d["known_prescribed"] |= text_values(raw[field]).str.contains(
            r"prescribed|\bPB\b", case=False, na=False
        )
    d["month_name"] = (
        d.month_num.where(~d.invalid_month)
        .map(
            dict(
                enumerate(
                    [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ],
                    1,
                )
            )
        )
        .fillna("Unknown")
    )
    d["season"] = d.month_num.map(
        {
            12: "Winter",
            1: "Winter",
            2: "Winter",
            3: "Spring",
            4: "Spring",
            5: "Spring",
            6: "Summer",
            7: "Summer",
            8: "Summer",
            9: "Autumn",
            10: "Autumn",
            11: "Autumn",
        }
    ).fillna("Unknown")
    d["decade"] = ((d.year.where(~d.invalid_year) // 10) * 10).astype("Int64")
    usable_size = d.size_ha.where(~d.invalid_size)
    d["size_class"] = pd.cut(usable_size, SIZE_BINS, right=False, labels=SIZE_LABELS)
    d["is_large_fire"] = usable_size.ge(LARGE_FIRE_HA).where(usable_size.notna()).astype("boolean")
    d["grid_latitude"] = d.latitude.where(~d.invalid_coordinates).round(0)
    d["grid_longitude"] = d.longitude.where(~d.invalid_coordinates).round(0)
    d["grid_cell"] = (
        d.grid_latitude.astype("Int64").astype("string")
        + "_"
        + d.grid_longitude.astype("Int64").astype("string")
    ).where(~d.invalid_coordinates)
    d["eligible_for_analysis"] = ~(
        d.invalid_year
        | d.invalid_size
        | d.unknown_reporting_agency
        | d.outside_documented_agency_years
        | d.exact_duplicate_row
        | d.known_prescribed
    )
    return d


def coverage_frame(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for agency, start in AGENCY_STARTS.items():
        for year in range(min(AGENCY_STARTS.values()), END_YEAR + 1):
            g = d.loc[d.reporting_agency.eq(agency) & d.year.eq(year)]
            usable = g.loc[g.eligible_for_analysis]
            rows.append(
                {
                    "reporting_agency": agency,
                    "year": year,
                    "source_records": len(g),
                    "analysis_eligible_records": len(usable),
                    "reported_area_ha": usable.size_ha.sum() if len(usable) else np.nan,
                    "unknown_cause_records": int(g.unknown_cause.sum()),
                    "missing_report_date_records": int(g.missing_report_date.sum()),
                    "missing_size_records": int(g.missing_size.sum()),
                    "invalid_month_records": int(g.invalid_month.sum()),
                    "documented_start_year": start,
                    "coverage_status": "Outside documented coverage"
                    if year < start
                    else (
                        "Records present; completeness unverified"
                        if len(g)
                        else "No records; completeness unknown"
                    ),
                }
            )
    return pd.DataFrame(rows)


def window_options(d: pd.DataFrame) -> pd.DataFrame:
    options = []
    for label, (start, include_pe) in WINDOW_OPTIONS.items():
        mask = d.eligible_for_analysis & d.year.between(start, END_YEAR)
        if not include_pe:
            mask &= d.reporting_agency.ne("PE")
        g = d.loc[mask]
        options.append(
            {
                "option": label,
                "start_year": start,
                "end_year": END_YEAR,
                "includes_PE": include_pe,
                "reporting_agencies": g.reporting_agency.nunique(),
                "records": len(g),
                "reported_area_ha": float(g.size_ha.sum()),
                "unknown_cause_pct": float(g.unknown_cause.mean() * 100),
                "missing_report_date_pct": float(g.missing_report_date.mean() * 100),
                "invalid_month_pct": float(g.invalid_month.mean() * 100),
            }
        )
    return pd.DataFrame(options)


def main() -> dict:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    source_version = pd.read_csv(ROOT / "data/source_versions.csv", dtype=str).iloc[0]
    if hashlib.sha256((RAW / SOURCE_FILE).read_bytes()).hexdigest() != source_version.sha256:
        raise ValueError(
            "Source checksum differs from the recorded snapshot. Review before preparing."
        )
    raw = pd.read_csv(RAW / SOURCE_FILE, low_memory=False)
    d = prepare_frame(raw, pd.read_csv(ROOT / "data/seeds/cause_mapping.csv"))
    d.to_csv(PROCESSED / "cnfdb_flagged.csv", index=False)
    coverage_frame(d).to_csv(PROCESSED / "agency_year_coverage.csv", index=False)
    window_options(d).to_csv(PROCESSED / "window_options.csv", index=False)
    flags = [
        "exact_duplicate_row",
        "repeated_fire_id",
        "invalid_year",
        "invalid_month",
        "missing_size",
        "invalid_size",
        "zero_size",
        "invalid_coordinates",
        "outside_documented_agency_years",
        "missing_report_date",
        "invalid_report_date",
        "missing_attack_date",
        "invalid_attack_date",
        "missing_out_date",
        "invalid_out_date",
        "invalid_calendar_date",
        "report_calendar_conflict",
        "out_before_report",
        "attack_before_report",
        "unknown_cause",
        "unmapped_cause",
        "known_prescribed",
    ]
    q = {
        "source_rows": len(raw),
        "retained_rows": len(d),
        "analysis_eligible_rows_all_years": int(d.eligible_for_analysis.sum()),
        "flagged_rows": {c: int(d[c].sum()) for c in flags},
        "selected_window": SELECTED_WINDOW,
    }
    (PROCESSED / "quality_summary.json").write_text(json.dumps(q, indent=2), encoding="utf-8")
    print(json.dumps(q, indent=2))
    print(window_options(d).to_string(index=False))
    return q


if __name__ == "__main__":
    main()
