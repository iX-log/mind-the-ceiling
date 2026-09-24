"""Charts for the three session 11/12 findings that had no figure.

Unlike plot_sustained.py and plot_wer.py, these plot summary values rather
than a per-sample series, so every number is declared in DATA below with
the file or screenshot that backs it. Nothing here is computed from a
distribution; if a value changes in RESULTS.md it must change here too.

Outputs:
  results/charts/ceiling-vs-ram.png
  results/charts/quantization-memory.png
  results/charts/low-power-spread.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

CHARTS_DIR = "results/charts"

# --- palette -----------------------------------------------------------
SERIES_1 = "#2a78d6"   # blue
SERIES_2 = "#eb6834"   # orange
INK      = "#0b0b0b"
INK_2    = "#52514e"
MUTED    = "#898781"
GRID     = "#e1e0d9"
AXIS     = "#c3c2b7"
SURFACE  = "#fcfcfb"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK_2,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# --- data --------------------------------------------------------------
# Jetsam limits: every sample of the ceiling probes, sessions 9, 11, 12.
#   A16      results/device-pull/ceiling-iphone14promax-a16-20260915.json
#   A18 Pro  results/device-pull/ceiling-iphone16pro-a18pro-1790161164.json
#   A19 Pro  results/device-pull/ceiling-iphone17promax-a19pro-run{1,2}.json
# physical_memory_bytes: schema-2 sustained runs, sessions 11 and 12.
#   A16      sustained-fp16-1790178261.json
#   A18 Pro  sustained-fp16-1790161164.json
#   A19 Pro  sustained-fp16-1790174217.json
CEILING = [
    ("iPhone 14 Pro Max\nA16",        5_911_134_208, 3_221_225_472),
    ("iPhone 16 Pro\nA18 Pro",        8_014_741_504, 3_539_992_576),
    ("iPhone 17 Pro Max\nA19 Pro",   12_262_113_280, 3_539_992_576),
]

# Cold first load, empty page cache, iPhone 17 Pro Max. Session 12.
# Screenshots: iphone17promax-quick-{fp16-cold,int8,int4}.png
# Single device: quick runs write no file.
QUANT = [
    ("fp16", 39.4, 51.8),
    ("int8", 19.8, 34.1),
    ("int4", 10.0, 66.0),
]

# Quick test, 100 runs, fp16, synthetic, iPhone 17 Pro Max. Session 12.
# Screenshots: iphone17promax-quick-fp16-cold.png (normal),
#              iphone17promax-quick-fp16-lowpower.png (low power)
LOWPOWER = [
    ("Normal",          26.0, 26.2, 26.6, 27.3),
    ("Low Power Mode",  39.5, 50.9, 56.8, 60.9),
]


def _save(fig, name):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print("wrote " + path)
    return path


def plot_ceiling():
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ys = range(len(CEILING))
    h = 0.34
    gap = 0.02
    for i, (name, ram, limit) in enumerate(CEILING):
        ax.barh(i + (h / 2 + gap), ram / 1e9, height=h, color=SERIES_1,
                label="Physical memory, as the device reports it" if i == 0 else None)
        ax.barh(i - (h / 2 + gap), limit / 1e9, height=h, color=SERIES_2,
                label="Memory your app gets before jetsam kills it" if i == 0 else None)
        ax.text(ram / 1e9 + 0.15, i + (h / 2 + gap), f"{ram/1e9:.2f} GB",
                va="center", fontsize=9, color=INK_2)
        ax.text(limit / 1e9 + 0.15, i - (h / 2 + gap), f"{limit:,} bytes",
                va="center", fontsize=9, color=INK_2)

    ax.set_yticks(list(ys))
    ax.set_yticklabels([c[0] for c in CEILING], fontsize=10, color=INK)
    ax.set_xlabel("gigabytes")
    ax.set_xlim(0, 14.6)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    ax.set_title("The limit does not scale with RAM",
                 fontsize=14, color=INK, loc="left", pad=26)
    ax.text(0, 1.045,
            "Two phones 4 GB apart in RAM, identical allowance to the byte",
            transform=ax.transAxes, fontsize=10, color=INK_2)
    ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    fig.tight_layout()
    return _save(fig, "ceiling-vs-ram.png")


def plot_quant():
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    xs = range(len(QUANT))
    w = 0.34
    gap = 0.02
    for i, (name, disk, foot) in enumerate(QUANT):
        ax.bar(i - (w / 2 + gap), disk, width=w, color=SERIES_1,
               label="Size on disk" if i == 0 else None)
        ax.bar(i + (w / 2 + gap), foot, width=w, color=SERIES_2,
               label="Memory at first load" if i == 0 else None)
        ax.text(i - (w / 2 + gap), disk + 1.4, f"{disk:.1f} MB",
                ha="center", fontsize=9.5, color=INK_2)
        ax.text(i + (w / 2 + gap), foot + 1.4, f"{foot:.1f} MB",
                ha="center", fontsize=9.5, color=INK_2)

    ax.set_xticks(list(xs))
    ax.set_xticklabels([q[0] for q in QUANT], fontsize=11, color=INK)
    ax.set_ylabel("megabytes")
    ax.set_ylim(0, 78)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    ax.set_title("Quantization shrinks the file, not the memory",
                 fontsize=14, color=INK, loc="left", pad=26)
    ax.text(0, 1.045,
            "int4 is the smallest download and the largest resident cost",
            transform=ax.transAxes, fontsize=10, color=INK_2)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    fig.tight_layout()
    return _save(fig, "quantization-memory.png")


def plot_lowpower():
    from matplotlib.lines import Line2D
    fig, ax = plt.subplots(figsize=(9.6, 3.8))
    for i, (name, lo, med, p95, hi) in enumerate(LOWPOWER):
        colour = SERIES_1 if i == 0 else SERIES_2
        y = len(LOWPOWER) - 1 - i
        ax.plot([lo, hi], [y, y], color=colour, linewidth=2,
                solid_capstyle="butt", zorder=2)
        for x in (lo, hi):
            ax.plot([x], [y], marker="|", markersize=15, markeredgewidth=2,
                    color=colour, zorder=3)
        ax.plot([med], [y], marker="o", markersize=11, color=colour,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=5)
        ax.plot([p95], [y], marker="D", markersize=7, color=colour,
                markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=4)
        ax.text(lo - 0.9, y, f"{lo:.1f}", va="center", ha="right",
                fontsize=9.5, color=MUTED)
        ax.text(hi + 0.9, y, f"{hi:.1f}", va="center", ha="left",
                fontsize=9.5, color=MUTED)
        ax.text(med, y + 0.26, f"median {med:.1f} ms", ha="center",
                fontsize=10, color=INK_2)
        ax.text(med, y - 0.32, f"spread {hi-lo:.1f} ms", ha="center",
                fontsize=10.5, color=colour, fontweight="bold")

    ax.set_yticks([1, 0])
    ax.set_yticklabels([LOWPOWER[0][0], LOWPOWER[1][0]], fontsize=11, color=INK)
    ax.set_ylim(-0.75, 1.75)
    ax.set_xlim(20, 68)
    ax.set_xlabel("inference latency (ms), 100 runs each")
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    handles = [
        Line2D([], [], marker="o", linestyle="none", markersize=10,
               color=MUTED, markeredgecolor=SURFACE, markeredgewidth=2,
               label="median"),
        Line2D([], [], marker="D", linestyle="none", markersize=7,
               color=MUTED, markeredgecolor=SURFACE, markeredgewidth=1.5,
               label="p95"),
        Line2D([], [], marker="|", linestyle="none", markersize=13,
               markeredgewidth=2, color=MUTED, label="min / max"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False,
              fontsize=9.5, ncol=3, handletextpad=0.4, columnspacing=1.4)
    ax.set_title("Low Power Mode changes the distribution, not just the median",
                 fontsize=14, color=INK, loc="left", pad=30)
    ax.text(0, 1.075,
            "iPhone 17 Pro Max, fp16: min to max widens 16x, from 1.3 ms to 21.4 ms",
            transform=ax.transAxes, fontsize=10, color=INK_2)
    fig.tight_layout()
    return _save(fig, "low-power-spread.png")


def main():
    plot_ceiling()
    plot_quant()
    plot_lowpower()


if __name__ == "__main__":
    main()
