import numpy as np
import pandas as pd

from src.config import ROOT
from src.prepare_cnfdb import prepare_frame, window_options


def fixture():
    raw = pd.read_csv(ROOT / "tests/fixtures/cnfdb_sample.csv", low_memory=False)
    mapping = pd.read_csv(ROOT / "data/seeds/cause_mapping.csv")
    return raw, mapping


def test_rows_and_source_evidence_are_retained():
    raw, mapping = fixture()
    raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
    d = prepare_frame(raw, mapping)
    assert len(d) == len(raw)
    assert d.source_row.is_unique
    assert bool(d.exact_duplicate_row.iloc[-1])
    assert not bool(d.eligible_for_analysis.iloc[-1])
    pd.testing.assert_frame_equal(d[raw.columns], raw)


def test_invalid_values_are_flagged_without_imputation():
    raw, mapping = fixture()
    raw.loc[0, ["LATITUDE", "LONGITUDE", "SIZE_HA", "MONTH", "REP_DATE"]] = [
        0,
        0,
        -999,
        0,
        "not-a-date",
    ]
    d = prepare_frame(raw, mapping)
    assert bool(d.loc[0, "invalid_coordinates"])
    assert bool(d.loc[0, "invalid_size"])
    assert bool(d.loc[0, "invalid_month"])
    assert bool(d.loc[0, "invalid_report_date"])
    assert pd.isna(d.loc[0, "grid_cell"])
    assert pd.isna(d.loc[0, "is_large_fire"])
    assert d.loc[0, "SIZE_HA"] == -999


def test_thresholds_and_half_open_classes():
    raw, mapping = fixture()
    raw = raw.iloc[:6].copy()
    raw["SIZE_HA"] = [0, 1, 10, 200, 1000, 10000]
    d = prepare_frame(raw, mapping)
    assert len(d.size_class.unique()) == len(raw)
    assert d.is_large_fire.tolist() == [False, False, False, True, True, True]
    assert d.loc[3, "size_class"] == "200 to under 1,000 ha"


def test_seed_mapping_and_local_response_codes():
    raw, mapping = fixture()
    raw.loc[0, "CAUSE"] = "N"
    raw.loc[0, "RESPONSE"] = "SUP"
    d = prepare_frame(raw, mapping)
    assert d.loc[0, "cause_class"] == "Natural/lightning"
    assert d.loc[0, "response_class"] == "Unmapped local code"
    assert "province_territory" not in d.columns


def test_grid_uses_rounding_not_floor():
    raw, mapping = fixture()
    raw.loc[0, ["LATITUDE", "LONGITUDE"]] = [53.8, -113.8]
    d = prepare_frame(raw, mapping)
    assert d.loc[0, "grid_cell"] == "54_-114"


def test_prescribed_evidence_in_secondary_cause_is_flagged():
    raw, mapping = fixture()
    raw.loc[0, "CAUSE2"] = "H-PB"
    d = prepare_frame(raw, mapping)
    assert bool(d.loc[0, "known_prescribed"])
    assert not bool(d.loc[0, "eligible_for_analysis"])


def test_date_inversions_retained_and_flagged():
    raw, mapping = fixture()
    raw.loc[0, "REP_DATE"] = "2020-07-10"
    raw.loc[0, "OUT_DATE"] = "2020-07-09"
    d = prepare_frame(raw, mapping)
    assert bool(d.loc[0, "out_before_report"])
    assert d.loc[0, "out_date"] == pd.Timestamp("2020-07-09")


def test_window_options_are_candidates_not_a_selected_filter():
    raw, mapping = fixture()
    d = prepare_frame(raw, mapping)
    options = window_options(d)
    assert options.option.is_unique
    assert options.includes_PE.any()
    assert not np.isnan(options.records).any()
