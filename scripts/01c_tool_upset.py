#!/usr/bin/env python3
"""Step 1c: UpSet plot of tool co-occurrence per session.

Usage:
    python scripts/01c_tool_upset.py data/claudefiles/

For each MAIN session, the set of distinct tools it used is its "signature".
This plots, UpSet-style, which tool combinations co-occur across sessions:
  - top bars   = number of sessions with each exact tool combination
  - left bars  = number of sessions that used each tool at all (set size)
  - dot matrix = which tools make up each combination

Restricted to the TOP_K tools by session frequency - an UpSet over all ~47
distinct tools is unreadable. Sessions with 0 tool calls, and sessions that
used only long-tail tools outside the top K, are counted in the subtitle
rather than plotted (their restricted signature is empty).

Built directly on matplotlib (no upsetplot/pandas dependency) to stay
consistent with the other scripts in this repo.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.inventory import inventory_dir  # noqa: E402

FIGDIR = REPO / "notes" / "figures"
TOP_K = 12               # tools shown as matrix rows
TOP_N_INTERSECTIONS = 30  # tool combinations shown as columns


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1]).expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    sessions = inventory_dir(root)
    main_s = [s for s in sessions if not s.is_subagent]
    if not main_s:
        sys.exit("no main sessions")

    # one signature per session: the set of distinct tools it used
    sigs_all = [set(s.tools) for s in main_s]
    n_no_tools = sum(1 for sg in sigs_all if not sg)

    # pick the TOP_K tools by how many sessions use them
    tool_sessions: Counter = Counter()
    for sg in sigs_all:
        tool_sessions.update(sg)
    top_tools = [t for t, _ in tool_sessions.most_common(TOP_K)]
    top_set = set(top_tools)

    # restrict each signature to the top-K tools
    restricted = [frozenset(sg & top_set) for sg in sigs_all]
    n_only_longtail = sum(
        1 for sg, r in zip(sigs_all, restricted) if sg and not r
    )
    nonempty = [r for r in restricted if r]
    inter_counts = Counter(nonempty)
    top_inter = inter_counts.most_common(TOP_N_INTERSECTIONS)

    # order matrix rows by set size, largest at top
    top_tools = sorted(top_tools, key=lambda t: -tool_sessions[t])
    set_sizes = [tool_sessions[t] for t in top_tools]
    sigs = [s for s, _ in top_inter]
    sizes = [c for _, c in top_inter]
    N, K = len(sigs), len(top_tools)
    xs, ys = np.arange(N), np.arange(K)

    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(15, 9))
    gs = GridSpec(
        2, 2, width_ratios=[1, 4.6], height_ratios=[2.2, 3],
        hspace=0.07, wspace=0.04,
    )
    ax_int = fig.add_subplot(gs[0, 1])
    ax_matrix = fig.add_subplot(gs[1, 1], sharex=ax_int)
    ax_set = fig.add_subplot(gs[1, 0], sharey=ax_matrix)

    # ---- top: intersection sizes ----
    ax_int.bar(xs, sizes, width=0.62, color="#2563eb")
    for x, c in zip(xs, sizes):
        ax_int.text(x, c + max(sizes) * 0.012, str(c), ha="center",
                    va="bottom", fontsize=7)
    ax_int.set_ylabel("sessions with this\ntool combination", fontsize=10)
    ax_int.set_ylim(0, max(sizes) * 1.16)
    ax_int.spines[["top", "right"]].set_visible(False)
    ax_int.tick_params(labelbottom=False, bottom=False)

    # ---- bottom-left: set sizes ----
    ax_set.barh(ys, set_sizes, height=0.62, color="#0f766e")
    # headroom past the longest bar so the count labels clear the tool names
    ax_set.set_xlim(max(set_sizes) * 1.32, 0)
    ax_set.set_xlabel("sessions using\ntool (set size)", fontsize=10)
    ax_set.spines[["top", "left"]].set_visible(False)
    for y, c in zip(ys, set_sizes):
        ax_set.text(c + max(set_sizes) * 0.035, y, str(c), ha="right",
                    va="center", fontsize=7)

    # ---- bottom-right: dot matrix ----
    for i in range(K):
        if i % 2 == 0:
            ax_matrix.axhspan(i - 0.5, i + 0.5, color="#f1f3f7", zorder=0)
    for j, sig in enumerate(sigs):
        members = [i for i, t in enumerate(top_tools) if t in sig]
        ax_matrix.scatter([j] * K, ys, s=58, color="#d4dae3", zorder=2)
        if members:
            ax_matrix.scatter([j] * len(members), members, s=58,
                              color="#172033", zorder=3)
            ax_matrix.plot([j, j], [min(members), max(members)],
                           color="#172033", lw=1.6, zorder=2)
    ax_matrix.set_ylim(K - 0.5, -0.5)
    ax_matrix.set_xlim(-0.5, N - 0.5)
    ax_matrix.tick_params(labelbottom=False, bottom=False,
                          labelleft=False, left=False)
    ax_matrix.set_xlabel(
        f"tool combinations, ranked by session count (top {N} of "
        f"{len(inter_counts)} distinct combinations)", fontsize=10,
    )
    for sp in ax_matrix.spines.values():
        sp.set_visible(False)

    # y tick labels live on the shared axis; set them last so nothing clears
    # them. The matrix hides its own copy via tick_params(labelleft=False).
    ax_set.set_yticks(ys)
    ax_set.set_yticklabels(top_tools, fontsize=9)

    plotted = sum(sizes)
    fig.suptitle(
        "BERIL hackathon - tool co-occurrence per session (UpSet)",
        fontsize=14, fontweight="bold", y=0.97,
    )
    fig.text(
        0.5, 0.925,
        f"{len(main_s)} main sessions  |  matrix restricted to top {K} tools  |  "
        f"{plotted} sessions in the {N} combinations shown  |  "
        f"excluded: {n_no_tools} used no tools, "
        f"{n_only_longtail} used only tools outside the top {K}",
        ha="center", fontsize=9, color="#475569",
    )
    fig.savefig(FIGDIR / "04_tool_upset.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {FIGDIR / '04_tool_upset.png'}")
    print(f"  {len(main_s)} main sessions; {n_no_tools} used no tools; "
          f"{n_only_longtail} used only long-tail tools")
    print(f"  {len(inter_counts)} distinct tool combinations over the top "
          f"{K} tools; showing top {N}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
