# Plan - BERIL Hackathon Reasoning-Trace Vibe Analysis

Open this file when you `cd` into the repo. It's the working plan and the runbook.

GTD project: `~/gtd/projects/lbl-related/beril-hackathon-trace-analysis/`

## What this is

Qualitative ("vibe") analysis of the Claude Code reasoning traces collected during the **5/7/2026 KBase / BERIL Co-Scientist Paper Challenge hackathon**. Companion to the formal evaluation Param / Chris / Elisha are running on the KBase Lakehouse evaluation tenant. Goal: a sense of *how participants used the agent* - patterns, failure modes, prompting style effects, how much of a paper actually got written.

## Source data

| What | Where |
|---|---|
| Raw participant traces | BERDL hub `/global_share/gazimahmud/claudefiles.zip` |
| Consent tracking | [Google Sheet, Consent tab gid=1121416091](https://docs.google.com/spreadsheets/d/17wLZUVccD6y7Q2aNkMyV7cU1PaH5yUgNUPA6dkv2O-g/edit?gid=1121416091#gid=1121416091) |
| Zoom recording / chat / transcript | [Drive folder](https://drive.google.com/drive/folders/1x5yI3orSlHwRqYvsIl2UbOQV6FOE0Tzx) |
| Chris's prototype trace browser | `~/gtd/tmp/beril-traces/bw.html` |
| KBase Lakehouse evaluation tenant | (Elisha set up; you were being added 5/11) |

**Consent filter before doing anything that leaves this machine:** Ben opted out, Nik Chia did not reply (excluded). Chris H + Ranjan opted in. KBase + BERIL team members are in but not part of the public summary.

## How to pull the data

You'll need ssh access to the BERDL hub. Once in:

```bash
# from BERDL hub, e.g.
scp /global_share/gazimahmud/claudefiles.zip <local>:~/PythonProject/beril_hackathon_reasoning_trace_vibe_analysis/data/

# locally
cd ~/PythonProject/beril_hackathon_reasoning_trace_vibe_analysis
mkdir -p data
unzip data/claudefiles.zip -d data/claudefiles/
```

`data/` is in `.gitignore` - nothing in there leaves the repo.

If the zip layout is different from `~/.claude/projects/<encoded-cwd>/<session>.jsonl`, the parser still works (it walks `**/*.jsonl`), but the per-user breakdown depends on each user having their own subdirectory. If users are mixed at the top level, we'll need to reconstruct user identity from the trace metadata - flag that and re-run.

## The plan

### Step 1 - Inventory & shape (mechanical, ~1 hr)

Get the count before reading anything. Histograms only, no judgment.

```bash
python3 scripts/01_inventory.py data/claudefiles/
```

Writes `notes/01_inventory.csv` (one row per session) and prints to stdout:
- sessions per user
- turns/session histogram
- tool calls/session histogram
- duration histogram
- time-to-first-tool histogram
- top tools across all sessions

**Why this comes first:** kills the urge to over-generalize from the first three traces you happen to read. Without baseline shape, every later observation is anecdotal.

### Step 2 - Outcome labeling (the cheapest signal, ~30 sec/session)

For each session, one of three labels:
- `nothing` - produced no real artifact
- `partial` - some scaffolding / fragments / notes but not paper-shaped
- `real` - something that looks like a paper-fragment by the end

```bash
python3 scripts/02_outcome_labels.py data/claudefiles/
# then open the CSV and fill in the `label` column
open notes/02_outcomes_to_label.csv
```

The script extracts per-session: files written, last assistant text, last user text, total chars written, manuscript-like-file-detected. You scan and label. Don't grade quality yet - just bucket. The bucket is what makes every later question be "compared to what?"

If the manuscript-detector regex (`paper|manuscript|draft|abstract|main|writeup|results.{md,tex,ipynb,docx,rmd,qmd}`) is missing the actual artifact names from the hackathon, widen it in `src/outcomes.py` and re-run.

### Step 3 - Read 5 traces end-to-end, narrate (~30 min/trace)

Stratified sample: 2 from `real`, 2 from `partial`, 1 from `nothing`. Write a paragraph per trace describing what happened in your own words, into `notes/03_narratives/<session_id>.md`.

This is the actual "vibe" part. It's slow but it's the only way to know what categories are even worth coding for.

```bash
mkdir -p notes/03_narratives
# pick 5 sessions from notes/02_outcomes_to_label.csv based on label distribution
# read each via Chris's bw.html viewer or by directly reading the .jsonl
```

### Step 4 - Extract a coding scheme from those 5

Candidate dimensions to look for during step 3 (don't lock these in until you've read the 5):
- Prompting style: one big prompt vs. iterative
- Use of subagents (`Task` tool) - did anyone use them?
- Recovery from a wrong tool call - retried, gave up, asked human?
- Off-topic loops
- Asking-vs-instructing (questions to the agent vs. directives)
- Trust calibration - did the user trust the agent's output? Spot-check it?
- Domain anchoring - did the user supply enough biology context, or expect the agent to know?

Lock the final list into `notes/04_coding_scheme.md` and a small CSV template in `notes/04_codes.csv`.

### Step 5 - Code the rest against the scheme (~5 min/session)

Skim, don't deep-read. Fill in `notes/04_codes.csv` for every consenting session. Param's formal analysis will be doing the structured stuff; you're filling in the qualitative texture they can't easily quantify.

### Step 6 - Failure-mode pass

Now you have ground truth and a coding sheet, so failure modes get tagged in context. Specifically watch for:
- Hallucinated tool args
- Hallucinated dataset / file / schema names
- Looping retries on the same failing call
- Agent talking past the user
- Premature "task complete" claims
- Giving up too early
- Bad ontology / vocabulary choices
- Silent failure (tool returned an error, agent didn't notice)

Write into `notes/05_failure_modes.md` with one section per pattern, each section listing the session_ids where you saw it.

**Why failure modes come last, not first:** failure-mode-first biases the read - you find what you go looking for. Doing inventory → outcomes → narrative → coding *first* keeps the analysis honest and gives you something to compare against Param's run.

## Coordination

- Param's formal analysis is happening in the KBase Lakehouse evaluation tenant. Don't duplicate quantitative work - check with Param on what they're already extracting (turn counts, tool counts, etc., are likely covered).
- Your value-add is the qualitative texture: narratives in step 3, coding scheme in step 4, failure-mode patterns in step 6.
- Cross-reference the Zoom transcript when a trace is confusing - participants said things out loud they didn't type into the agent.
- Keep `notes/` markdown-friendly so we can publish a writeup as-is.

## Outputs to aim for

- `notes/01_inventory.csv` - shape stats, one row per session
- `notes/02_outcomes_to_label.csv` - human-labeled outcome bucket per session
- `notes/03_narratives/*.md` - 5 stratified deep-reads
- `notes/04_coding_scheme.md` + `notes/04_codes.csv` - dimensions + per-session codes
- `notes/05_failure_modes.md` - one section per pattern
- `notes/99_writeup.md` - short writeup for Param/Chris/Elisha; potentially a section in the OpenScientist Sage talk (Jul 28 - see `~/gtd/projects/openscientist/sage-elite-talk-jul-2026/`)

## Repo layout

```
src/         inventory.py, outcomes.py - per-session extractors (importable)
scripts/     01_inventory.py, 02_outcome_labels.py - CLI runners
notes/       all output goes here (CSVs, narratives, coding, writeup)
notebooks/   Jupyter for ad-hoc exploration if needed
data/        raw traces (gitignored)
viewer/      Chris's bw.html or other viewers
```

## Status (5/14/2026)

- [x] Repo scaffolded
- [x] Step-1 inventory parser + runner
- [x] Step-2 outcome-triage parser + runner
- [x] Smoke-tested both against local Claude Code session dirs (same JSONL format)
- [x] Pull `claudefiles.zip` from BERDL (it's a gzipped tar, not a zip - 2291 jsonl, 80 users)
- [x] Step 1 on BERIL data -> `notes/01_inventory.csv`
- [ ] Step 2 labeling (`notes/02_outcomes_to_label.csv` generated; `label` column still empty)
- [ ] Step 3 narratives
- [ ] Step 4 coding scheme
- [ ] Step 5 coding pass
- [ ] Step 6 failure modes
- [ ] Step 7 writeup
