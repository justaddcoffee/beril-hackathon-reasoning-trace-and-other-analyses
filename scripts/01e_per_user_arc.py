#!/usr/bin/env python3
"""Step 1e: per-user session arc (swim-lane figure).

Usage:
    python3 scripts/01e_per_user_arc.py data/claudefiles/

One row per opt-in user, anonymized as user01..userNN. Each session is a
point at its first_ts. Two figures:

  07_per_user_arc_typology.png        colored by first-prompt typology
                                      (slash_bootstrap / template_review /
                                      free_form / etc)
  08_per_user_arc_project.png         colored by project_slug for sessions
                                      using the "Review the project at
                                      projects/<slug>" template

The hackathon day is 2026-05-07. The window 2026-05-04..2026-05-09 covers
the hackathon plus a day of prep and a day of cleanup. A long tail of
sessions sits months before that - traces in pre-existing project dirs
with old timestamps. Those are counted in the subtitle but not plotted
(they'd compress the interesting window to a sliver). Sessions with no
parseable timestamp are also counted in the subtitle and dropped.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.consent import filter_sessions  # noqa: E402
from src.inventory import inventory_dir  # noqa: E402
from src.typology import CATEGORIES, first_prompt_of  # noqa: E402

DEFAULT_CONSENT = REPO / "data" / "consent.csv"
FIGDIR = REPO / "notes" / "figures"

# Hackathon window (UTC). The hackathon ran 2026-05-07; we widen by a day
# on either side. Anything outside this window is a pre-existing trace
# (different project dir, old timestamps) and gets dropped from the plot.
WINDOW_LO = datetime(2026, 5, 4, tzinfo=timezone.utc)
WINDOW_HI = datetime(2026, 5, 9, tzinfo=timezone.utc)

CAT_COLOR = {
    "slash_bootstrap": "#2563eb",
    "template_review": "#0f766e",
    "local_command":   "#94a3b8",
    "empty":           "#cbd5e1",
    "free_form":       "#c026d3",
}

# matplotlib tab10 / Dark2 hybrid; first 10 are distinct enough side-by-side.
# Top-N project slugs get these, everything else gets "other_color".
SLUG_PALETTE = [
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e",
    "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f",
]
OTHER_COLOR = "#d4dae3"


def _parse_ts(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _draw_lane_grid(ax, n_users):
    """Alternating grey stripes per user row for readability on dense days."""
    for i in range(n_users):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="#f6f7f9", zorder=0)


def _format_time_axis(ax):
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
    ax.tick_params(axis="x", which="minor", length=2)
    ax.set_xlim(WINDOW_LO, WINDOW_HI)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", type=Path, help="path to claudefiles trace directory")
    p.add_argument("--consent", type=Path, default=DEFAULT_CONSENT)
    p.add_argument("--no-consent-filter", action="store_true")
    p.add_argument("--show-usernames", action="store_true",
                   help="use real usernames instead of anonymized user01..userNN")
    args = p.parse_args()
    root = args.root.expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    sessions = inventory_dir(root)
    main_s = [s for s in sessions if not s.is_subagent]
    if not args.no_consent_filter:
        n_before = len(main_s)
        main_s = filter_sessions(main_s, args.consent, strict=False)
        if len(main_s) != n_before:
            print(f"consent filter: {len(main_s)}/{n_before} sessions kept "
                  f"({n_before - len(main_s)} dropped)")
    if not main_s:
        sys.exit("0 sessions left after filtering")

    # Classify each session's first prompt (for color).
    info_by_file = {s.file: first_prompt_of(Path(s.file)) for s in main_s}

    # User ordering: most active at top, anonymize unless --show-usernames.
    per_user = Counter(s.user_dir for s in main_s)
    user_order = [u for u, _ in per_user.most_common()]
    if args.show_usernames:
        labels = user_order
        title_suffix = ""
    else:
        width = max(2, len(str(len(user_order))))
        labels = [f"user{i + 1:0{width}d}" for i in range(len(user_order))]
        title_suffix = "  (usernames anonymized)"
    y_of = {u: i for i, u in enumerate(user_order)}

    # Bucket sessions by what we'll plot vs drop.
    plotted = []
    n_no_ts = 0
    n_outside_window = 0
    for s in main_s:
        ts = _parse_ts(s.first_ts)
        if ts is None:
            n_no_ts += 1
            continue
        if ts < WINDOW_LO or ts > WINDOW_HI:
            n_outside_window += 1
            continue
        plotted.append((s, ts))

    if not plotted:
        sys.exit("no sessions inside the plot window; check WINDOW_LO/HI")

    n_users_with_data = len({s.user_dir for s, _ in plotted})
    subtitle = (
        f"{len(plotted)} sessions across {n_users_with_data} users  |  "
        f"{n_outside_window} pre-hackathon sessions not shown  |  "
        f"{n_no_ts} with no parseable timestamp"
    )

    FIGDIR.mkdir(parents=True, exist_ok=True)

    # ----- figure 7: colored by typology -----
    fig, ax = plt.subplots(figsize=(13, max(5, len(user_order) * 0.28)))
    _draw_lane_grid(ax, len(user_order))
    by_cat: dict[str, list] = {c: ([], []) for c in CATEGORIES}
    for s, ts in plotted:
        info = info_by_file[s.file]
        xs_ys = by_cat[info.category]
        xs_ys[0].append(ts)
        xs_ys[1].append(y_of[s.user_dir])
    for c in CATEGORIES:
        xs, ys = by_cat[c]
        if not xs:
            continue
        ax.scatter(xs, ys, s=42, color=CAT_COLOR[c], label=c,
                   edgecolors="white", linewidth=0.5, alpha=0.92, zorder=3)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()                              # user01 (most active) at top
    ax.set_ylim(len(labels) - 0.5, -0.5)
    _format_time_axis(ax)
    ax.set_title(
        f"BERIL hackathon - per-user session arc, colored by first-prompt typology"
        f"{title_suffix}\n{subtitle}",
        fontsize=11, fontweight="bold",
    )
    ax.legend(loc="lower right", framealpha=0.95, fontsize=8, ncols=5,
              bbox_to_anchor=(1.0, -0.13))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f7 = FIGDIR / "07_per_user_arc_typology.png"
    fig.savefig(f7, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {f7}")

    # ----- figure 8: colored by project slug -----
    # Pick the top-N slugs to give distinct colors; the rest get OTHER_COLOR.
    slug_counts = Counter(
        info_by_file[s.file].project_slug
        for s, _ in plotted
        if info_by_file[s.file].project_slug
    )
    TOP_N = min(len(SLUG_PALETTE), len(slug_counts))
    top_slugs = [sl for sl, _ in slug_counts.most_common(TOP_N)]
    slug_color = {sl: SLUG_PALETTE[i] for i, sl in enumerate(top_slugs)}

    fig, ax = plt.subplots(figsize=(13, max(5, len(user_order) * 0.28)))
    _draw_lane_grid(ax, len(user_order))

    # Plot "no slug" (slash_bootstrap, empty, free_form, etc) as a thin grey
    # dot so the arc-of-activity is still visible, then overlay slugged
    # sessions on top with strong colors.
    grey_xs, grey_ys = [], []
    by_slug: dict[str, list] = {sl: ([], []) for sl in top_slugs}
    other_xs, other_ys = [], []
    for s, ts in plotted:
        sl = info_by_file[s.file].project_slug
        if not sl:
            grey_xs.append(ts)
            grey_ys.append(y_of[s.user_dir])
        elif sl in slug_color:
            by_slug[sl][0].append(ts)
            by_slug[sl][1].append(y_of[s.user_dir])
        else:
            other_xs.append(ts)
            other_ys.append(y_of[s.user_dir])
    if grey_xs:
        ax.scatter(grey_xs, grey_ys, s=18, color="#e1e5ea",
                   edgecolors="none", zorder=2,
                   label=f"no project slug  ({len(grey_xs)})")
    for sl in top_slugs:
        xs, ys = by_slug[sl]
        ax.scatter(xs, ys, s=48, color=slug_color[sl],
                   edgecolors="white", linewidth=0.5, zorder=3,
                   label=f"{sl}  ({len(xs)})")
    if other_xs:
        ax.scatter(other_xs, other_ys, s=42, color=OTHER_COLOR,
                   edgecolors="white", linewidth=0.4, zorder=3,
                   label=f"other slugs  ({len(other_xs)})")

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_ylim(len(labels) - 0.5, -0.5)
    _format_time_axis(ax)
    ax.set_title(
        f"BERIL hackathon - per-user session arc, colored by project slug"
        f"{title_suffix}\n{subtitle}",
        fontsize=11, fontweight="bold",
    )
    ax.legend(loc="upper left", framealpha=0.95, fontsize=7, ncols=2,
              bbox_to_anchor=(1.005, 1.0))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f8 = FIGDIR / "08_per_user_arc_project.png"
    fig.savefig(f8, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {f8}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
