"""Train models, freeze the alert threshold and evaluate later fire seasons."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data import CATEGORICAL, FEATURES, NUMERIC, ROOT, TARGET, load_cohort, split_cohort, summarize
from .evaluation import choose_threshold, evaluate

SEED = 42
MODEL_SETTINGS = {
    "Logistic regression": {"C": 1.0, "max_iter": 400, "random_state": SEED},
    "Gradient boosting": {
        "max_iter": 120,
        "max_leaf_nodes": 15,
        "learning_rate": 0.08,
        "early_stopping": False,
        "random_state": SEED,
    },
}


def candidates():
    preprocessing = ColumnTransformer(
        [
            (
                "coordinates",
                make_pipeline(
                    SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
                    StandardScaler(),
                ),
                NUMERIC,
            ),
            (
                "reporting context",
                make_pipeline(
                    SimpleImputer(strategy="constant", fill_value="Unknown"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                CATEGORICAL,
            ),
        ]
    )
    return {
        "Logistic regression": make_pipeline(
            clone(preprocessing), LogisticRegression(**MODEL_SETTINGS["Logistic regression"])
        ),
        "Gradient boosting": make_pipeline(
            clone(preprocessing),
            HistGradientBoostingClassifier(**MODEL_SETTINGS["Gradient boosting"]),
        ),
    }


def scores(model, rows):
    return model.predict_proba(rows[FEATURES])[:, 1]


def validate(model, train):
    temporal = []
    for start in range(2010, 2020, 2):
        earlier = train.loc[train.year.lt(start)]
        later = train.loc[train.year.between(start, start + 1)]
        fitted = clone(model).fit(earlier[FEATURES], earlier[TARGET])
        temporal.append(
            {
                "validation_years": f"{start}–{start + 1}",
                "average_precision": float(
                    average_precision_score(later[TARGET], scores(fitted, later))
                ),
                "positive_share": float(later[TARGET].mean()),
            }
        )

    # An interpolation diagnostic within the training era only. It cannot choose the model.
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    stratified = []
    for i, j in splitter.split(train[FEATURES], train[TARGET]):
        left, right = train.iloc[i], train.iloc[j]
        fitted = clone(model).fit(left[FEATURES], left[TARGET])
        stratified.append(float(average_precision_score(right[TARGET], scores(fitted, right))))
    temporal_scores = [row["average_precision"] for row in temporal]
    return {
        "forward_folds": temporal,
        "forward_mean": float(np.mean(temporal_scores)),
        "forward_standard_deviation": float(np.std(temporal_scores, ddof=1)),
        "stratified_folds": stratified,
        "stratified_mean": float(np.mean(stratified)),
        "stratified_standard_deviation": float(np.std(stratified, ddof=1)),
    }


def run(database, output, miss_cost):
    if not np.isfinite(miss_cost) or miss_cost <= 0:
        raise ValueError("Miss cost must be finite and positive.")
    data, excluded = load_cohort(database)
    splits = split_cohort(data)
    train, calibration, test = splits.values()
    models = candidates()
    validation = {name: validate(model, train) for name, model in models.items()}
    chosen = max(models, key=lambda name: validation[name]["forward_mean"])
    model = models[chosen].fit(train[FEATURES], train[TARGET])
    calibration_scores = scores(model, calibration)
    policies = {
        f"Miss cost {cost:g}×": choose_threshold(calibration[TARGET], calibration_scores, cost)
        for cost in sorted({2.0, 5.0, miss_cost, 20.0})
    }
    selected = policies[f"Miss cost {miss_cost:g}×"]

    # Only now read test outcomes for scoring. All policies were fixed above.
    test_scores = scores(model, test)
    constant = DummyClassifier(strategy="prior").fit(train[FEATURES], train[TARGET])
    test_policies = {
        "Default 0.50": evaluate(test[TARGET], test_scores, 0.5, miss_cost),
        "Alert every record": evaluate(test[TARGET], test_scores, 0.0, miss_cost),
        "Alert no records": evaluate(test[TARGET], test_scores, 2.0, miss_cost),
        **{
            name: evaluate(test[TARGET], test_scores, cutoff, miss_cost)
            for name, cutoff in policies.items()
        },
    }
    yearly = {
        str(year): evaluate(group[TARGET], scores(model, group), selected, miss_cost)
        for year, group in test.groupby("year")
    }
    with database.open("rb") as stream:
        warehouse_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    result = {
        "study": "Canada wildfire large-fire triage",
        "warehouse_sha256": warehouse_hash,
        "scikit_learn_version": sklearn.__version__,
        "size_threshold_hectares": 200,
        "miss_cost": miss_cost,
        "excluded_ambiguous_identity": excluded,
        "split_profile": {name: summarize(rows) for name, rows in splits.items()},
        "validation": validation,
        "model_settings": MODEL_SETTINGS,
        "selected_model": chosen,
        "selected_policy": f"Miss cost {miss_cost:g}×",
        "calibration_policies": {
            name: evaluate(calibration[TARGET], calibration_scores, cutoff, miss_cost)
            for name, cutoff in policies.items()
        },
        "test_prevalence_baseline": evaluate(test[TARGET], scores(constant, test), 0.5, miss_cost),
        "test_policies": test_policies,
        "test_by_year": yearly,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "evaluation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8"
    )
    for filename, grain, rows in [
        ("test_policies.csv", "policy", test_policies),
        ("test_by_year.csv", "year", yearly),
    ]:
        with (output / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=[grain, *next(iter(rows.values()))])
            writer.writeheader()
            writer.writerows({grain: key, **metrics} for key, metrics in rows.items())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warehouse", type=Path, default=ROOT / "data/warehouse/wildfire.db")
    parser.add_argument("--output", type=Path, default=ROOT / "modeling/results")
    parser.add_argument("--miss-cost", type=float, default=10)
    args = parser.parse_args()
    result = run(args.warehouse, args.output, args.miss_cost)
    print(result["selected_model"], result["test_policies"][result["selected_policy"]])


if __name__ == "__main__":
    main()
