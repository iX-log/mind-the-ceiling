"""The opening figure: how much of the phone your app actually gets.

ceiling-vs-ram.png already compares the two numbers as a pair of bars. This
one nests them instead, drawing each phone's whole memory as a track with the
app's allowance filled in, because the point here is proportion rather than
comparison: the track gets longer as phones get bigger and the filled part
does not.

Numbers come from plot_findings.CEILING so there is one place to change them.
That list cites the ceiling probes and schema-2 sustained runs they come from.

Output:
  results/charts/fixed-slice.png

    python3 analysis/plot_slice.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from plot_findings import AXIS, CEILING, INK, INK_2, MUTED, SERIES_2, _save

GB = 1e9
LABEL_ON_FILL = "#ffffff"   # the percentage sits on top of the orange


def plot_slice():
    fig, ax = plt.subplots(figsize=(9.5, 3.6))

    height = 0.52
    for i, (name, ram, limit) in enumerate(CEILING):
        row = len(CEILING) - 1 - i  # biggest phone at the bottom

        # the whole phone
        ax.barh(row, ram / GB, height=height, color="none",
                edgecolor=AXIS, linewidth=1.1, zorder=2)
        # the part your app gets
        ax.barh(row, limit / GB, height=height, color=SERIES_2, zorder=3,
                label="What your app gets before iOS kills it" if i == 0 else None)

        ax.text(limit / GB - 0.14, row, f"{limit / ram * 100:.0f}%",
                va="center", ha="right", fontsize=10, color=LABEL_ON_FILL, zorder=4)
        ax.text(ram / GB + 0.16, row, f"{ram / GB:.1f} GB",
                va="center", fontsize=9.5, color=MUTED, zorder=4)

    ax.set_yticks(range(len(CEILING)))
    ax.set_yticklabels([c[0] for c in reversed(CEILING)], fontsize=10, color=INK)
    ax.set_xlabel("gigabytes")
    ax.set_xlim(0, 13.6)
    ax.set_ylim(-0.6, len(CEILING) - 0.4)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)

    ax.set_title("Your app gets a fixed slice of the phone",
                 fontsize=14, color=INK, loc="left", pad=26)
    ax.text(0, 1.06,
            "The phone gets bigger. The slice does not.",
            transform=ax.transAxes, fontsize=10, color=INK_2)
    # top right is the only corner the tracks do not reach into
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)

    fig.tight_layout()
    return _save(fig, "fixed-slice.png")


if __name__ == "__main__":
    plot_slice()
