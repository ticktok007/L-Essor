"""
run_distribution_plots.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 14

Generates all 6 distribution plots defined in:
docs/data-quality/distribution_visualization_spec.md

Run: python scripts/run_distribution_plots.py
Requires: pip install matplotlib

Outputs: data/processed/plots/*.png
"""

import collections
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT      = Path(__file__).resolve().parent.parent
SYN       = ROOT / "data" / "synthetic"
PROC      = ROOT / "data" / "processed"
PLOTS_DIR = PROC / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

STYLE = {
    "bar_color":  "#5B7CF6",
    "hist_color": "#E5599B",
    "warn_color": "#F2B84B",
    "ok_color":   "#3FCB88",
    "bg":         "white",
    "spine_off":  ["top", "right"],
}

# ── Loaders ───────────────────────────────────────────────────────────────────

def load_syn(filename: str) -> list[dict[str, str]]:
    path = SYN / filename
    if not path.exists():
        print(f"  WARN: {filename} not found — skipping")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_proc(filename: str) -> list[dict[str, str]]:
    path = PROC / filename
    if not path.exists():
        print(f"  WARN: {filename} not found — skipping")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _floats(rows: list[dict], col: str) -> list[float]:
    out = []
    for r in rows:
        try:
            out.append(float(r[col]))
        except (ValueError, KeyError, TypeError):
            pass
    return out

def _histogram_bins(values: list[float], n_bins: int = 20) -> tuple[list[float], list[int]]:
    """Manual histogram bucketing — no numpy."""
    if not values:
        return [], []
    mn, mx = min(values), max(values)
    if mn == mx:
        return [mn], [len(values)]
    width  = (mx - mn) / n_bins
    counts = [0] * n_bins
    edges  = [mn + i * width for i in range(n_bins + 1)]
    for v in values:
        idx = min(int((v - mn) / width), n_bins - 1)
        counts[idx] += 1
    centers = [(edges[i] + edges[i + 1]) / 2 for i in range(n_bins)]
    return centers, counts

def _style(ax: plt.Axes) -> None:
    for spine in STYLE["spine_off"]:
        ax.spines[spine].set_visible(False)
    ax.set_facecolor(STYLE["bg"])

# ── Plot 1 — Funding stage distribution ──────────────────────────────────────

def plot_funding_stage() -> None:
    rows = load_syn("startup_profiles.csv")
    if not rows:
        return

    counter = collections.Counter(r.get("funding_stage", "unknown") for r in rows)
    stages  = sorted(counter.keys())
    counts  = [counter[s] for s in stages]
    n       = len(rows)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(stages, counts, color=STYLE["bar_color"], edgecolor="white")
    for bar, count in zip(bars, counts):
        ratio = count / n
        color = STYLE["warn_color"] if ratio > 0.60 else STYLE["ok_color"]
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{count}  ({ratio:.0%})", va="center", fontsize=9, color=color)
    ax.set_xlabel("Startup Count")
    ax.set_title("Funding Stage Distribution\n"
                 "Review: no single stage should exceed 60% of total", fontsize=10)
    _style(ax)
    plt.tight_layout()
    out = PLOTS_DIR / "funding_stage_distribution.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out.name}")

# ── Plot 2 — AIS histogram ────────────────────────────────────────────────────

def plot_ais_histogram() -> None:
    rows = load_proc("profile_feature_scores.csv")
    if not rows:
        return

    vals = _floats(rows, "ais_normalized")
    if not vals:
        print("  WARN: ais_normalized column missing — skipping AIS plot")
        return

    centers, counts = _histogram_bins(vals, n_bins=20)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(centers, counts, width=(centers[1] - centers[0]) * 0.9 if len(centers) > 1 else 5,
           color=STYLE["hist_color"], edgecolor="white", alpha=0.85)
    ax.set_xlabel("AIS Normalized Score (0–100)")
    ax.set_ylabel("Profile Count")
    ax.set_title("Achievement Impact Score (AIS) Histogram\n"
                 "Review: should be spread across range — no single spike dominant", fontsize=10)
    _style(ax)
    plt.tight_layout()
    out = PLOTS_DIR / "ais_histogram.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out.name}")

# ── Plot 3 — Degree distribution ─────────────────────────────────────────────

def plot_degree_distribution() -> None:
    rows = load_syn("interaction_edges.csv")
    if not rows:
        return

    degree: collections.Counter = collections.Counter()
    for e in rows:
        degree[e.get("source_profile_id", "")] += 1
        degree[e.get("target_profile_id", "")]  += 1

    values   = list(degree.values())
    max_d    = max(values) if values else 1
    n_bins   = min(30, max_d + 1)
    bin_w    = max(1, math.ceil(max_d / n_bins))
    buckets: collections.Counter = collections.Counter()
    for v in values:
        buckets[v // bin_w] += 1

    xs     = sorted(buckets)
    ys     = [buckets[x] for x in xs]
    labels = [str(x * bin_w) for x in xs]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(len(xs)), ys, color=STYLE["bar_color"], edgecolor="white", linewidth=0.4)
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Node Degree (edges per node)")
    ax.set_ylabel("Number of Nodes")
    ax.set_title("Interaction Graph — Degree Distribution Sanity Check\n"
                 "Review: hub-and-spoke shape expected (few high-degree, many low-degree nodes)",
                 fontsize=10)
    _style(ax)
    plt.tight_layout()
    out = PLOTS_DIR / "degree_distribution.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out.name}")

# ── Plot 4 — Grit histogram ───────────────────────────────────────────────────

def plot_grit_histogram() -> None:
    rows = load_proc("profile_feature_scores.csv")
    if not rows:
        return

    vals = _floats(rows, "grit_normalized")
    if not vals:
        print("  WARN: grit_normalized column missing — skipping Grit plot")
        return

    centers, counts = _histogram_bins(vals, n_bins=20)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(centers, counts, width=(centers[1] - centers[0]) * 0.9 if len(centers) > 1 else 5,
           color="#2BC4C9", edgecolor="white", alpha=0.85)
    ax.set_xlabel("Grit Index Normalized Score (0–100)")
    ax.set_ylabel("Profile Count")
    ax.set_title("Grit Index Histogram\n"
                 "Review: should be spread — not a single spike", fontsize=10)
    _style(ax)
    plt.tight_layout()
    out = PLOTS_DIR / "grit_histogram.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out.name}")

# ── Plot 5 — Label balance ────────────────────────────────────────────────────

def plot_label_balance() -> None:
    rows = load_proc("profile_feature_scores.csv")
    if not rows:
        return

    labels = ["success_prediction_label", "at_risk_label"]
    bounds = {
        "success_prediction_label": (0.35, 0.65),
        "at_risk_label":            (0.20, 0.50),
    }
    n = len(rows)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for ax, lbl in zip(axes, labels):
        try:
            pos = sum(1 for r in rows if int(r.get(lbl, 0)) == 1)
        except ValueError:
            pos = 0
        neg   = n - pos
        ratio = pos / n if n else 0
        lo, hi = bounds[lbl]
        in_range = lo <= ratio <= hi
        color    = STYLE["ok_color"] if in_range else STYLE["warn_color"]

        ax.bar(["Positive\n(label=1)", "Negative\n(label=0)"],
               [pos, neg], color=[color, STYLE["bar_color"]], edgecolor="white")
        ax.set_title(f"{lbl}\nratio={ratio:.2%}  {'✓ in bounds' if in_range else '✗ out of bounds'}",
                     fontsize=9)
        ax.set_ylabel("Count")
        _style(ax)

    fig.suptitle("Target Label Balance — Review: both labels must be within required ratio bounds",
                 fontsize=10)
    plt.tight_layout()
    out = PLOTS_DIR / "label_balance.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out.name}")

# ── Plot 6 — Review flag distribution ────────────────────────────────────────

def plot_review_flag_distribution() -> None:
    rows = load_proc("profile_feature_scores.csv")
    if not rows:
        return

    counter = collections.Counter(r.get("review_flag", "unknown") for r in rows)
    flags   = sorted(counter.keys())
    counts  = [counter[f] for f in flags]
    n       = len(rows)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(flags, counts, color=STYLE["bar_color"], edgecolor="white")
    for bar, count in zip(bars, counts):
        ratio = count / n
        color = STYLE["warn_color"] if ratio > 0.70 else STYLE["ok_color"]
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{count}  ({ratio:.0%})", va="center", fontsize=9, color=color)
    ax.set_xlabel("Profile Count")
    ax.set_title("Review Flag Distribution\n"
                 "Review: all 4 flags should appear; no single flag > 70%", fontsize=10)
    _style(ax)
    plt.tight_layout()
    out = PLOTS_DIR / "review_flag_distribution.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out.name}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 Day 14 — Distribution Plots\n")

    plot_funding_stage()
    plot_ais_histogram()
    plot_degree_distribution()
    plot_grit_histogram()
    plot_label_balance()
    plot_review_flag_distribution()

    print(f"\n  All plots saved → {PLOTS_DIR.resolve()}")


if __name__ == "__main__":
    main()