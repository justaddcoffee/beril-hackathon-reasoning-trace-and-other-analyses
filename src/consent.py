"""Consent filter for the BERIL trace analysis.

Single source of truth for "which user_dirs are we allowed to include in
analyses that leave this machine." Every script that aggregates across
users should call `load_consenting_users()` and intersect against it before
doing anything else.

The consent.csv file is gitignored - it carries real names and per-person
decisions. Generate the stub with `scripts/00_bootstrap_consent.py`, then
fill it in from the Google Sheet:

    https://docs.google.com/spreadsheets/d/17wLZUVccD6y7Q2aNkMyV7cU1PaH5yUgNUPA6dkv2O-g/edit?gid=1121416091#gid=1121416091

Schema:
    user_dir      - directory name under claudefiles/ (the join key)
    display_name  - human-readable name, for the human filling in the sheet
    consent       - one of: opt_in, opt_out, no_reply, team, unknown

`load_consenting_users()` returns the set of user_dirs where consent ==
"opt_in" (and optionally "team" if include_team=True). Anything else -
opt_out, no_reply, unknown, blank - is excluded by default. Fail closed.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

VALID_CONSENT = {"opt_in", "opt_out", "no_reply", "team", "unknown"}
DEFAULT_PATH = Path("data/consent.csv")


def load_consent_table(path: Path | str = DEFAULT_PATH) -> dict[str, str]:
    """Return {user_dir: consent_value} from the consent CSV.

    Raises FileNotFoundError if the file is missing - callers should decide
    whether to fail or fall back, but the loader itself does not silently
    return empty (that would be indistinguishable from "nobody consented").
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"consent file not found: {path}\n"
            f"run: python3 scripts/00_bootstrap_consent.py data/claudefiles/\n"
            f"then fill in the consent column from the Google Sheet."
        )
    table: dict[str, str] = {}
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            user_dir = (row.get("user_dir") or "").strip()
            consent = (row.get("consent") or "").strip().lower() or "unknown"
            if not user_dir:
                continue
            if consent not in VALID_CONSENT:
                # treat typos as unknown rather than silently bucketing them
                consent = "unknown"
            table[user_dir] = consent
    return table


def load_consenting_users(
    path: Path | str = DEFAULT_PATH,
    *,
    include_team: bool = False,
) -> set[str]:
    """Return the set of user_dirs we're allowed to include in analysis.

    By default: opt_in only. Pass include_team=True to also include KBase /
    BERIL team members (who consented to internal analysis but should not
    appear in public summaries - PLAN.md explicitly carves them out).
    """
    table = load_consent_table(path)
    allowed = {"opt_in"} | ({"team"} if include_team else set())
    return {u for u, c in table.items() if c in allowed}


def filter_sessions(sessions, consent_path: Path | str = DEFAULT_PATH,
                    *, include_team: bool = False, strict: bool = True):
    """Filter an iterable of session objects (any object with .user_dir).

    If consent_path is missing and strict=True, raises. If strict=False, emits
    a loud warning to stderr and returns the input unchanged - used by the
    bootstrap step before consent.csv exists.
    """
    try:
        allowed = load_consenting_users(consent_path, include_team=include_team)
    except FileNotFoundError as e:
        if strict:
            raise
        print(f"WARNING: {e}\nWARNING: proceeding WITHOUT consent filter - "
              f"do not publish these outputs.", file=sys.stderr)
        return list(sessions)
    filtered = [s for s in sessions if s.user_dir in allowed]
    return filtered
