"""Charts for the approved notebook review additions."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from src.analyse import COLORS, finish, style
from src.review_analysis import tables


def main():
    style()
    t = tables()
    h = t["heaping"]
    pos = np.arange(len(h))
    plt.figure(figsize=(12, 5))
    for offset, col, label, color, hatch in [
        (-0.25, "exactly_zero_pct", "Exactly 0 ha", COLORS["muted"], "///"),
        (0, "exactly_001_pct", "Exactly 0.01 ha", COLORS["sand"], "..."),
        (0.25, "exactly_01_pct", "Exactly 0.1 ha", COLORS["text"], ""),
    ]:
        plt.bar(
            pos + offset,
            h[col],
            0.25,
            label=label,
            color=color,
            hatch=hatch,
            edgecolor=COLORS["grid"],
        )
    plt.xticks(pos, h.reporting_agency)
    plt.legend(facecolor=COLORS["card"], labelcolor=COLORS["text"])
    plt.annotate(
        "Exact values only; near-value checks remain separate",
        xy=(0.02, 0.92),
        xycoords="axes fraction",
        bbox={"facecolor": COLORS["card"], "edgecolor": "none", "alpha": 0.95},
    )
    finish(
        "recording_conventions",
        "Small recorded-size values have different agency patterns",
        "Reporting agency",
        "Share of agency selected records (%)",
    )
    c = t["agency_top3"]
    national = c.loc[c.reporting_agency.eq("ALL"), "area_share"].iloc[0]
    a = c.loc[c.reporting_agency.ne("ALL")].sort_values("area_share")
    plt.figure(figsize=(10, 5))
    plt.barh(a.reporting_agency, a.area_share * 100, color=COLORS["rust"])
    plt.axvline(
        national * 100,
        color=COLORS["amber"],
        linestyle="--",
        label=f"Pooled reference: {national:.2%}",
    )
    plt.legend(facecolor=COLORS["card"], labelcolor=COLORS["text"], loc="lower right")
    plt.annotate(
        f"Within-agency range: {a.area_share.min():.2%} to {a.area_share.max():.2%}",
        xy=(0.02, 0.94),
        xycoords="axes fraction",
        bbox={"facecolor": COLORS["card"], "edgecolor": "none", "alpha": 0.95},
    )
    finish(
        "agency_concentration",
        "Within-agency shares range from 59.46% to 99.56%",
        "Area share from each agency’s largest 3% of records (%)",
        "Reporting agency",
    )
    s = t["national_segments"]
    known = s.loc[s.month_num.gt(0)]
    matrix = known.pivot(
        index="cause_class", columns="month_num", values="large_fire_share"
    ).reindex(columns=range(1, 13))
    blocked = known.pivot(index="cause_class", columns="month_num", values="do_not_rank").reindex(
        columns=range(1, 13)
    )
    cmap = LinearSegmentedColormap.from_list("burden", [COLORS["card"], COLORS["rust"]])
    cmap.set_bad(COLORS["muted"])
    plt.figure(figsize=(12, 4))
    plt.imshow(matrix.mask(blocked.eq(1)) * 100, aspect="auto", cmap=cmap)
    plt.xticks(
        range(12),
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    )
    plt.yticks(range(len(matrix)), matrix.index)
    plt.colorbar(label="Observed large-fire share (%)")
    finish(
        "national_segments",
        "Cause-by-month shares describe selected records, not population risk",
        "Source month; grey cells are not ranked",
        "Recorded cause",
    )
    nt = t["nt_response"]
    pos = np.arange(len(nt))
    plt.figure(figsize=(11, 5))
    plt.barh(pos - 0.18, nt.record_share * 100, 0.36, color=COLORS["sand"], label="Record share")
    plt.barh(
        pos + 0.18, nt.area_share * 100, 0.36, color=COLORS["rust"], label="Reported-area share"
    )
    plt.yticks(pos, nt.response_classification)
    plt.legend(facecolor=COLORS["card"], labelcolor=COLORS["text"], loc="lower right")
    mon = nt.loc[nt.response_classification.eq("MON")].iloc[0]
    plt.annotate(
        f"MON: {mon.record_share:.2%} of records; {mon.area_share:.2%} of area",
        xy=(mon.area_share * 100, 2.18),
        xytext=(12, 3.2),
        arrowprops={"arrowstyle": "->", "color": COLORS["amber"]},
        bbox={"facecolor": COLORS["card"], "edgecolor": "none", "alpha": 0.95},
    )
    finish(
        "nt_response_classification",
        "NT response classification has different record and area shares",
        "Share of all selected NT records or reported area (%)",
        "Response classification; Unknown included",
    )


if __name__ == "__main__":
    main()
