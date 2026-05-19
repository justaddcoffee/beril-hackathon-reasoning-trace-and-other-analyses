"""Step-1 inventory of Claude Code session traces.

Walks a directory of .jsonl session files (the format Claude Code writes to
~/.claude/projects/.../*.jsonl) and emits one row per session with:

    file, session_id, user_dir, n_lines, n_user_turns, n_assistant_turns,
    n_tool_calls, n_tool_results, tools (Counter), first_ts, last_ts,
    duration_min, time_to_first_tool_s, n_text_chars_user, n_text_chars_assistant

The parser is intentionally forgiving: malformed lines, missing keys, and
unexpected content shapes are counted in `n_skipped_lines` rather than crashing.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class SessionStats:
    file: str
    session_id: str = ""
    user_dir: str = ""
    cwd: str = ""
    is_subagent: bool = False
    n_lines: int = 0
    n_skipped_lines: int = 0
    n_user_turns: int = 0          # human-typed turns (content is str OR has any non-tool_result block)
    n_assistant_turns: int = 0
    n_tool_calls: int = 0
    n_tool_results: int = 0
    tools: Counter = field(default_factory=Counter)
    first_ts: str = ""
    last_ts: str = ""
    duration_min: float = 0.0
    time_to_first_tool_s: float | None = None
    n_text_chars_user: int = 0
    n_text_chars_assistant: int = 0


def _parse_ts(s) -> datetime | None:
    """Parse a trace timestamp. Accepts ISO-8601 strings (Claude Code's usual
    format) and numeric epoch values (seconds or milliseconds), which some
    lines in the hackathon archive use instead."""
    if s is None or s == "":
        return None
    if isinstance(s, bool):
        return None
    if isinstance(s, (int, float)):
        try:
            val = float(s)
        except (ValueError, TypeError):
            return None
        if val > 1e11:  # milliseconds since epoch
            val /= 1000.0
        try:
            return datetime.fromtimestamp(val, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    if not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _content_blocks(msg: dict) -> list[dict]:
    """Normalize message.content to a list of blocks. A bare string becomes one text block."""
    content = msg.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def user_dir_from_path(path: Path) -> str:
    """Extract the participant's user_dir from a trace path.

    The hackathon archive nests traces as
        .../claude-_files/<username>/.claude/projects/<encoded-cwd>/<session>.jsonl
    so the username is the path component right after the "claude-_files"
    anchor. Falls back to the immediate parent dir name (Claude Code's
    default layout, where parent == <encoded-cwd>) if the anchor isn't
    present. Used as the join key against consent.csv.
    """
    parts = path.parts
    for anchor in ("claude-_files", "claudefiles", "claude_files"):
        if anchor in parts:
            i = parts.index(anchor)
            if i + 1 < len(parts):
                return parts[i + 1]
            break
    return path.parent.name


def is_subagent_path(path: Path) -> bool:
    """Subagent traces live at .../<session-uuid>/subagents/agent-*.jsonl and
    are not standalone sessions."""
    return "subagents" in path.parts or path.name.startswith("agent-")


def inventory_session(path: Path) -> SessionStats:
    s = SessionStats(file=str(path))
    first_user_ts: datetime | None = None
    first_tool_ts: datetime | None = None
    timestamps: list[datetime] = []

    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            s.n_lines += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                s.n_skipped_lines += 1
                continue

            # Pick up session-level metadata if present
            if not s.session_id:
                s.session_id = obj.get("sessionId", "") or obj.get("session_id", "")
            if not s.cwd:
                s.cwd = obj.get("cwd", "") or obj.get("workingDirectory", "")

            ts = _parse_ts(obj.get("timestamp", ""))
            if ts:
                timestamps.append(ts)

            msg = obj.get("message") or {}
            role = msg.get("role") or obj.get("type", "")
            blocks = _content_blocks(msg) if msg else []

            if role in ("user", "human"):
                # Distinguish a real human turn from a synthetic tool_result wrapper
                non_tool_result = [b for b in blocks if b.get("type") != "tool_result"]
                tool_results = [b for b in blocks if b.get("type") == "tool_result"]
                s.n_tool_results += len(tool_results)
                if isinstance(msg.get("content"), str) or non_tool_result:
                    s.n_user_turns += 1
                    if first_user_ts is None and ts:
                        first_user_ts = ts
                    for b in non_tool_result:
                        if b.get("type") == "text":
                            s.n_text_chars_user += len(b.get("text", "") or "")
            elif role == "assistant":
                s.n_assistant_turns += 1
                for b in blocks:
                    btype = b.get("type")
                    if btype == "text":
                        s.n_text_chars_assistant += len(b.get("text", "") or "")
                    elif btype == "tool_use":
                        s.n_tool_calls += 1
                        s.tools[b.get("name", "<unknown>")] += 1
                        if first_tool_ts is None and ts:
                            first_tool_ts = ts

    if timestamps:
        s.first_ts = min(timestamps).isoformat()
        s.last_ts = max(timestamps).isoformat()
        s.duration_min = (max(timestamps) - min(timestamps)).total_seconds() / 60.0
    if first_user_ts and first_tool_ts:
        s.time_to_first_tool_s = (first_tool_ts - first_user_ts).total_seconds()

    s.user_dir = user_dir_from_path(path)
    s.is_subagent = is_subagent_path(path)
    return s


def inventory_dir(root: Path | str, glob: str = "**/*.jsonl") -> list[SessionStats]:
    root = Path(root)
    return [inventory_session(p) for p in sorted(root.glob(glob))]


def to_records(sessions: Iterable[SessionStats]) -> list[dict]:
    """Flatten for pandas / CSV. Top tools collapsed into a single column."""
    rows = []
    for s in sessions:
        d = asdict(s)
        # asdict turns Counter into dict; collapse for tabular display
        tools_dict = d.pop("tools") or {}
        d["tools_top5"] = ", ".join(
            f"{name}:{n}" for name, n in sorted(tools_dict.items(), key=lambda x: -x[1])[:5]
        )
        d["tools_total_distinct"] = len(tools_dict)
        rows.append(d)
    return rows
