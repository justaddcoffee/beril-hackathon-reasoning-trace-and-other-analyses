#!/usr/bin/env python3
"""Step 1d: classify each session by its first user prompt.

Usage:
    python3 scripts/01d_first_prompt_typology.py data/claudefiles/

Writes:
    notes/01d_first_prompts.csv         (one row per session, gitignored)
    notes/figures/05_first_prompt_typology.png       (aggregate distribution)
    notes/figures/06_template_review_project_slugs.png (top project slugs)

The categories are defined in src/typology.py. The finding the figure is
designed to surface: the BERIL hackathon's first-prompt distribution is
heavily dominated by two canned bootstraps (`/berdl_start` and the
"Review the project at projects/<slug>" template), with a small free-form
tail. That shapes how Step 5 coding should be done - the interesting
agent behavior lives in turns 2+, not turn 1.

Subagent traces are dropped (they aren't standalone sessions). Sessions
from non-opt-in users are dropped by the consent filter; pass
--no-consent-filter for internal-only outputs.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.consent import filter_sessions  # noqa: E402
from src.inventory import is_history_path, is_subagent_path, user_dir_from_path  # noqa: E402
from src.typology import CATEGORIES, first_prompt_of  # noqa: E402

DEFAULT_CONSENT = REPO / "data" / "consent.csv"
FIGDIR = REPO / "notes" / "figures"
CSV_OUT = REPO / "notes" / "01d_first_prompts.csv"

# Stable palette per category so colors don't shuffle across runs.
CAT_COLOR = {
    "slash_bootstrap": "#2563eb",
    "template_review": "#0f766e",
    "local_command":   "#94a3b8",
    "empty":           "#cbd5e1",
    "free_form":       "#c026d3",
}


class _Row:
    """Lightweight session row carrying user_dir + the typology fields, so
    filter_sessions (which expects .user_dir) works on it."""
    __slots__ = ("info", "user_dir", "is_subagent")
    def __init__(self, info, user_dir, is_subagent):
        self.info = info
        self.user_dir = user_dir
        self.is_subagent = is_subagent


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

    rows: list[_Row] = []
    for path in sorted(root.glob("**/*.jsonl")):
        if is_subagent_path(path) or is_history_path(path):
            continue
        rows.append(_Row(
            info=first_prompt_of(path),
            user_dir=user_dir_from_path(path),
            is_subagent=False,
        ))
    if not rows:
        sys.exit(f"no .jsonl files under {root}")

    n_before = len(rows)
    if not args.no_consent_filter:
        rows = filter_sessions(rows, args.consent, strict=False)
        if len(rows) != n_before:
            print(f"consent filter: {len(rows)}/{n_before} sessions kept "
                  f"({n_before - len(rows)} dropped)")
    if not rows:
        sys.exit("0 sessions left after filtering - refusing to write empty "
                 "artifacts. Fill in data/consent.csv or pass --no-consent-filter.")

    # ---- CSV ----
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "session_id", "user_dir", "category",
                    "project_slug", "n_chars", "first_prompt"])
        for r in rows:
            d = asdict(r.info)
            w.writerow([d["file"], d["session_id"], r.user_dir, d["category"],
                        d["project_slug"], d["n_chars"], d["first_prompt"]])

    # ---- summary ----
    cats = Counter(r.info.category for r in rows)
    print(f"\nwrote {CSV_OUT} ({len(rows)} sessions)\n")
    print("category distribution:")
    for c in CATEGORIES:
        n = cats.get(c, 0)
        print(f"  {c:18s} {n:4d}  ({n / len(rows):5.1%})")
    unknown = sum(v for k, v in cats.items() if k not in CATEGORIES)
    if unknown:
        print(f"  ?? unknown category: {unknown}")

    slugs = Counter(r.info.project_slug for r in rows if r.info.project_slug)
    print(f"\ntemplate_review project slugs: {len(slugs)} distinct, "
          f"covering {sum(slugs.values())} sessions")
    for s, n in slugs.most_common(10):
        print(f"  {n:4d}  {s}")

    # ---- figure 5: category distribution ----
    FIGDIR.mkdir(parents=True, exist_ok=True)
    ordered = [(c, cats.get(c, 0)) for c in CATEGORIES]
    labels = [c for c, _ in ordered][::-1]
    counts = [n for _, n in ordered][::-1]
    colors = [CAT_COLOR[c] for c in labels]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.barh(labels, counts, color=colors, edgecolor="white", linewidth=0.4)
    for i, n in enumerate(counts):
        ax.text(n + max(counts) * 0.008, i,
                f"{n}  ({n / len(rows):.0%})",
                va="center", fontsize=9)
    ax.set_xlim(0, max(counts) * 1.16)
    ax.set_xlabel("sessions")
    ax.set_title(
        f"BERIL first-prompt typology  ({len(rows)} opt-in sessions)",
        fontsize=12, fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f5 = FIGDIR / "05_first_prompt_typology.png"
    fig.savefig(f5, dpi=130)
    plt.close(fig)
    print(f"\nwrote {f5}")

    # ---- figure 6: top project slugs (when any) ----
    if slugs:
        top = slugs.most_common(20)
        names = [s for s, _ in top][::-1]
        snums = [n for _, n in top][::-1]
        fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.34)))
        ax.barh(names, snums, color="#0f766e", edgecolor="white", linewidth=0.4)
        for i, n in enumerate(snums):
            ax.text(n + max(snums) * 0.01, i, str(n), va="center", fontsize=8)
        ax.set_xlim(0, max(snums) * 1.12)
        ax.set_xlabel("sessions using this project slug")
        ax.set_title(
            f"Project slugs from the \"Review the project at projects/X\" template\n"
            f"top {len(top)} of {len(slugs)} distinct slugs  -  "
            f"{sum(slugs.values())} sessions total",
            fontsize=11, fontweight="bold",
        )
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        f6 = FIGDIR / "06_template_review_project_slugs.png"
        fig.savefig(f6, dpi=130)
        plt.close(fig)
        print(f"wrote {f6}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
