# Usability notes

How smoothly sessions ran (not what they produced). Opt-in main sessions
only (252 sessions, 32 users). From `scripts/01g_usability.py`. Numbers
independently re-derived in a codex review; corrections noted at the end.

## Errors are common but mostly recoverable

| tool | calls | fail% | recovery% † |
|---|---:|---:|---:|
| Bash | 6199 | 12.5% | 73% |
| Read | 1965 | 8.1% | 80% |
| Write | 657 | 6.1% | 91% |
| Edit | 664 | 4.8% | 83% |
| NotebookEdit | 321 | 2.2% | 100% |

† recovery = next call to the *same* tool succeeded (a lower bound). Only 9
Bash errors were never retried. Fig 12.

## Session-level friction

| signal | share |
|---|---:|
| any tool error | 51% |
| context reset | 14% |
| ended on unresolved error | 6% (16/252; 10% of the 157 with tools) |
| Bash thrashing (same cmd ≥3×) | 2% |

Context resets (92 across 36 sessions) are the more disruptive friction —
a recovered tool error usually isn't felt; a reset is. Thrashing was mostly
notebook-execution and git retries, not loops. Fig 13.

## Bash failures (777, regex-categorized, rough)

~24% agent Python crashes (NameError, ModuleNotFoundError), ~14% missing
files, ~10% user rejections, rest bare exit codes. Recurring infra:
`spark_connect_remote` missing (24), MinIO credential failures (2).

## Corrections from the codex review

- **Dropped the "bootstrap retry tax."** High `/berdl_start` counts are
  normal session starts, not friction — strictly operationalized (no-work
  bootstrap → another within 10 min) there were 2 events, 1 user.
- AskUserQuestion / ExitPlanMode `is_error` excluded — mostly user
  rejections, not failures (AskUserQuestion has ~29 genuine
  `InputValidationError`s, noted separately).
- Disengagement: 0/32 opt-in users (corrects an earlier session-vs-user
  conflation).

## Not yet computed
User dwell time; permission-rejection rate by tool; onboarding tax
(bootstrap → first real work).
