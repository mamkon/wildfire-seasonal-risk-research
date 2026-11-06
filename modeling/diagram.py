"""Render the verified pipeline as a 300 dots-per-inch image and a vector file."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent
INK = "#152C33"
MUTED = "#39555C"
TEAL = "#E2F4EF"
BLUE = "#E8F2FC"
GRAY = "#F0F4F6"
AMBER = "#FCECCB"
RUST = "#FADBD4"


def render(report, output):
    fig, ax = plt.subplots(figsize=(16, 10), facecolor="#FFFFFF")
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(0, 16), ylim=(0, 10))
    ax.axis("off")

    def card(x, y, width, height, title, body, fill, title_size=13):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                width,
                height,
                boxstyle="round,pad=0.035,rounding_size=0.15",
                facecolor=fill,
                edgecolor="#CAD9DC",
                linewidth=0.8,
            )
        )
        ax.text(
            x + 0.19, y + height - 0.18, title, va="top", size=title_size, color=INK, weight="bold"
        )
        ax.text(
            x + 0.19,
            y + height - (0.45 + title_size / 95),
            body,
            va="top",
            size=10,
            color=MUTED,
            linespacing=1.38,
        )

    def percent(value):
        return "undefined" if value is None else f"{value:.1%}"

    card(
        0.45,
        8.72,
        15.1,
        0.98,
        "Canada wildfire large-fire triage",
        "Predict whether a recorded fire reaches 200 hectares  •  Python, SQLite, scikit-learn, Matplotlib and Power BI",
        TEAL,
        21,
    )
    steps = [
        ("1  Ingest", "Validate the archive\nand audit missingness"),
        ("2  Split", "Separate seasons\nbefore preprocessing"),
        ("3  Validate", "Compare models on\nfive forward folds"),
        ("4  Set the alert rule", "Tune the cutoff on\n2020–2022 only"),
        ("5  Score later years", "Apply the frozen rule\nto 2023–2025"),
    ]
    for i, (title, body) in enumerate(steps):
        x = 0.45 + i * 3.08
        card(x, 7.16, 2.78, 1.15, title, body, (TEAL, BLUE, GRAY, AMBER, TEAL)[i])
        if i < 4:
            ax.annotate(
                "",
                xy=(x + 3.02, 7.72),
                xytext=(x + 2.81, 7.72),
                arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 1.6},
            )

    profile = report["split_profile"]
    fit = report["validation"][report["selected_model"]]
    selected = report["test_policies"][report["selected_policy"]]
    settings = report["model_settings"][report["selected_model"]]
    regularization = settings.get("C")
    model_detail = (
        f"Regularization setting {regularization:g} and at most {settings['max_iter']} iterations."
        if regularization is not None
        else f"{settings['max_iter']} rounds, {settings['max_leaf_nodes']} leaves per tree and learning rate {settings['learning_rate']:g}."
    )
    card(
        0.45,
        5.06,
        7.38,
        1.72,
        "Cohort and outcome",
        "\n".join(
            f"{label}   {row['records']:,} records  ·  {percent(row['positive_share'])} reached 200 hectares"
            for label, row in profile.items()
        ),
        GRAY,
    )
    card(
        8.17,
        5.06,
        7.38,
        1.72,
        "Inputs and fitting",
        "Report month, reporting agency, latitude and longitude.\n"
        "Fit missing-value handling, scaling and encoding inside each fold.\n"
        "Compare logistic regression and gradient boosting.",
        BLUE,
    )
    card(
        0.45,
        3.09,
        7.38,
        1.65,
        "Model selection",
        f"{report['selected_model']}  ·  {model_detail}\n"
        f"Forward average precision {fit['forward_mean']:.3f}  ·  standard deviation {fit['forward_standard_deviation']:.3f}\n"
        "Historical stratified folds serve as an interpolation check.",
        TEAL,
    )
    card(
        8.17,
        3.09,
        7.38,
        1.65,
        "Alert rule",
        f"One missed large fire costs {report['miss_cost']:g} review units in this scenario.\n"
        f"Frozen cutoff {selected['threshold']:.4f}  ·  Test alert share {percent(selected['alert_share'])}\n"
        "A score at or above the cutoff triggers manual review.",
        AMBER,
    )

    card(
        0.45,
        0.45,
        5.05,
        2.27,
        "Final test  ·  2023–2025",
        f"Accuracy {percent(selected['accuracy'])}  ·  Precision {percent(selected['precision'])}\n"
        f"Recall {percent(selected['recall'])}  ·  Specificity {percent(selected['specificity'])}\n"
        f"F1 score {selected['f1']:.3f}  ·  Average precision {selected['average_precision']:.3f}\n"
        f"Receiver operating characteristic area {selected['roc_auc']:.3f}\n"
        "F1 balances precision and recall.",
        GRAY,
    )
    for i, (label, key, fill) in enumerate(
        [
            ("Correctly cleared", "true_negatives", TEAL),
            ("Extra reviews", "false_positives", AMBER),
            ("Missed large fires", "false_negatives", RUST),
            ("Large fires flagged", "true_positives", TEAL),
        ]
    ):
        x, y = 5.82 + (i % 2) * 4.95, 1.75 - (i // 2) * 0.93
        card(x, y, 4.78, 0.82, label, f"{selected[key]:,} records", fill, 11)
    ax.text(
        5.84,
        0.48,
        "Green  correct decision     Amber  review workload     Rust  critical miss",
        color=MUTED,
        size=10,
    )
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "pipeline_workflow.png", dpi=300, facecolor="#FFFFFF")
    vector = output / "pipeline_workflow.svg"
    with matplotlib.rc_context({"svg.hashsalt": "wildfire-workflow"}):
        fig.savefig(vector, facecolor="#FFFFFF", metadata={"Date": None})
    lines = vector.read_text(encoding="utf-8").splitlines()
    vector.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, default=ROOT / "results/evaluation.json")
    parser.add_argument("--output", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    render(json.loads(args.evaluation.read_text(encoding="utf-8")), args.output)
