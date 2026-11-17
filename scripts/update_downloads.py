#!/usr/bin/env python3
"""Redraw the Daybreak download pill (assets/chips/daybreak-downloads.svg).

The count comes from the Horizon mod registry index, the same file the launcher
and playhorizon.dev read. The registry refreshes it hourly from GitHub's
download counts of the release assets.

Text is drawn as outlines from scripts/downloads-chip.json (Inter, SIL OFL),
so the pill looks the same for every viewer and needs no web font. Dark and
light colours switch with prefers-color-scheme inside the SVG.
"""
import json
import os
import re
import sys
import urllib.request

INDEX_URL = "https://horizon-rust.github.io/horizon-mods/index.json"
PROJECT_ID = "daybreak"
HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "..", "assets", "chips", "daybreak-downloads.svg")
README = os.path.join(HERE, "..", "README.md")
DATA = os.path.join(HERE, "downloads-chip.json")

# Layout in px: pill height, text size, paddings. The extra 6 px below the
# pill keep it apart from the language chips on the next line.
H, MARGIN, SIZE = 28, 6, 13
PAD_L, ICON, ICON_GAP, WORD_GAP, ARROW_GAP, ARROW, PAD_R = 10, 14, 7, 5, 8, 11, 10


def fmt(n: int) -> str:
    # Rounded down, so the profile never claims more than the launcher shows.
    if n >= 1_000_000:
        return f"{n // 100_000 / 10:g}M+"
    if n >= 1_000:
        return f"{n // 1_000}k+"
    return str(n)


def draw(shown: str) -> str:
    data = json.load(open(DATA, encoding="utf-8"))
    font = data["count"]
    scale = SIZE / font["upm"]
    base = H / 2 + SIZE * 0.36
    x0 = PAD_L + ICON + ICON_GAP

    glyphs, x = [], x0
    for ch in shown:
        g = font["glyphs"][ch]
        glyphs.append(
            f'<path transform="translate({x:.2f} {base:.2f}) scale({scale:.6f} -{scale:.6f})" d="{g["d"]}"/>'
        )
        x += g["w"] * scale
    label_x = x + WORD_GAP
    w = round(label_x + data["label"]["w"] + ARROW_GAP + ARROW + PAD_R)
    title = f"{shown} downloads on Horizon"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H + MARGIN}" '
        f'viewBox="0 0 {w} {H + MARGIN}" role="img" aria-label="{title}"><title>{title}</title>'
        f'{data["style"]}\n'
        f'<rect class="abg" x=".5" y=".5" width="{w - 1}" height="{H - 1}" rx="{H / 2}"/>\n'
        f'<g class="aic" transform="translate({PAD_L} {(H - ICON) / 2}) scale({ICON / 16})">{data["icon"]}</g>\n'
        f'<g class="atx">{"".join(glyphs)}</g>\n'
        f'<path class="atx" opacity=".85" transform="translate({label_x:.2f} {base:.2f})" d="{data["label"]["d"]}"/>\n'
        f'<g class="aic" opacity=".7" transform="translate({w - PAD_R - ARROW} {(H - ARROW) / 2}) '
        f'scale({ARROW / 16})">{data["arrow"]}</g></svg>\n'
    )


def main() -> int:
    with urllib.request.urlopen(INDEX_URL, timeout=30) as resp:
        index = json.load(resp)
    project = next((p for p in index["projects"] if p["id"] == PROJECT_ID), None)
    if not project or not project.get("downloads"):
        print(f"no download count for {PROJECT_ID}, leaving the pill as it is")
        return 0

    shown = fmt(project["downloads"])
    svg = draw(shown)
    old = open(SVG, encoding="utf-8").read() if os.path.exists(SVG) else ""
    if svg != old:
        with open(SVG, "w", encoding="utf-8") as f:
            f.write(svg)
    # Keep the alt text of the pill in the README in step with the image.
    readme = open(README, encoding="utf-8").read()
    new = re.sub(
        r'(src="assets/chips/daybreak-downloads\.svg" alt=")[^"]*(")',
        lambda m: f"{m.group(1)}{shown} downloads on Horizon{m.group(2)}",
        readme,
    )
    if new != readme:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
    print(f"{PROJECT_ID}: {project['downloads']} -> {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
