"""Collapse the empty bands out of the device screenshots used in README.md.

The app draws its readout at the top of the screen and its controls at the
bottom, so a full-device screenshot is mostly black in between: 72% of the
rows in the quick-run shot and 63% in the sustained one carry nothing at all.
At README width that empty space costs more vertical room than the content.

Each source screenshot is rewritten with every blank band longer than
MIN_RUN_PX collapsed down to KEEP_PX, and the results are padded back out to
a common height so they line up when README.md shows them side by side. The
padding goes back into the largest blank band rather than onto the bottom
edge, which would cut off the rounded corner of the screen.

Nothing else about the images changes: no rescaling, no cropping of anything
that is not uniformly black, no touching of a single row that has content in
it.

The sources in results/screenshots/ are the record of what was on screen and
are never modified. These outputs exist only so README.md can show the same
screenshots without the dead space, and are regenerated rather than edited:

    python3 analysis/make_readme_crops.py
"""

import os

import numpy as np
from PIL import Image

SRC_DIR = "results/screenshots"
OUT_DIR = "results/screenshots/readme"

# A row counts as blank when no pixel in it is brighter than this. The app
# renders on pure black, so anything with text in it clears this easily.
BLANK_LEVEL = 25

# Bands shorter than this are real layout spacing and are left alone. Longer
# ones are collapsed to KEEP_PX so the sections stay visually separated.
MIN_RUN_PX = 80
KEEP_PX = 40

SCREENSHOTS = [
    "iphone17promax-quick-fp16-cold.png",
    "iphone17promax-sustained-summary.png",
]


def blank_rows(arr):
    """Boolean mask of rows with no pixel brighter than BLANK_LEVEL."""
    return arr.max(axis=(1, 2)) < BLANK_LEVEL if arr.ndim == 3 else arr.max(axis=1) < BLANK_LEVEL


def blank_bands(mask, minimum=1):
    """Yield (start, end) for each run of True at least `minimum` rows long."""
    row = 0
    while row < len(mask):
        if not mask[row]:
            row += 1
            continue
        end = row
        while end < len(mask) and mask[end]:
            end += 1
        if end - row >= minimum:
            yield row, end
        row = end


def collapse(arr, extra=0):
    """Shorten every blank band longer than MIN_RUN_PX down to KEEP_PX.

    `extra` rows are left in the band that was largest in the source, which is
    how the two screenshots are brought to a common height: the space goes
    back into the gap it was taken from, rather than onto the top margin
    (which shifts the whole screen down) or into some other gap the app only
    ever drew a few pixels of.
    """
    bands = list(blank_bands(blank_rows(arr), MIN_RUN_PX + 1))
    if not bands:
        return arr
    largest = max(bands, key=lambda b: b[1] - b[0])

    keep = np.ones(len(arr), dtype=bool)
    for start, end in bands:
        hold = KEEP_PX + (extra if (start, end) == largest else 0)
        cut_from, cut_to = start + hold // 2, end - (hold - hold // 2)
        if cut_to > cut_from:
            keep[cut_from:cut_to] = False
    return arr[np.flatnonzero(keep)]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    sources = {n: np.array(Image.open(os.path.join(SRC_DIR, n)).convert("RGB")) for n in SCREENSHOTS}
    collapsed = {n: collapse(a) for n, a in sources.items()}
    target = max(len(a) for a in collapsed.values())

    for name in SCREENSHOTS:
        out = collapse(sources[name], extra=target - len(collapsed[name]))
        Image.fromarray(out).save(os.path.join(OUT_DIR, name))
        original = len(sources[name])
        print(
            f"{name}: {original} -> {len(out)} px "
            f"({original - len(out)} px of blank rows removed, "
            f"{(original - len(out)) / original * 100:.0f}%)"
        )

    print(f"both written at {target} px tall, so they align side by side")


if __name__ == "__main__":
    main()
