#!/usr/bin/env python3
"""Step 1: inventory & shape.

Usage:
    python scripts/01_inventory.py path/to/claudefiles/

Walks the directory recursively, picks up every *.jsonl file, computes
per-session stats, writes notes/01_inventory.csv, and prints a few
histograms / top-tools tables to stdout.

Run this BEFORE forming opinions about anything. It exists to discourage
generalizing from the first three traces you happen to read.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.inventory import inventory_dir, to_records  # noqa: E402


def histogram(values, bins=10, width=40):
    """ASCII histogram. Skips empty / None values."""
    vals = [v for v in values if v is not None]
    if not vals:
        return "  (no values)"
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return f"  all values = {lo}"
    step = (hi - lo) / bins
    buckets = [0] * bins
    for v in vals:
        i = min(int((v - lo) / step), bins - 1)
        buckets[i] += 1
    peak = max(buckets) or 1
    out = []
    for i, count in enumerate(buckets):
        edge_lo = lo + i * step
        edge_hi = edge_lo + step
        bar = "█" * int(width * count / peak)
        out.append(f"  {edge_lo:8.1f}-{edge_hi:8.1f} | {bar} {count}")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1]).expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    sessions = inventory_dir(root)
    if not sessions:
        sys.exit(f"no .jsonl files under {root}")

    records = to_records(sessions)
    out = REPO / "notes" / "01_inventory.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print(f"\nwrote {out} ({len(records)} jsonl files)\n")

    # Subagent traces (.../subagents/agent-*.jsonl) are kept in the CSV but are
    # not standalone sessions, so the shape summary below is computed on the
    # main sessions only.
    main = [s for s in sessions if not s.is_subagent]
    subagents = [s for s in sessions if s.is_subagent]

    # ---- shape summary ----
    print(f"jsonl files: {len(sessions)}  ({len(main)} main sessions, "
          f"{len(subagents)} subagent traces)")
    print(f"users (distinct user_dir): {len({s.user_dir for s in main})}")
    print(f"sessions per user (top 10):")
    per_user = Counter(s.user_dir for s in main)
    for u, n in per_user.most_common(10):
        print(f"  {n:4d}  {u}")

    print("\nturns/session:")
    print(histogram([s.n_user_turns + s.n_assistant_turns for s in main]))

    print("\ntool calls/session:")
    print(histogram([s.n_tool_calls for s in main]))

    print("\nduration (min)/session:")
    print(histogram([s.duration_min for s in main]))

    print("\ntime-to-first-tool (s):")
    print(histogram([s.time_to_first_tool_s for s in main]))

    print("\ntop tools across all main sessions:")
    all_tools: Counter = Counter()
    for s in main:
        all_tools.update(s.tools)
    for tool, n in all_tools.most_common(20):
        print(f"  {n:6d}  {tool}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
