"""Choose and evaluate an alert policy without using the final test outcomes."""

import numpy as np
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score


def choose_threshold(labels, scores, miss_cost):
    if miss_cost <= 0 or not np.isfinite(miss_cost):
        raise ValueError("Miss cost must be finite and positive.")
    labels, scores = np.asarray(labels), np.asarray(scores)
    order = np.argsort(-scores, kind="stable")
    labels, scores = labels[order], scores[order]
    # Ties must move together under the inclusive score >= threshold rule.
    last = np.r_[np.flatnonzero(scores[:-1] != scores[1:]), len(scores) - 1]
    true_alerts = labels.cumsum()[last]
    alerts = last + 1
    thresholds = np.r_[np.nextafter(scores[0], np.inf), scores[last]]
    misses = np.r_[labels.sum(), labels.sum() - true_alerts]
    false_alerts = np.r_[0, alerts - true_alerts]
    costs = miss_cost * misses + false_alerts
    # Equal cost favors fewer misses, then the higher threshold.
    best = np.lexsort((-thresholds, misses, costs))[0]
    return float(thresholds[best])


def evaluate(labels, scores, threshold, miss_cost):
    predictions = scores >= threshold
    tn, fp, fn, tp = map(int, confusion_matrix(labels, predictions, labels=[0, 1]).ravel())

    def rate(numerator, denominator):
        return numerator / denominator if denominator else None

    both_classes = bool((tp + fn) and (tn + fp))
    return {
        "threshold": threshold,
        "records": tn + fp + fn + tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp,
        "accuracy": rate(tp + tn, tn + fp + fn + tp),
        "precision": rate(tp, tp + fp),
        "recall": rate(tp, tp + fn),
        "specificity": rate(tn, tn + fp),
        "f1": rate(2 * tp, 2 * tp + fp + fn),
        "roc_auc": float(roc_auc_score(labels, scores)) if both_classes else None,
        "average_precision": float(average_precision_score(labels, scores))
        if both_classes
        else None,
        "alert_share": rate(tp + fp, tn + fp + fn + tp),
        "cost_units": miss_cost * fn + fp,
    }
