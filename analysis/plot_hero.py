"""The banner at the top of README.md.

Not a chart. No axes, no gridlines, nothing to read off: this has to be
legible in about a second and make someone want the rest of the file.

Each phone is drawn at a fixed width with its height proportional to the
memory the device reports, so the outline's AREA is that memory. The filled
part is the share the app gets before jetsam, taken off the height, so the
filled AREA works out proportional to the allowance alone and the three bands
come out nearly the same size however tall the phone is. The picture makes
the claim rather than illustrating it.

Every number, including the two ratios in the strapline, is computed from
plot_findings.CEILING rather than typed in, so none of it can drift away from
the data it cites.

Output:
  results/charts/hero.png

    python3 analysis/plot_hero.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from plot_findings import CEILING, CHARTS_DIR, SERIES_2

GB = 1e9

PANEL = "#14161a"
TEXT = "#f4f3ef"
DIM = "#8a8884"
EMPTY = "#2a2d33"

PHONE_W = 7.2       # same for every device, so height alone carries the memory
TALLEST = 23.0
BASELINE = 6.0
GAP = 6.4


def strapline():
    """The sharpest true sentence the ceiling data supports.

    Two of the three devices return the same limit to the byte despite a wide
    gap in physical memory, which is a blunter fact than any ratio across the
    whole range. If a future run breaks that tie the function falls back to
    the range, so the banner cannot end up asserting a coincidence that is no
    longer in the data.
    """
    by_limit = {}
    for _, ram, limit in CEILING:
        by_limit.setdefault(limit, []).append(ram)

    tied = [rams for rams in by_limit.values() if len(rams) > 1]
    if tied:
        rams = max(tied, key=lambda r: max(r) - min(r))
        gap = max(rams) - min(rams)
        if gap > 0:
            return f"{gap / GB:.0f} GB more RAM. Not one extra byte."

    rams = [ram for _, ram, _ in CEILING]
    limits = [limit for _, _, limit in CEILING]
    return (f"{max(rams) / min(rams):.1f}x the RAM. "
            f"{(max(limits) / min(limits) - 1) * 100:.0f}% more room.")


def plot_hero():
    rams = [ram for _, ram, _ in CEILING]
    limits = [limit for _, _, limit in CEILING]
    scale = TALLEST / max(rams)

    fig, ax = plt.subplots(figsize=(10, 3.4))
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(PANEL)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 33)
    ax.axis("off")

    ax.text(4, 25.4,
            f"{min(rams) / GB:.1f} to {max(rams) / GB:.1f} GB of RAM.",
            fontsize=25, color=TEXT, weight="bold", va="center")
    ax.text(4, 18.6,
            f"{min(limits) / GB:.1f} to {max(limits) / GB:.1f} GB for your app.",
            fontsize=25, color=SERIES_2, weight="bold", va="center")
    ax.text(4, 11.4, strapline(), fontsize=14, color=TEXT, va="center")
    ax.text(4, 7.2, "Measured on the devices, not read off a spec sheet.",
            fontsize=11.5, color=DIM, va="center")

    x = 55.0
    for name, ram, limit in CEILING:
        height = ram * scale
        share = limit / ram

        body = FancyBboxPatch((x, BASELINE), PHONE_W, height,
                              boxstyle="round,pad=0,rounding_size=1.4",
                              facecolor=EMPTY, edgecolor=DIM, linewidth=1.3)
        ax.add_patch(body)

        fill = Rectangle((x, BASELINE), PHONE_W, height * share,
                         facecolor=SERIES_2, edgecolor="none", zorder=2)
        ax.add_patch(fill)
        # square corners would otherwise sit outside the rounded bottom
        fill.set_clip_path(body)

        ax.text(x + PHONE_W / 2, BASELINE + height * share / 2,
                f"{share * 100:.0f}%", ha="center", va="center",
                fontsize=11, color="#ffffff", weight="bold", zorder=3)

        chip = name.split("\n")[-1]
        ax.text(x + PHONE_W / 2, BASELINE - 1.3, chip, ha="center", va="top",
                fontsize=10.5, color=TEXT)
        ax.text(x + PHONE_W / 2, BASELINE - 4.0, f"{ram / GB:.1f} GB",
                ha="center", va="top", fontsize=9.5, color=DIM)

        x += PHONE_W + GAP

    fig.tight_layout(pad=0.2)
    # not plot_findings._save: that one writes the light chart background,
    # which would put a white border round a dark panel.
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, "hero.png")
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.06,
                facecolor=PANEL)
    plt.close(fig)
    print("wrote " + path)
    return path


if __name__ == "__main__":
    plot_hero()
