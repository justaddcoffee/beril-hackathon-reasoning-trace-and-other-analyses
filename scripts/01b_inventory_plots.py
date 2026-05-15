#!/usr/bin/env python3
"""Step 1b: turn the inventory into actual figures.

Usage:
    python scripts/01b_inventory_plots.py data/claudefiles/

Re-runs the Step-1 inventory parser over the trace directory (so tool counts
are exact, not the top-5 truncation stored in notes/01_inventory.csv) and
writes PNGs to notes/figures/.

Shape stats are computed on MAIN sessions only (is_subagent == False); subagent
traces are not standalone sessions.

All four shape metrics (turns, tool calls, duration, time-to-first-tool) are
heavy-tailed, so they're drawn on a log-scaled x-axis with log-spaced bins -
the bulk of the distribution stays legible and the tail is shown honestly
rather than clipped. The duration tail in particular has a separate far-right
bump: a handful of session files carry timestamps from months before the
hackathon (pre-existing project dirs), so their "duration" is an artifact.
Zero-valued sessions can't sit on a log axis; they're counted in the
annotation instead.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.inventory import inventory_dir  # noqa: E402

FIGDIR = REPO / "notes" / "figures"


def logx_hist(ax, values, title, xlabel, bins=42, color="#2563eb"):
    """Histogram on a log-scaled x-axis with log-spaced bins. Non-positive
    values can't be placed on a log axis, so they're counted in the annotation
    rather than plotted. The median (over all values, including zeros) is drawn
    as a dashed line."""
    vals = [v for v in values if v is not None]
    if not vals:
        ax.set_title(f"{title}\n(no values)")
        return
    pos = [v for v in vals if v > 0]
    n_zero = len(vals) - len(pos)
    if not pos:
        ax.set_title(f"{title}\n(no positive values; {n_zero} zero)")
        return
    lo, hi = min(pos), max(pos)
    edges = np.logspace(np.log10(lo), np.log10(hi), bins) if hi > lo else bins
    ax.hist(pos, bins=edges, color=color, edgecolor="white", linewidth=0.4)
    ax.set_xscale("log")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel(f"{xlabel}  (log scale)")
    ax.set_ylabel("sessions")
    sv = sorted(vals)
    med = sv[len(sv) // 2]
    if med > 0:
        ax.axvline(med, color="#dc2626", linestyle="--", linewidth=1)
    note = f"n={len(vals)}  median={med:.1f}  max={max(vals):.0f}"
    if n_zero:
        note += f"\n{n_zero} zero-valued (not on log axis)"
    ax.text(
        0.03, 0.95, note, transform=ax.transAxes, ha="left", va="top",
        fontsize=8, bbox=dict(boxstyle="round", fc="#fff7ed", ec="#fdba74"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Step-1 inventory figures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("root", type=Path,
                        help="path to claudefiles trace directory")
    parser.add_argument(
        "--show-usernames", action="store_true",
        help="use real usernames in the per-user figure. Default is to "
             "anonymize as user01..userNN (sorted by session count, desc) "
             "so the committed figure is safe for a public repo before the "
             "consent filter is applied.",
    )
    args = parser.parse_args()
    root = args.root.expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    sessions = inventory_dir(root)
    if not sessions:
        sys.exit(f"no .jsonl files under {root}")
    main_s = [s for s in sessions if not s.is_subagent]
    n_sub = len(sessions) - len(main_s)
    if not main_s:
        sys.exit("no main sessions (is_subagent all True?)")

    FIGDIR.mkdir(parents=True, exist_ok=True)

    turns = [s.n_user_turns + s.n_assistant_turns for s in main_s]
    tool_calls = [s.n_tool_calls for s in main_s]
    duration = [s.duration_min for s in main_s]
    ttft = [s.time_to_first_tool_s for s in main_s]

    # ---- figure 1: 2x2 shape histograms ----
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    logx_hist(axes[0, 0], turns, "Turns per session", "user + assistant turns")
    logx_hist(axes[0, 1], tool_calls, "Tool calls per session", "tool calls",
              color="#0f766e")
    logx_hist(axes[1, 0], duration, "Duration per session", "minutes",
              color="#7c3aed")
    logx_hist(axes[1, 1], ttft, "Time to first tool call", "seconds",
              color="#c026d3")
    fig.suptitle(
        f"BERIL hackathon - session shape  ({len(main_s)} main sessions, "
        f"{n_sub} subagent traces excluded)",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    f1 = FIGDIR / "01_session_shape.png"
    fig.savefig(f1, dpi=130)
    plt.close(fig)

    # ---- figure 2: sessions per user ----
    per_user = Counter(s.user_dir for s in main_s)
    items = per_user.most_common()
    if args.show_usernames:
        labels = [u for u, _ in items]
        title_suffix = ""
    else:
        width = max(2, len(str(len(items))))
        labels = [f"user{i + 1:0{width}d}" for i in range(len(items))]
        title_suffix = "  (usernames anonymized)"
    # barh draws bottom-up, so reverse for largest-at-top
    names = labels[::-1]
    counts = [n for _, n in items][::-1]
    fig, ax = plt.subplots(figsize=(9, max(6, len(names) * 0.22)))
    ax.barh(names, counts, color="#2563eb", edgecolor="white", linewidth=0.3)
    ax.set_title(
        f"Sessions per user  ({len(names)} users, "
        f"{sum(counts)} main sessions){title_suffix}",
        fontsize=12, fontweight="bold",
    )
    ax.set_xlabel("main sessions")
    ax.tick_params(axis="y", labelsize=7)
    for i, c in enumerate(counts):
        ax.text(c + 0.5, i, str(c), va="center", fontsize=6)
    fig.tight_layout()
    f2 = FIGDIR / "02_sessions_per_user.png"
    fig.savefig(f2, dpi=130)
    plt.close(fig)

    # ---- figure 3: top tools (exact, full counts) ----
    all_tools: Counter = Counter()
    for s in main_s:
        all_tools.update(s.tools)
    top = all_tools.most_common(20)
    tnames = [t for t, _ in top][::-1]
    tcounts = [n for _, n in top][::-1]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(tnames, tcounts, color="#0f766e", edgecolor="white", linewidth=0.3)
    ax.set_title(
        f"Top 20 tools across {len(main_s)} main sessions  "
        f"({len(all_tools)} distinct tools, {sum(all_tools.values())} calls total)",
        fontsize=11, fontweight="bold",
    )
    ax.set_xlabel("calls")
    ax.tick_params(axis="y", labelsize=8)
    for i, c in enumerate(tcounts):
        ax.text(c + max(tcounts) * 0.005, i, str(c), va="center", fontsize=7)
    fig.tight_layout()
    f3 = FIGDIR / "03_top_tools.png"
    fig.savefig(f3, dpi=130)
    plt.close(fig)

    for f in (f1, f2, f3):
        print(f"wrote {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
