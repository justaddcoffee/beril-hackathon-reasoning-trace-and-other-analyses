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

Subagent traces are dropped (they aren't standalone sessions). Sessions from
non-opt-in users are dropped via the consent filter; if data/consent.csv
doesn't exist yet, a warning is emitted and analysis runs unfiltered (for
bootstrap only - do not publish those outputs).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.consent import filter_sessions  # noqa: E402
from src.outcomes import outcomes_dir, to_records  # noqa: E402

DEFAULT_CONSENT = REPO / "data" / "consent.csv"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", type=Path, help="path to claudefiles trace directory")
    p.add_argument("--consent", type=Path, default=DEFAULT_CONSENT,
                   help=f"path to consent.csv (default: {DEFAULT_CONSENT.relative_to(REPO)})")
    p.add_argument("--no-consent-filter", action="store_true",
                   help="skip consent filter even if consent.csv exists")
    args = p.parse_args()
    root = args.root.expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    outs = outcomes_dir(root)
    if not outs:
        sys.exit(f"no .jsonl files under {root}")

    main_outs = [o for o in outs if not o.is_subagent]
    n_sub = len(outs) - len(main_outs)
    if not args.no_consent_filter:
        n_before = len(main_outs)
        main_outs = filter_sessions(main_outs, args.consent, strict=False)
        if len(main_outs) != n_before:
            print(f"consent filter: {len(main_outs)}/{n_before} sessions kept "
                  f"({n_before - len(main_outs)} dropped)")
    if not main_outs:
        sys.exit("0 sessions left after filtering - refusing to write an empty "
                 "CSV. Fill in data/consent.csv or pass --no-consent-filter.")

    records = to_records(main_outs)
    csv_path = REPO / "notes" / "02_outcomes_to_label.csv"
    csv_path.parent.mkdir(exist_ok=True)
    with csv_path.open("w") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    n_manu = sum(1 for o in main_outs if o.has_manuscript_like)
    print(f"\nwrote {csv_path} ({len(records)} sessions, {n_sub} subagent traces excluded)")
    print(f"  {n_manu} sessions have a manuscript-like file path (paper|manuscript|draft|...)")
    print(f"  {sum(1 for o in main_outs if o.n_files_written == 0)} sessions wrote nothing")
    print()
    print("Next: open the CSV in your editor of choice and fill in the `label` column")
    print("with one of {nothing, partial, real}.  ~30 sec/session if you trust the")
    print("snippets; longer if you want to spot-check by opening the trace.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
