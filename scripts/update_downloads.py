#!/usr/bin/env python3
"""Refresh the Daybreak download count in README.md.

The count comes from the Horizon mod registry index, the same file the launcher
and playhorizon.dev read. The registry refreshes it hourly from GitHub's
download counts of the release assets.
"""
import json
import re
import sys
import urllib.request

INDEX_URL = "https://horizon-rust.github.io/horizon-mods/index.json"
PROJECT_ID = "daybreak"
README = "README.md"
MARKER = re.compile(
    r"(<!-- daybreak-downloads -->).*?(<!-- /daybreak-downloads -->)", re.S
)


def fmt(n: int) -> str:
    # Rounded down, so the README never claims more than the launcher shows.
    if n >= 1_000_000:
        return f"{n // 100_000 / 10:g}M"
    if n >= 1_000:
        return f"{n // 1_000}k"
    return str(n)


def main() -> int:
    with urllib.request.urlopen(INDEX_URL, timeout=30) as resp:
        index = json.load(resp)
    project = next((p for p in index["projects"] if p["id"] == PROJECT_ID), None)
    if not project or not project.get("downloads"):
        print(f"no download count for {PROJECT_ID}, leaving README as it is")
        return 0

    tag = f"<code>{fmt(project['downloads'])}+ downloads</code>"
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if not MARKER.search(text):
        print("marker not found in README.md", file=sys.stderr)
        return 1
    new = MARKER.sub(lambda m: m.group(1) + tag + m.group(2), text)
    if new != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
    print(f"{PROJECT_ID}: {project['downloads']} -> {tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
