#!/usr/bin/env python3
"""Step 1f: characterize subagent activity in opt-in sessions.

Usage:
    python3 scripts/01f_subagent_characterization.py data/claudefiles/

The earlier analyses excluded subagent traces (.../<parent-uuid>/subagents/
agent-*.jsonl), counting only the user-initiated "main" sessions. That hid
a lot of agent activity: the main agent delegates work to subagents via
the Task tool, and those subagents do their own Bash / Read / Edit runs.
"Bash 6213 calls" in main-only undercounts what really happened.

This pass joins each subagent trace back to its parent main session via
the path layout, restricts to opt-in users, and reports:

  09_subagent_spawn_per_session.png   How many subagents each main session
                                      spawned (heavy-tail distribution).
  10_subagent_vs_main_tools.png       Top tools, side-by-side: where the
                                      activity actually happens.
  11_subagent_types.png               Which subagent_type (Explore /
                                      general-purpose / Plan / etc.) the
                                      main agent picked.

Subagent_type counts come from a separate pass that greps `subagent_type`
out of `Task` tool_use blocks in MAIN session JSONLs (the type isn't
recorded inside the subagent's own trace). The Task-call count and the
subagent-file count are not 1:1 - a single Task call can produce multiple
trace files - so they're reported as independent stats rather than joined.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.consent import load_consenting_users  # noqa: E402
from src.inventory import (  # noqa: E402
    inventory_session, is_history_path, is_subagent_path,
    parent_session_id_from_subagent_path, user_dir_from_path,
)

DEFAULT_CONSENT = REPO / "data" / "consent.csv"
FIGDIR = REPO / "notes" / "figures"

# subagent_type appears in Task tool_use blocks inside main session JSONLs.
SUBAGENT_TYPE_RE = re.compile(r'"subagent_type"\s*:\s*"([^"]+)"')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", type=Path, help="path to claudefiles trace directory")
    p.add_argument("--consent", type=Path, default=DEFAULT_CONSENT)
    p.add_argument("--no-consent-filter", action="store_true")
    args = p.parse_args()
    root = args.root.expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    if not args.no_consent_filter:
        allowed = load_consenting_users(args.consent)
    else:
        allowed = None  # accept all

    # Walk every JSONL once. Bucket into main / subagent / skipped.
    main_by_session: dict[str, dict] = {}      # parent session_id -> {tools, n_tool_calls, file, user_dir}
    main_by_file: dict[str, dict] = {}         # parent file -> main_by_session value (for outcome join)
    subagent_records: list[dict] = []           # one per subagent file we kept
    skipped_history = 0
    n_main_total = 0
    n_subagent_total = 0
    n_dropped_consent = 0

    for path in sorted(root.glob("**/*.jsonl")):
        if is_history_path(path):
            skipped_history += 1
            continue
        user_dir = user_dir_from_path(path)
        if allowed is not None and user_dir not in allowed:
            n_dropped_consent += 1
            continue
        s = inventory_session(path)
        if is_subagent_path(path):
            n_subagent_total += 1
            parent_id = parent_session_id_from_subagent_path(path)
            subagent_records.append({
                "file": str(path),
                "user_dir": user_dir,
                "parent_session_id": parent_id,
                "n_tool_calls": s.n_tool_calls,
                "tools": s.tools,
            })
        else:
            n_main_total += 1
            sid = s.session_id or path.stem
            main_by_session[sid] = {
                "file": str(path),
                "user_dir": user_dir,
                "session_id": sid,
                "n_tool_calls": s.n_tool_calls,
                "tools": s.tools,
            }
            main_by_file[str(path)] = main_by_session[sid]

    # ---- subagent_type counts: re-scan MAIN session jsonls for Task tool_use blocks ----
    type_counts: Counter = Counter()
    for m in main_by_session.values():
        try:
            with open(m["file"], encoding="utf-8") as fh:
                txt = fh.read()
        except OSError:
            continue
        for match in SUBAGENT_TYPE_RE.findall(txt):
            type_counts[match] += 1

    # ---- per-main-session spawn count ----
    spawns_per_session: Counter = Counter()
    for sub in subagent_records:
        spawns_per_session[sub["parent_session_id"]] += 1
    # main sessions that spawned zero subagents need explicit zero entries
    spawn_dist: list[int] = []
    for sid in main_by_session:
        spawn_dist.append(spawns_per_session.get(sid, 0))

    # ---- aggregate tool counts ----
    main_tools: Counter = Counter()
    for m in main_by_session.values():
        main_tools.update(m["tools"])
    subagent_tools: Counter = Counter()
    for sub in subagent_records:
        subagent_tools.update(sub["tools"])

    print(f"opt-in main sessions:          {len(main_by_session)}")
    print(f"opt-in subagent traces:        {len(subagent_records)}")
    print(f"history.jsonl files skipped:   {skipped_history}")
    print(f"files dropped by consent:      {n_dropped_consent}")
    print()
    print(f"subagent tool calls (total):   {sum(subagent_tools.values())}")
    print(f"main tool calls (total):       {sum(main_tools.values())}")
    print(f"subagent share of all tools:   "
          f"{sum(subagent_tools.values())/(sum(subagent_tools.values())+sum(main_tools.values())):.0%}")
    print()
    print("spawns per main session:")
    spawn_hist = Counter(spawn_dist)
    n_with_subagents = sum(1 for v in spawn_dist if v > 0)
    print(f"  {n_with_subagents}/{len(spawn_dist)} main sessions spawned >=1 subagent  "
          f"({n_with_subagents/len(spawn_dist):.0%})")
    print(f"  max spawns: {max(spawn_dist) if spawn_dist else 0}")
    print(f"  median (non-zero only): "
          f"{int(np.median([v for v in spawn_dist if v > 0])) if n_with_subagents else 0}")
    print()
    print("subagent_type frequency (from Task calls in main sessions):")
    for t, n in type_counts.most_common():
        print(f"  {n:5d}  {t}")

    # ---- figure 9: spawns per session ----
    FIGDIR.mkdir(parents=True, exist_ok=True)
    nonzero = [v for v in spawn_dist if v > 0]
    if not nonzero:
        nonzero = [0]
    fig, ax = plt.subplots(figsize=(10, 5))
    edges = np.logspace(0, np.log10(max(nonzero) + 1), 30) if max(nonzero) > 1 else 20
    ax.hist(nonzero, bins=edges, color="#0f766e", edgecolor="white", linewidth=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("subagents spawned (log scale)")
    ax.set_ylabel("main sessions")
    n_zero = sum(1 for v in spawn_dist if v == 0)
    ax.set_title(
        f"Subagents spawned per main session  "
        f"({n_with_subagents} of {len(spawn_dist)} opt-in sessions "
        f"spawned >=1; {n_zero} spawned none)",
        fontsize=11, fontweight="bold",
    )
    med = int(np.median(nonzero)) if nonzero else 0
    if med > 0:
        ax.axvline(med, color="#dc2626", linestyle="--", linewidth=1)
        ax.text(0.97, 0.95, f"median (non-zero) = {med}\nmax = {max(nonzero)}",
                transform=ax.transAxes, ha="right", va="top", fontsize=9,
                bbox=dict(boxstyle="round", fc="#fff7ed", ec="#fdba74"))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f9 = FIGDIR / "09_subagent_spawn_per_session.png"
    fig.savefig(f9, dpi=130)
    plt.close(fig)
    print(f"\nwrote {f9}")

    # ---- figure 10: side-by-side main vs subagent tool counts ----
    union = Counter()
    union.update(main_tools)
    union.update(subagent_tools)
    top = [t for t, _ in union.most_common(15)]
    main_vals = [main_tools.get(t, 0) for t in top]
    sub_vals = [subagent_tools.get(t, 0) for t in top]
    # display largest at top
    top, main_vals, sub_vals = top[::-1], main_vals[::-1], sub_vals[::-1]
    y = np.arange(len(top))
    h = 0.4
    fig, ax = plt.subplots(figsize=(11, max(5, len(top) * 0.36)))
    ax.barh(y - h/2, main_vals, height=h, color="#2563eb",
            label="main sessions", edgecolor="white", linewidth=0.4)
    ax.barh(y + h/2, sub_vals, height=h, color="#0f766e",
            label="subagent traces", edgecolor="white", linewidth=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(top, fontsize=9)
    ax.set_xlabel("tool calls")
    max_v = max(max(main_vals or [0]), max(sub_vals or [0]))
    for i, (m, s) in enumerate(zip(main_vals, sub_vals)):
        if m:
            ax.text(m + max_v * 0.005, i - h/2, str(m), va="center", fontsize=7)
        if s:
            ax.text(s + max_v * 0.005, i + h/2, str(s), va="center", fontsize=7)
    total_main, total_sub = sum(main_tools.values()), sum(subagent_tools.values())
    ax.set_title(
        f"Top tools: main sessions vs subagent traces  "
        f"(main {total_main} calls, subagents {total_sub} calls, "
        f"subagents = {total_sub/(total_main+total_sub):.0%} of total)",
        fontsize=11, fontweight="bold",
    )
    ax.legend(loc="lower right", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f10 = FIGDIR / "10_subagent_vs_main_tools.png"
    fig.savefig(f10, dpi=130)
    plt.close(fig)
    print(f"wrote {f10}")

    # ---- figure 11: subagent_type frequency ----
    if type_counts:
        items = type_counts.most_common()
        labels = [t for t, _ in items][::-1]
        counts = [n for _, n in items][::-1]
        fig, ax = plt.subplots(figsize=(9, max(3, len(labels) * 0.5)))
        ax.barh(labels, counts, color="#7c3aed", edgecolor="white", linewidth=0.4)
        for i, n in enumerate(counts):
            ax.text(n + max(counts) * 0.008, i,
                    f"{n}  ({n/sum(counts):.0%})", va="center", fontsize=9)
        ax.set_xlim(0, max(counts) * 1.18)
        ax.set_xlabel("Task tool_use calls in main sessions")
        ax.set_title(
            f"Subagent types invoked from main sessions  "
            f"({sum(counts)} Task calls across "
            f"{len(main_by_session)} opt-in main sessions)",
            fontsize=11, fontweight="bold",
        )
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        f11 = FIGDIR / "11_subagent_types.png"
        fig.savefig(f11, dpi=130)
        plt.close(fig)
        print(f"wrote {f11}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
