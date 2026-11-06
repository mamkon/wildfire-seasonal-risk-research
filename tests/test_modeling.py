"""Regression checks for the time split and alert rule."""

import numpy as np
import pandas as pd

from modeling.data import split_cohort
from modeling.evaluation import choose_threshold, evaluate


def test_later_seasons_are_disjoint_and_never_used_for_training():
    data = pd.DataFrame(
        {
            "year": [2000, 2019, 2020, 2022, 2023, 2025],
            "large_fire": [0, 1, 0, 1, 0, 1],
        }
    )
    training, calibration, test = split_cohort(data).values()
    assert training.year.max() < calibration.year.min()
    assert calibration.year.max() < test.year.min()
    assert len(training) + len(calibration) + len(test) == len(data)


def test_threshold_minimizes_cost_with_tied_scores_and_extreme_policies():
    labels = np.array([0, 1, 1, 0, 0, 1])
    scores = np.array([0.8, 0.8, 0.7, 0.6, 0.6, 0.3])
    for weight in (0.1, 1, 2, 10):
        threshold = choose_threshold(labels, scores, weight)
        candidate_policies = [
            evaluate(labels, scores, candidate, weight)
            for candidate in [*np.unique(scores), np.nextafter(scores.max(), np.inf)]
        ]
        best = min(
            candidate_policies,
            key=lambda row: (
                row["cost_units"],
                row["false_negatives"],
                -row["threshold"],
            ),
        )
        assert threshold == best["threshold"]


def test_confusion_counts_and_undefined_precision():
    result = evaluate(np.array([0, 1]), np.array([0.1, 0.2]), 0.5, 10)
    assert result["false_negatives"] == 1
    assert result["true_negatives"] == 1
    assert result["precision"] is None
    assert result["cost_units"] == 10
