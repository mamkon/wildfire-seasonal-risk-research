"""Render the Executive Summary map from rounded CNFDB cells and Natural Earth."""

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parents[1]
LAND = "#344339"
WATER = "#0C2029"
INK = "#F2E6D8"


def render(basemap, destination):
    features = json.loads(basemap.read_text(encoding="utf-8"))["features"]
    with (ROOT / "data/processed/warehouse_exports/vw_grid.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        cells = [
            (int(lat), int(lon), float(row["area_ha"]))
            for row in csv.DictReader(source)
            if "_" in row["grid_cell"]
            for lat, lon in [row["grid_cell"].split("_")]
        ]
    fig = plt.figure(figsize=(10.44, 6.54), facecolor=WATER)
    ax = fig.add_axes((0.025, 0.13, 0.95, 0.72), facecolor=WATER)
    for feature in features:
        name = feature["properties"]["ADMIN"]
        if name not in {"Canada", "United States of America", "Greenland", "France"}:
            continue
        geometry = feature["geometry"]
        polygons = (
            geometry["coordinates"]
            if geometry["type"] == "MultiPolygon"
            else [geometry["coordinates"]]
        )
        for rings in polygons:
            ax.add_patch(
                Polygon(
                    rings[0],
                    facecolor=LAND if name == "Canada" else "#273336",
                    edgecolor="#68756C",
                    linewidth=0.65,
                )
            )
            for ring in rings[1:]:
                ax.add_patch(Polygon(ring, facecolor=WATER, edgecolor="none"))
    groups = [
        (0, 10_000, 9, "#B96850", "Under 10k ha"),
        (10_000, 100_000, 22, "#E38153", "10k–under 100k ha"),
        (100_000, float("inf"), 51, "#FFD08A", "100k ha or more"),
    ]
    for lower, upper, size, color, label in groups:
        points = [(lon, lat) for lat, lon, area in cells if lower <= area < upper]
        x, y = zip(*points, strict=True)
        ax.scatter(x, y, s=size, c=color, alpha=0.87, linewidths=0, label=label)
    ax.set(xlim=(-145, -49), ylim=(40, 84))
    ax.set_axis_off()
    fig.text(0.04, 0.93, "Recorded fire area across Canada", fontsize=21, weight="bold", color=INK)
    fig.text(0.04, 0.875, "Rounded coordinate cells  ·  2000–2025", fontsize=12, color="#C5CCC5")
    fig.legend(
        loc="lower left",
        bbox_to_anchor=(0.032, 0.064),
        ncol=3,
        frameon=False,
        labelcolor=INK,
        fontsize=11,
        handletextpad=0.35,
        columnspacing=1.05,
    )
    fig.text(
        0.04,
        0.035,
        "Cell totals sum reported sizes. Boundaries: Natural Earth.",
        fontsize=10,
        color="#C5CCC5",
    )
    fig.savefig(
        destination,
        dpi=140,
        facecolor=fig.get_facecolor(),
        metadata={"Title": "Recorded fire area across Canada"},
    )
    plt.close(fig)
    print(f"Mapped {len(cells):,} rounded coordinate cells.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("basemap", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "images/executive_recorded_area.png")
    args = parser.parse_args()
    render(args.basemap, args.output)
