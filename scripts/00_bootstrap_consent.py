#!/usr/bin/env python3
"""Step 0: generate a stub consent CSV listing every user_dir found in the
trace tree, with empty display_name and consent columns for the human to
fill in from the Google Sheet.

Usage:
    python3 scripts/00_bootstrap_consent.py data/claudefiles/

Writes data/consent.csv (gitignored). If the file already exists, refuses
to overwrite unless --force is passed - the existing file likely has the
human's filled-in decisions and shouldn't be clobbered.

Each row gets:
    user_dir      - directory name (the join key against trace paths)
    display_name  - blank, for the human to fill in from the Sheet
    consent       - blank, fill in one of: opt_in, opt_out, no_reply, team
    n_sessions    - main-session count (read-only convenience; sort the CSV
                    by this to label the heaviest users first)

After filling in the CSV, every script that aggregates across users will
automatically intersect against the opt-in set.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.inventory import inventory_dir  # noqa: E402

OUT = REPO / "data" / "consent.csv"
HEADER = ["user_dir", "display_name", "consent", "n_sessions"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", type=Path, help="path to claudefiles/ root")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing data/consent.csv")
    args = p.parse_args()

    root = args.root.expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")
    if OUT.exists() and not args.force:
        sys.exit(f"{OUT} already exists. Use --force to overwrite "
                 f"(this will erase any filled-in consent decisions).")

    sessions = inventory_dir(root)
    main_s = [s for s in sessions if not s.is_subagent]
    if not main_s:
        sys.exit("no main sessions found")

    counts = Counter(s.user_dir for s in main_s)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        for user_dir, n in counts.most_common():
            w.writerow([user_dir, "", "", n])

    print(f"wrote {OUT} with {len(counts)} users")
    print("next: open the file, fill display_name and consent for each row")
    print("      consent values: opt_in | opt_out | no_reply | team")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
