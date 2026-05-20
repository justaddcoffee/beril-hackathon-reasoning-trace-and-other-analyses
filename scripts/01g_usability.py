#!/usr/bin/env python3
"""Step 1g: usability signals.

Usage:
    python3 scripts/01g_usability.py data/claudefiles/

Looks at how smoothly sessions ran, not what they produced. The headline:
tool calls fail fairly often, but the failures are mostly recoverable - the
agent retries and succeeds - so the raw failure rate overstates the friction.

Signals (opt-in main sessions only):
  - tool failure rate per tool (tool_result.is_error, joined to the tool_use
    that produced it)
  - error-recovery rate: after a tool errors, did the NEXT call to the same
    tool in that session succeed?
  - sessions ending on an unresolved tool error
  - context-window resets ("continued from a previous conversation...")
  - Bash thrashing: the same command repeated >=3x in a row

Figures:
  12_tool_failure_vs_recovery.png   per-tool failure rate next to recovery rate
  13_usability_friction_overview.png  session-level friction prevalence

Caveats baked in from an independent review:
  - AskUserQuestion / ExitPlanMode is_error results are mostly USER rejections
    (not tool failures); AskUserQuestion also has genuine InputValidationError
    cases. They're reported separately, not mixed into the execution-tool
    failure story.
  - "Recovery" only tracks the next call to the SAME tool; a recovery via a
    different tool isn't counted, so the true recovery rate is a lower bound.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.consent import load_consenting_users  # noqa: E402
from src.inventory import is_history_path, is_subagent_path, user_dir_from_path  # noqa: E402

DEFAULT_CONSENT = REPO / "data" / "consent.csv"
FIGDIR = REPO / "notes" / "figures"

CONTEXT_RESET_RE = re.compile(
    r"This session is being continued from a previous conversation that ran out of context",
    re.IGNORECASE,
)
# Execution tools: is_error means a genuine failure. Interaction tools
# (AskUserQuestion / ExitPlanMode) are reported separately because their
# is_error is dominated by user rejection.
EXEC_TOOLS = ["Bash", "Read", "Write", "Edit", "NotebookEdit", "Glob", "Grep"]


def _norm(cmd: str) -> str:
    return re.sub(r"\s+", " ", cmd or "").strip()


def scan_session(path: Path) -> dict:
    rows = []
    with path.open() as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    id_to_tool: dict[str, str] = {}
    id_to_cmd: dict[str, str] = {}
    for obj in rows:
        msg = obj.get("message") or {}
        if (msg.get("role") or obj.get("type")) != "assistant":
            continue
        for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                tid = b.get("id", "")
                id_to_tool[tid] = b.get("name", "")
                if b.get("name") == "Bash":
                    id_to_cmd[tid] = (b.get("input", {}) or {}).get("command", "")

    results = []           # ordered (tool, is_error)
    n_context_resets = 0
    bash_call_cmds = []
    for obj in rows:
        msg = obj.get("message") or {}
        role = msg.get("role") or obj.get("type", "")
        content = msg.get("content")
        blocks = content if isinstance(content, list) else (
            [{"type": "text", "text": content}] if isinstance(content, str) else []
        )
        if role in ("user", "human"):
            for b in blocks:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and CONTEXT_RESET_RE.search(b.get("text", "")):
                    n_context_resets += 1
                if b.get("type") == "tool_result":
                    results.append((id_to_tool.get(b.get("tool_use_id", ""), ""),
                                    bool(b.get("is_error"))))
        elif role == "assistant":
            for b in blocks:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash":
                    bash_call_cmds.append(_norm((b.get("input", {}) or {}).get("command", "")))

    # thrashing: same normalized bash command >=3x consecutively
    thrash = False
    run = 1
    for a, b in zip(bash_call_cmds, bash_call_cmds[1:]):
        if a and a == b:
            run += 1
            if run >= 3:
                thrash = True
                break
        else:
            run = 1

    return {
        "user_dir": user_dir_from_path(path),
        "results": results,
        "n_context_resets": n_context_resets,
        "ends_on_error": bool(results) and results[-1][1],
        "has_tools": bool(results),
        "thrash": thrash,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", type=Path)
    p.add_argument("--consent", type=Path, default=DEFAULT_CONSENT)
    p.add_argument("--no-consent-filter", action="store_true")
    args = p.parse_args()
    root = args.root.expanduser()
    if not root.exists():
        sys.exit(f"not found: {root}")

    allowed = None if args.no_consent_filter else load_consenting_users(args.consent)

    sessions = []
    for path in sorted(root.rglob("*.jsonl")):
        if is_history_path(path) or is_subagent_path(path):
            continue
        if allowed is not None and user_dir_from_path(path) not in allowed:
            continue
        sessions.append(scan_session(path))
    if not sessions:
        sys.exit("no sessions after filtering")

    # ---- per-tool failure + recovery ----
    calls = Counter()
    errors = Counter()
    retry_attempts = Counter()
    retry_success = Counter()
    for s in sessions:
        res = s["results"]
        for tool, err in res:
            calls[tool] += 1
            if err:
                errors[tool] += 1
        # recovery: for each error, next result of same tool
        for i, (tool, err) in enumerate(res):
            if not err:
                continue
            for j in range(i + 1, len(res)):
                if res[j][0] == tool:
                    retry_attempts[tool] += 1
                    if not res[j][1]:
                        retry_success[tool] += 1
                    break

    n = len(sessions)
    end_on_error = sum(s["ends_on_error"] for s in sessions)
    with_tools = sum(s["has_tools"] for s in sessions)
    with_reset = sum(1 for s in sessions if s["n_context_resets"])
    thrash = sum(s["thrash"] for s in sessions)

    print(f"opt-in main sessions: {n}\n")
    print("=== per-tool failure + recovery (execution tools) ===")
    print(f"{'tool':12s} {'calls':>7} {'errs':>6} {'fail%':>7} {'recover%':>9}")
    for t in EXEC_TOOLS:
        c, e = calls.get(t, 0), errors.get(t, 0)
        if not c:
            continue
        a, sok = retry_attempts.get(t, 0), retry_success.get(t, 0)
        rec = sok / a if a else float("nan")
        print(f"{t:12s} {c:>7d} {e:>6d} {e/c:>6.1%} {rec:>8.0%}")
    print(f"\nsessions ending on unresolved error: {end_on_error}/{with_tools} "
          f"({end_on_error/with_tools:.0%} of sessions with tools)")
    print(f"sessions with a context reset:       {with_reset}/{n} ({with_reset/n:.0%})")
    print(f"sessions with Bash thrashing (>=3x):  {thrash}/{n} ({thrash/n:.0%})")

    FIGDIR.mkdir(parents=True, exist_ok=True)

    # ---- figure 12: failure vs recovery, execution tools ----
    # require enough calls to be meaningful AND at least one error (recovery
    # rate is undefined for a tool that never failed).
    tools = [t for t in EXEC_TOOLS if calls.get(t, 0) >= 20 and errors.get(t, 0) > 0]
    fail_rate = [errors.get(t, 0) / calls[t] for t in tools]
    rec_rate = [(retry_success.get(t, 0) / retry_attempts.get(t, 0))
                if retry_attempts.get(t, 0) else 0 for t in tools]
    y = np.arange(len(tools))
    h = 0.38
    fig, ax = plt.subplots(figsize=(10, max(4, len(tools) * 0.7)))
    ax.barh(y + h/2, fail_rate, height=h, color="#dc2626", label="failure rate")
    ax.barh(y - h/2, rec_rate, height=h, color="#0f766e", label="recovery rate (next same-tool call)")
    ax.set_yticks(y)
    ax.set_yticklabels(tools, fontsize=10)
    ax.set_xlim(0, 1.0)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    for i, (f, r) in enumerate(zip(fail_rate, rec_rate)):
        ax.text(f + 0.01, i + h/2, f"{f:.0%}", va="center", fontsize=8)
        ax.text(r + 0.01, i - h/2, f"{r:.0%}", va="center", fontsize=8)
    ax.set_title(
        f"Tool failures are common but mostly recoverable  "
        f"({n} opt-in sessions)\n"
        f"failure rate = is_error share; recovery = next same-tool call succeeded",
        fontsize=11, fontweight="bold",
    )
    ax.legend(loc="lower right", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f12 = FIGDIR / "12_tool_failure_vs_recovery.png"
    fig.savefig(f12, dpi=130)
    plt.close(fig)
    print(f"\nwrote {f12}")

    # ---- figure 13: session-level friction prevalence ----
    labels = [
        "any tool error",
        "context reset",
        "ended on error",
        "Bash thrashing",
    ]
    any_err = sum(1 for s in sessions if any(e for _, e in s["results"]))
    vals = [any_err / n, with_reset / n, end_on_error / n, thrash / n]
    labels, vals = labels[::-1], vals[::-1]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.barh(labels, vals, color="#7c3aed", edgecolor="white", linewidth=0.4)
    for i, v in enumerate(vals):
        ax.text(v + 0.005, i, f"{v:.0%}", va="center", fontsize=9)
    ax.set_xlim(0, max(vals) * 1.2)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_xlabel("share of opt-in sessions")
    ax.set_title(f"Session-level friction prevalence  ({n} opt-in sessions)",
                 fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    f13 = FIGDIR / "13_usability_friction_overview.png"
    fig.savefig(f13, dpi=130)
    plt.close(fig)
    print(f"wrote {f13}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
