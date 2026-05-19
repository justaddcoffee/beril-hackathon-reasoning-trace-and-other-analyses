"""Step-2 outcome triage. For each session, extract signals that help a human
decide: did this user end up with `nothing`, a `partial`, or `something real`
by the end of the hackathon?

We don't try to auto-label. Auto-labeling "did they write a paper" from traces
is unreliable. Instead: extract enough context per session that a human
can scan a CSV and assign labels in ~30 sec/session.

Per session we collect:
    files_written          - list of (path, n_writes) pairs from Edit/Write/MultiEdit/NotebookEdit
    n_files_written        - distinct files touched by write tools
    total_write_chars      - sum of new_string / content lengths across all writes
    last_assistant_text    - the last assistant text block, truncated
    last_user_text         - the last human user turn, truncated
    has_manuscript_like    - True if any written path matches /paper|manuscript|draft|abstract|main\\.(md|tex|ipynb)/i
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

from src.inventory import is_history_path, is_subagent_path, user_dir_from_path


WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
MANUSCRIPT_RE = re.compile(
    r"(paper|manuscript|draft|abstract|main|writeup|results)\.(md|tex|ipynb|docx|rmd|qmd)$",
    re.IGNORECASE,
)


@dataclass
class SessionOutcome:
    file: str
    session_id: str = ""
    user_dir: str = ""
    is_subagent: bool = False
    files_written: Counter = field(default_factory=Counter)
    n_files_written: int = 0
    total_write_chars: int = 0
    last_assistant_text: str = ""
    last_user_text: str = ""
    has_manuscript_like: bool = False


def _content_blocks(msg: dict) -> list[dict]:
    content = msg.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def _oneline(s: str, limit: int = 500) -> str:
    """Collapse all whitespace (incl. newlines) to single spaces, then truncate.

    The last_user/last_assistant snippets are frequently multi-line markdown.
    Left as-is they embed newlines inside quoted CSV fields - still valid CSV,
    but the file shows as a wall of markdown in any viewer that doesn't parse
    quoting. Flattening keeps the triage CSV to one physical line per row so
    it stays scannable. Collapse happens before truncation so the limit counts
    real content, not whitespace.
    """
    return " ".join((s or "").split())[:limit]


def _write_chars(tool_name: str, tool_input: dict) -> int:
    """Approximate count of characters written by this tool call."""
    if not isinstance(tool_input, dict):
        return 0
    if tool_name == "Write":
        return len(tool_input.get("content", "") or "")
    if tool_name == "Edit":
        return len(tool_input.get("new_string", "") or "")
    if tool_name == "MultiEdit":
        edits = tool_input.get("edits", []) or []
        return sum(len((e or {}).get("new_string", "") or "") for e in edits if isinstance(e, dict))
    if tool_name == "NotebookEdit":
        return len(tool_input.get("new_source", "") or "")
    return 0


def _path_of(tool_name: str, tool_input: dict) -> str | None:
    if not isinstance(tool_input, dict):
        return None
    return (
        tool_input.get("file_path")
        or tool_input.get("notebook_path")
        or tool_input.get("path")
    )


def outcome_for_session(path: Path) -> SessionOutcome:
    o = SessionOutcome(file=str(path))
    last_user = ""
    last_assistant = ""

    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not o.session_id:
                o.session_id = obj.get("sessionId", "") or obj.get("session_id", "")

            msg = obj.get("message") or {}
            role = msg.get("role") or obj.get("type", "")
            blocks = _content_blocks(msg) if msg else []

            if role in ("user", "human"):
                non_tool_result = [b for b in blocks if b.get("type") != "tool_result"]
                if isinstance(msg.get("content"), str) or non_tool_result:
                    text = " ".join(
                        b.get("text", "") for b in non_tool_result if b.get("type") == "text"
                    ).strip()
                    if isinstance(msg.get("content"), str):
                        text = msg["content"].strip()
                    if text:
                        last_user = text
            elif role == "assistant":
                for b in blocks:
                    if b.get("type") == "text":
                        text = (b.get("text") or "").strip()
                        if text:
                            last_assistant = text
                    elif b.get("type") == "tool_use":
                        name = b.get("name", "")
                        if name in WRITE_TOOLS:
                            tin = b.get("input", {}) or {}
                            p = _path_of(name, tin)
                            if p:
                                o.files_written[p] += 1
                                if MANUSCRIPT_RE.search(p):
                                    o.has_manuscript_like = True
                            o.total_write_chars += _write_chars(name, tin)

    o.n_files_written = len(o.files_written)
    o.last_user_text = _oneline(last_user)
    o.last_assistant_text = _oneline(last_assistant)
    o.user_dir = user_dir_from_path(path)
    o.is_subagent = is_subagent_path(path)
    return o


def outcomes_dir(root: Path | str, glob: str = "**/*.jsonl",
                 include_history: bool = False) -> list[SessionOutcome]:
    """Walk a trace tree and return one SessionOutcome per .jsonl. By default
    history.jsonl files are skipped (see src/inventory.is_history_path)."""
    root = Path(root)
    paths = sorted(Path(root).glob(glob))
    if not include_history:
        paths = [p for p in paths if not is_history_path(p)]
    return [outcome_for_session(p) for p in paths]


def to_records(outcomes: Iterable[SessionOutcome]) -> list[dict]:
    """Flatten for the human-triage CSV. Adds an empty `label` column."""
    rows = []
    for o in outcomes:
        d = asdict(o)
        files = d.pop("files_written") or {}
        d["files_written_top10"] = "; ".join(
            f"{p} (x{n})" for p, n in sorted(files.items(), key=lambda x: -x[1])[:10]
        )
        # Empty column for the human to fill in
        d["label"] = ""
        rows.append(d)
    return rows
