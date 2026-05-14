#!/usr/bin/env python3
"""Step 2: outcome triage CSV.

Usage:
    python scripts/02_outcome_labels.py path/to/claudefiles/

Walks the directory recursively, extracts per-session signals (files written,
last assistant text, last user text, manuscript-like file detected), and
writes notes/02_outcomes_to_label.csv with an empty `label` column.

You then open the CSV and fill in `label` for each row with one of:
    nothing    - session produced no real artifact
    partial    - some scaffolding / fragments / notes but not a paper-shaped thing
    real       - something that looks like a paper-fragment by the end

This is the cheapest signal. Don't grade quality. Just bucket. The bucket is
what makes every later question be "compared to what?"
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.outcomes import outcomes_dir, to_records  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1]).expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    outs = outcomes_dir(root)
    if not outs:
        sys.exit(f"no .jsonl files under {root}")

    records = to_records(outs)
    csv_path = REPO / "notes" / "02_outcomes_to_label.csv"
    csv_path.parent.mkdir(exist_ok=True)
    with csv_path.open("w") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    n_manu = sum(1 for o in outs if o.has_manuscript_like)
    print(f"\nwrote {csv_path} ({len(records)} sessions)")
    print(f"  {n_manu} sessions have a manuscript-like file path (paper|manuscript|draft|...)")
    print(f"  {sum(1 for o in outs if o.n_files_written == 0)} sessions wrote nothing")
    print()
    print("Next: open the CSV in your editor of choice and fill in the `label` column")
    print("with one of {nothing, partial, real}.  ~30 sec/session if you trust the")
    print("snippets; longer if you want to spot-check by opening the trace.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
