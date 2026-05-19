"""First-prompt typology.

A sampling pass showed almost every BERIL session opens with one of three
canned starts, not a free-form prompt:

  1. The `/berdl_start` slash command (environment bootstrap that runs a
     hackathon-provided init script).
  2. A standardized "Review the project at projects/<slug>/..." preamble
     that participants pasted in. This carries a project slug we can lift
     out as a per-session topic tag.
  3. An empty or `<local-command-caveat>`-wrapped message - artifacts of
     Claude Code's local command system, not human authoring.

Only a small minority of sessions begin with a genuinely free-form prompt.
That itself is the finding: participants didn't really prompt - they kicked
off a templated harness and Claude rode it from there. The interesting
variation in agent behavior lives in turns 2+, not in turn 1.

This module classifies each session's *first* user message into a small
typology and pulls out the project slug when the template form is used.
Rule-based and transparent on purpose - both so the typology is debuggable
without re-running a model, and so a future reader can see the exact
patterns that defined each bucket.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

# ---- patterns ----------------------------------------------------------

# Claude Code slash commands appear in the trace as
#   <command-name>/berdl_start</command-name> ...
# or as plain text like "berdl start" / "beril start" if typed without the
# slash. Match all of those.
SLASH_RE = re.compile(
    r"<command-name>\s*/?\s*(berdl|beril)[a-z_]*\s*</command-name>"
    r"|^\s*/?\s*(berdl|beril)[ _]start\b",
    re.IGNORECASE,
)

# The hackathon's "Review the project" template. Captures the slug for use
# as a topic tag.
REVIEW_RE = re.compile(
    r"^\s*Review the (?:project|research plan) at projects/([A-Za-z0-9_\-]+)/?",
    re.IGNORECASE,
)

LOCAL_CMD_RE = re.compile(r"<local-command-caveat>", re.IGNORECASE)


@dataclass
class FirstPromptInfo:
    file: str
    session_id: str = ""
    category: str = ""          # one of CATEGORIES, see classify()
    project_slug: str = ""      # set when category == "template_review"
    first_prompt: str = ""      # oneline'd, truncated for the CSV
    n_chars: int = 0            # before truncation; lets us see "blank" vs "short"


CATEGORIES = (
    "slash_bootstrap",      # /berdl_start, /beril, "berdl start"
    "template_review",      # "Review the project at projects/<slug>/..."
    "local_command",        # <local-command-caveat> wrapper, no human text
    "empty",                # message exists but text is blank after stripping
    "free_form",            # anything else - the genuinely-authored prompts
)


def _oneline(s: str, limit: int = 240) -> str:
    return " ".join((s or "").split())[:limit]


def classify(text: str) -> tuple[str, str]:
    """Return (category, project_slug). slug is "" unless category is template_review."""
    if not text or not text.strip():
        return "empty", ""
    # Order matters: slash command can appear inside a local-command-caveat
    # wrapper, and we want to credit the slash command rather than the wrapper.
    if SLASH_RE.search(text):
        return "slash_bootstrap", ""
    m = REVIEW_RE.match(text)
    if m:
        return "template_review", m.group(1)
    if LOCAL_CMD_RE.search(text):
        return "local_command", ""
    return "free_form", ""


def _first_user_text(path: Path) -> str:
    """Return the first non-empty user/human message text, or ""."""
    with path.open() as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = obj.get("message") or {}
            role = msg.get("role") or obj.get("type", "")
            if role not in ("user", "human"):
                continue
            content = msg.get("content")
            if isinstance(content, str):
                t = content.strip()
                if t:
                    return t
            elif isinstance(content, list):
                parts = [
                    (b.get("text") or "")
                    for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                ]
                t = " ".join(parts).strip()
                if t:
                    return t
    return ""


def first_prompt_of(path: Path) -> FirstPromptInfo:
    info = FirstPromptInfo(file=str(path))
    # session_id: pick up from the first object that carries one
    try:
        with path.open() as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sid = obj.get("sessionId") or obj.get("session_id")
                if sid:
                    info.session_id = sid
                    break
    except OSError:
        pass

    text = _first_user_text(path)
    info.n_chars = len(text)
    info.category, info.project_slug = classify(text)
    info.first_prompt = _oneline(text)
    return info
