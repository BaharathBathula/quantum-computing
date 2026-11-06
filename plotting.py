"""Small matplotlib helpers so every figure in outputs/ shares one look."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: write PNGs, never open windows
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "outputs"

INK = "#1f2430"
MUTED = "#6b7280"
GRID = "#e5e7eb"
PALETTE = ["#4f46e5", "#0891b2", "#ea580c", "#16a34a", "#db2777", "#7c3aed"]

plt.rcParams.update(
    {
        "figure.dpi": 110,
        "savefig.dpi": 140,
        "savefig.bbox": "tight",
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.size": 10,
        "legend.frameon": False,
    }
)


def save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_y(1.06)  # keep the figure title clear of subplot titles
    fig.savefig(path)
    plt.close(fig)
    return path


def bar_counts(
    ax, counts: dict[str, int], title: str, color: str = PALETTE[0], all_outcomes: list[str] | None = None
) -> None:
    keys = all_outcomes or sorted(counts)
    vals = [counts.get(k, 0) for k in keys]
    total = sum(counts.values()) or 1
    bars = ax.bar(keys, vals, color=color, width=0.6)
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v,
            f"{v / total:.0%}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=MUTED,
        )
    ax.set_title(title)
    ax.set_ylabel("counts")
    ax.grid(axis="x", visible=False)
