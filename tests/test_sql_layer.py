import sqlite3

import numpy as np
import pandas as pd
import pytest

from src.config import ROOT
from src.load_warehouse import build_database
from src.prepare_cnfdb import prepare_frame
from src.reconcile import reconcile
from src.review_analysis import NATIONAL_SEGMENTS_SQL, NT_SQL


@pytest.fixture
def warehouse(tmp_path):
    raw = pd.read_csv(ROOT / "tests/fixtures/cnfdb_sample.csv", low_memory=False)
    mapping = pd.read_csv(ROOT / "data/seeds/cause_mapping.csv")
    d = prepare_frame(raw, mapping)
    p = tmp_path / "wildfire.db"
    build_database(d, p)
    return p, d


def test_constraints_unknowns_and_row_counts(warehouse):
    p, d = warehouse
    with sqlite3.connect(p) as db:
        assert not db.execute("PRAGMA foreign_key_check").fetchall()
        assert db.execute("SELECT COUNT(*) FROM fact_fire").fetchone()[0] == len(d)
        for table, key in [
            ("dim_date", "date_key"),
            ("dim_agency", "agency_key"),
            ("dim_cause", "cause_key"),
            ("dim_response", "response_key"),
            ("dim_size_class", "size_class_key"),
            ("dim_year", "year_key"),
            ("dim_month", "month_key"),
        ]:
            assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE {key}=-1").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE fact_fire SET size_ha=-1 WHERE fire_key=1")


def test_rebuild_is_idempotent(warehouse):
    p, d = warehouse
    build_database(d, p)
    with sqlite3.connect(p) as db:
        assert db.execute("SELECT COUNT(*) FROM fact_fire").fetchone()[0] == len(d)
        assert db.execute("SELECT COUNT(*) FROM load_batch").fetchone()[0] == 1


def test_every_reference_view_reconciles_on_fixture(warehouse):
    p, d = warehouse
    with sqlite3.connect(p) as db:
        assert all(c["status"] == "pass" for c in reconcile(d, db))


def test_analysis_and_quality_scripts_execute(warehouse):
    p, _ = warehouse
    with sqlite3.connect(p) as db:
        for name in ["02_analysis_queries.sql", "04_quality_checks.sql", "05_reconciliation.sql"]:
            db.executescript((ROOT / "sql" / name).read_text())


def test_new_reporting_queries_reconcile_to_source_fixture(warehouse):
    p, d = warehouse
    selected = d[
        d.eligible_for_analysis & d.year.between(2000, 2025) & d.reporting_agency.ne("PE")
    ].copy()
    selected["month_num"] = selected.month_num.where(~selected.invalid_month, -1)
    expected = (
        selected.groupby(["cause_class", "month_num"])
        .agg(records=("source_row", "size"), large_fire_records=("is_large_fire", "sum"))
        .sort_index()
    )
    with sqlite3.connect(p) as db:
        actual = (
            pd.read_sql_query(NATIONAL_SEGMENTS_SQL, db)
            .set_index(["cause_class", "month_num"])
            .sort_index()
        )
        assert np.allclose(
            actual[["records", "large_fire_records"]].astype(float), expected.astype(float)
        )
        assert np.allclose(
            actual.large_fire_share.astype(float),
            (expected.large_fire_records / expected.records).astype(float),
        )
        nt = selected.loc[selected.reporting_agency.eq("NT")].copy()
        nt["response_classification"] = nt.response_code.where(
            nt.response_code.isin(["FUL", "MOD", "MON"]), "Unknown"
        )
        expected_nt = (
            nt.groupby("response_classification")
            .agg(records=("source_row", "size"), area_ha=("size_ha", "sum"))
            .sort_index()
        )
        actual_nt = pd.read_sql_query(NT_SQL, db).set_index("response_classification").sort_index()
        assert np.allclose(actual_nt, expected_nt)


def test_even_and_odd_median(tmp_path):
    raw = pd.read_csv(ROOT / "tests/fixtures/cnfdb_sample.csv").iloc[:4].copy()
    raw["YEAR"] = 2020
    raw["SRC_AGENCY"] = "AB"
    raw["PRESCRIBED"] = "No"
    raw["FIRE_TYPE"] = "Wildfire"
    raw["CAUSE2"] = "N"
    raw["PROTZONE"] = ""
    raw["SIZE_HA"] = [1.0, 2.0, 10.0, 100.0]
    d = prepare_frame(raw, pd.read_csv(ROOT / "data/seeds/cause_mapping.csv"))
    p = tmp_path / "median.db"
    build_database(d, p)
    with sqlite3.connect(p) as db:
        assert db.execute("SELECT median_size_ha FROM vw_kpi_summary").fetchone()[0] == 6
        db.execute("UPDATE fact_fire SET in_analysis=0 WHERE fire_key=4")
        assert db.execute("SELECT median_size_ha FROM vw_kpi_summary").fetchone()[0] == 2


def test_fixture_reference_views_match_pandas(warehouse):
    p, d = warehouse
    expected = d[d.eligible_for_analysis & d.year.between(2000, 2025) & d.reporting_agency.ne("PE")]
    with sqlite3.connect(p) as db:
        k = pd.read_sql_query(
            "SELECT reported_records,area_ha,mean_size_ha,median_size_ha,large_fire_records FROM vw_kpi_summary",
            db,
        ).iloc[0]
        assert k.reported_records == len(expected)
        assert np.isclose(k.area_ha, expected.size_ha.sum())
        assert np.isclose(k.mean_size_ha, expected.size_ha.mean())
        assert np.isclose(k.median_size_ha, expected.size_ha.median())
        assert k.large_fire_records == expected.is_large_fire.sum()
        for view, keys in [
            ("vw_seasonality", ["reporting_agency", "month_num"]),
            ("vw_cause", ["reporting_agency", "cause_class"]),
            ("vw_agency", ["reporting_agency"]),
        ]:
            x = expected.copy()
            x["month_num"] = x.month_num.where(~x.invalid_month, -1)
            a = (
                x.groupby(keys)
                .agg(reported_records=("source_row", "size"), area_ha=("size_ha", "sum"))
                .sort_index()
            )
            b = (
                pd.read_sql_query(
                    f"SELECT {','.join(keys)},reported_records,area_ha FROM {view}", db
                )
                .set_index(keys)
                .sort_index()
            )
            assert np.allclose(a, b)
