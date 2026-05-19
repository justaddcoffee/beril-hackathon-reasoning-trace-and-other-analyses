# beril_hackathon_reasoning_trace_vibe_analysis

Open-ended ("vibe") qualitative analysis of the Claude Code reasoning traces collected during the 5/7/2026 KBase / BERIL Co-Scientist Paper Challenge hackathon.

Companion to the formal evaluation the KBase team is running on the KBase Lakehouse evaluation tenant. This repo is the parallel hand-read pass: read traces, look for usage patterns, failure modes, prompting-style effects, how much actual paper-writing got done.

## Source data

| Source | Where |
|---|---|
| Raw participant traces | BERDL hub: `/global_share/<team-member>/claudefiles.zip` (not redistributed) |
| Consent tracking | "Invite list" tab of the hackathon Google Sheet (private — has consent column) |
| Zoom recording / chat / transcript | Drive folder shared by the KBase team (private) |
| Prototype trace browser | `bw.html` (single-page HTML viewer maintained by a team member) |

**Consent filter:** every aggregation script drops sessions from non-opt-in users by default before doing anything that leaves the machine. See `src/consent.py` and the `data/consent.csv` table (gitignored). KBase + BERIL team members are tracked but excluded from public outputs.

## Layout

```
data/         raw traces + consent table (gitignored)
notebooks/    Jupyter notebooks for ad-hoc reading
notes/        figures + working CSVs (most CSVs gitignored)
viewer/       bw.html or other viewers
src/          extraction + classification helpers
scripts/      CLI runners (numbered by step)
```

See `PLAN.md` for the step-by-step runbook and `notes/figures/` for committed figures.
