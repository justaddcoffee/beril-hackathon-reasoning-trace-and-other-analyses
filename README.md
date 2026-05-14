# beril_hackathon_reasoning_trace_vibe_analysis

Open-ended ("vibe") qualitative analysis of the Claude Code reasoning traces collected during the 5/7/2026 KBase / BERIL Co-Scientist Paper Challenge hackathon.

Companion to the formal evaluation that the KBase team are running on the KBase Lakehouse evaluation tenant. This repo is the parallel hand-read pass: read traces by hand, look for usage patterns, failure modes, prompting style effects, how much actual paper-writing got done.

## Source data

| Source | Where |
|---|---|
| Raw participant traces | BERDL hub: `/global_share/<team-member>/claudefiles.zip` |
| Consent tracking | Google Sheet: `KBase/BERIL Co-scientist Paper Challenge - invite list`, Consent tab (gid=1121416091) |
| Zoom recording / chat / transcript | Drive folder shared by the KBase team |
| Prototype trace browser | `bw.html` (single-page HTML viewer, ~4.7 MB) |

**Consent filter:** Apply the consent filter before doing anything that leaves this machine.

## Layout

```
data/         # symlink or copy of the consenting-subset traces (gitignored)
notebooks/    # Jupyter notebooks for ad-hoc reading + annotation
notes/        # markdown notes per-trace and per-pattern
viewer/       # bw.html or other viewers
src/          # any extraction / parsing helpers
```

## GTD project

`~/gtd/projects/lbl-related/beril-hackathon-trace-analysis/`
