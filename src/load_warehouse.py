"""Build a fresh constrained SQLite database, then atomically replace the old one."""

import calendar
import os
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import AGENCY_STARTS, END_YEAR, PROCESSED, ROOT, SIZE_BINS, SIZE_LABELS

START_YEAR = 2000
EXCLUDED_AGENCIES = ("PE",)
MIN_SEGMENT_RECORDS = 30


def insert_frame(db, table, frame):
    values = frame.astype(object).where(frame.notna(), None)
    cols = ",".join('"' + str(c) + '"' for c in frame.columns)
    marks = ",".join("?" for _ in frame.columns)
    db.executemany(
        f"INSERT INTO {table} ({cols}) VALUES ({marks})", values.itertuples(index=False, name=None)
    )


def build_database(d: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".building.sqlite")
    if temp.exists():
        temp.unlink()
    version = pd.read_csv(ROOT / "data/source_versions.csv", dtype=str).iloc[0]
    with sqlite3.connect(temp) as db:
        db.executescript((ROOT / "sql/01_schema.sql").read_text())
        db.execute(
            "INSERT INTO load_batch VALUES (?,?,?,?,?)",
            (1, version.version, version.sha256, START_YEAR, END_YEAR),
        )
        agencies = {-1: ("Unknown", "Unknown", None)}
        agencies.update(
            {i: (a, a, AGENCY_STARTS[a]) for i, a in enumerate(sorted(AGENCY_STARTS), 1)}
        )
        db.executemany(
            "INSERT INTO dim_agency VALUES (?,?,?,?)", [(k, *v) for k, v in agencies.items()]
        )
        agency_keys = {v[0]: k for k, v in agencies.items()}
        causes = pd.read_csv(ROOT / "data/seeds/cause_mapping.csv")
        db.execute("INSERT INTO dim_cause VALUES(-1,'Unknown','Unknown')")
        cause_keys = {}
        for i, r in enumerate(causes.itertuples(index=False), 1):
            db.execute("INSERT INTO dim_cause VALUES(?,?,?)", (i, r.cause_code, r.cause_class))
            cause_keys[r.cause_code] = i
        db.execute("INSERT INTO dim_size_class VALUES(-1,'Unknown',-1,NULL,NULL)")
        for i, label in enumerate(SIZE_LABELS, 1):
            upper = SIZE_BINS[i]
            db.execute(
                "INSERT INTO dim_size_class VALUES(?,?,?,?,?)",
                (i, label, i, SIZE_BINS[i - 1], None if np.isinf(upper) else upper),
            )
        db.execute("INSERT INTO dim_response VALUES(-1,'Unknown','Unknown')")
        response_keys = {}
        for i, code in enumerate(sorted(d.response_code.dropna().unique()), 1):
            label = {"FUL": "Full response", "MOD": "Modified response", "MON": "Monitored"}.get(
                str(code).upper(), "Unmapped local code"
            )
            db.execute("INSERT INTO dim_response VALUES(?,?,?)", (i, code, label))
            response_keys[code] = i
        db.execute("INSERT INTO dim_date VALUES(-1,NULL,-1,-1,'Unknown','Unknown',-1)")
        db.execute("INSERT INTO dim_year VALUES(-1,'Unknown')")
        db.execute("INSERT INTO dim_month VALUES(-1,'Unknown','Unknown')")
        seasons = {
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
        for month in range(1, 13):
            db.execute(
                "INSERT INTO dim_month VALUES(?,?,?)",
                (month, calendar.month_abbr[month], seasons[month]),
            )
        validyears = d.loc[~d.invalid_year, "year"]
        first = min(int(validyears.min()), START_YEAR)
        for year in range(first, END_YEAR + 1):
            db.execute("INSERT INTO dim_year VALUES(?,?)", (year, str(year)))
        dates = pd.date_range(f"{first}-01-01", f"{END_YEAR}-12-31")
        db.executemany(
            "INSERT INTO dim_date VALUES(?,?,?,?,?,?,?)",
            [
                (
                    int(t.strftime("%Y%m%d")),
                    t.strftime("%Y-%m-%d"),
                    t.year,
                    t.month,
                    calendar.month_abbr[t.month],
                    seasons[t.month],
                    t.year // 10 * 10,
                )
                for t in dates
            ],
        )
        f = pd.DataFrame(
            {
                "fire_key": d.source_row,
                "fire_id": d.NFDBFIREID,
                "batch_key": 1,
                "date_key": pd.to_datetime(d.calendar_date, errors="coerce")
                .dt.strftime("%Y%m%d")
                .fillna("-1")
                .astype(int),
                "year_key": d.year.where(~d.invalid_year, -1).astype(int),
                "month_key": d.month_num.where(~d.invalid_month, -1).astype(int),
                "agency_key": d.reporting_agency.map(agency_keys).fillna(-1).astype(int),
                "cause_key": d.cause_code.map(cause_keys).fillna(-1).astype(int),
                "size_class_key": d.size_class.map({s: i for i, s in enumerate(SIZE_LABELS, 1)})
                .fillna(-1)
                .astype(int),
                "response_key": d.response_code.map(response_keys).fillna(-1).astype(int),
                "latitude": d.latitude.where(~d.invalid_coordinates),
                "longitude": d.longitude.where(~d.invalid_coordinates),
                "size_ha": d.size_ha.where(~d.invalid_size),
                "is_large_fire": d.is_large_fire,
                "in_analysis": (
                    d.eligible_for_analysis
                    & d.year.between(START_YEAR, END_YEAR)
                    & ~d.reporting_agency.isin(EXCLUDED_AGENCIES)
                ).astype(int),
                "grid_cell": d.grid_cell,
                "report_date": pd.to_datetime(d.report_date, errors="coerce").dt.strftime(
                    "%Y-%m-%d"
                ),
                "out_date": pd.to_datetime(d.out_date, errors="coerce").dt.strftime("%Y-%m-%d"),
            }
        )
        flags = [
            "missing_report_date",
            "missing_size",
            "invalid_size",
            "invalid_coordinates",
            "invalid_calendar_date",
            "report_calendar_conflict",
            "exact_duplicate_row",
            "known_prescribed",
            "repeated_fire_id",
            "out_before_report",
        ]
        for flag in flags:
            f[flag] = d[flag].astype(int)
        f["is_large_fire"] = f.is_large_fire.astype("Int64")
        insert_frame(db, "fact_fire", f)
        db.executescript((ROOT / "sql/03_reference_views.sql").read_text())
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Orphan dimension keys detected")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Database integrity check failed")
    db.close()
    os.replace(temp, path)


def main():
    d = pd.read_csv(PROCESSED / "cnfdb_flagged.csv", low_memory=False)
    path = ROOT / "data/warehouse/wildfire.db"
    build_database(d, path)
    export = PROCESSED / "warehouse_exports"
    export.mkdir(exist_ok=True)
    with sqlite3.connect(path) as db:
        names = [
            r[0]
            for r in db.execute(
                "SELECT name FROM sqlite_master WHERE type IN('view','table') ORDER BY name"
            )
        ]
        for name in names:
            # Identifiers come only from this locally defined schema, never user input.
            pd.read_sql_query(f'SELECT * FROM "{name}"', db).to_csv(
                export / f"{name}.csv", index=False
            )
        summary = pd.read_sql_query(
            "SELECT reported_records,area_ha,median_size_ha,large_fire_share FROM vw_kpi_summary",
            db,
        )
    (PROCESSED / "sql_stage_summary.json").write_text(
        summary.iloc[0].to_json(indent=2), encoding="utf-8"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
