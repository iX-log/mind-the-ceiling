"""Collapse the empty bands out of the device screenshots used in README.md.

The app draws its readout at the top of the screen and its controls at the
bottom, so a full-device screenshot is mostly black in between: 72% of the
rows in the quick-run shot and 63% in the sustained one carry nothing at all.
At README width that empty space costs more vertical room than the content.

This rewrites each source screenshot with every blank band longer than
MIN_RUN_PX collapsed down to KEEP_PX, and writes the result to
results/screenshots/readme/. Nothing else about the image changes: no
rescaling, no recompression of the content, no cropping of anything that is
not uniformly black.

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


def collapse_blank_bands(img):
    """Return img with every blank band longer than MIN_RUN_PX shortened."""
    blank = np.array(img.convert("L")).max(axis=1) < BLANK_LEVEL
    keep = np.ones(img.height, dtype=bool)

    row = 0
    while row < img.height:
        if not blank[row]:
            row += 1
            continue
        end = row
        while end < img.height and blank[end]:
            end += 1
        if end - row > MIN_RUN_PX:
            keep[row + KEEP_PX // 2 : end - KEEP_PX // 2] = False
        row = end

    return Image.fromarray(np.array(img)[np.flatnonzero(keep)])


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in SCREENSHOTS:
        src = os.path.join(SRC_DIR, name)
        img = Image.open(src).convert("RGB")
        out = collapse_blank_bands(img)
        out.save(os.path.join(OUT_DIR, name))
        removed = img.height - out.height
        print(
            f"{name}: {img.height} -> {out.height} px "
            f"({removed} px of blank rows removed, "
            f"{removed / img.height * 100:.0f}%)"
        )


if __name__ == "__main__":
    main()
