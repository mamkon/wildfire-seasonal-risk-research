"""Read and validate the reviewed wildfire cohort."""

import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd

NUMERIC = ["latitude", "longitude"]
CATEGORICAL = ["month", "agency"]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "large_fire"
ROOT = Path(__file__).resolve().parents[1]


def load_cohort(path):
    if not path.is_file():
        raise FileNotFoundError(f"Build the reviewed warehouse first: {path}")
    with closing(sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)) as db:
        data = pd.read_sql_query(
            """
            SELECT f.fire_key, f.year_key AS year, f.month_key AS month,
                   a.agency_code AS agency, f.latitude, f.longitude, f.size_ha,
                   f.repeated_fire_id, f.exact_duplicate_row
            FROM fact_fire AS f JOIN dim_agency AS a USING (agency_key)
            WHERE f.in_analysis = 1
            ORDER BY f.year_key, f.fire_key
        """,
            db,
        )
    if data.empty or data.fire_key.duplicated().any():
        raise ValueError("Expected a nonempty cohort with unique warehouse row keys.")
    if (
        not data.year.between(2000, 2025).all()
        or not np.isfinite(data.size_ha).all()
        or (data.size_ha < 0).any()
    ):
        raise ValueError("Invalid year or final size in the eligible cohort.")
    ambiguous = data.repeated_fire_id.eq(1) | data.exact_duplicate_row.eq(1)
    data = data.loc[~ambiguous].copy()
    data[TARGET] = data.size_ha.ge(200).astype(int)
    data["month"] = (
        data.month.where(data.month.between(1, 12))
        .map(lambda value: f"{int(value):02d}" if pd.notna(value) else np.nan)
        .astype(object)
    )
    return data, int(ambiguous.sum())


def split_cohort(data):
    splits = {
        "Training": data.loc[data.year.le(2019)],
        "Threshold calibration": data.loc[data.year.between(2020, 2022)],
        "Final test": data.loc[data.year.ge(2023)],
    }
    for name, rows in splits.items():
        if set(rows[TARGET]) != {0, 1}:
            raise ValueError(f"{name} must have both outcome classes.")
    return splits


def summarize(rows):
    features = rows[FEATURES]
    return {
        "records": len(rows),
        "large_fires": int(rows[TARGET].sum()),
        "positive_share": float(rows[TARGET].mean()),
        "missing_values": {k: int(v) for k, v in features.isna().sum().items()},
        "zero_variance_fields": features.columns[features.nunique() <= 1].tolist(),
    }
