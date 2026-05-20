# Jacob Rapp — non-programmer, technical output

The first of the Step-3 stratified deep-reads called for in PLAN.md.
Picked because Jacob's profile is a strong test of the hackathon's
premise: he's a wet-lab postdoc, not a programmer, and we wanted to see
what he could get out of BERIL in a single afternoon.

He opted in to this analysis.

## Profile

Postdoc at JBEI / LBNL. From his Invite-list proposal: a transcriptomics-
based method for predicting bioproduct titer in engineered bacterial
strains; ~10 transcripts out of 5700 produce R² > 0.9 on a small
collaborator-owned dataset, and the hackathon question is whether the
approach generalizes to public KBase data.

## Activity shape

8 main sessions on 2026-05-07, all on his project
`abf_proteome_metabolome_prediction` (Agile Biofoundry proteome /
metabolome prediction). Seven of the sessions are short — bootstrap
retries and conversation continuations after context-window exhaustion.
**One session is the whole story**: a 5.5-hour deep session running
16:35–22:08 UTC.

The 5.5-hour session:

| metric | value |
|---|---|
| turns | 749 |
| tool calls | 465 |
| duration | 333 min |
| Bash calls | 243 |
| Read calls | 35 |
| Edit calls | 35 |
| Write calls | 21 |
| distinct files written | 15 |
| subagent spawns | 0 |

Zero subagent spawns — the main agent did all the work itself.

## What Jacob said, in order

Twelve substantive user messages over the session, edited down from a
longer thread of conversation continuations and slash commands.
Verbatim, abridged:

1. *"What KBase databases would contain transcriptomic, proteomic, or metabolomic data?"*
2. *"In ese_ganymede, are there any datasets where you have proteomics and metabolomics for the same strains?"*
3. *"find me strains for which we have both metabolomic data and proteomic or transcriptomic data. My goal is to predict metabolites from the other types of omics."*
4. *"for the dataset mdc:sty-11-8ws97026, can you confirm that the proteomics are in fact proteomics for individual strains and not metaproteomics?"*
5. *"I would prefer isolate-level data, since I plan to later apply this to strain engineering efforts. Check Enigma for appropriate data."*
6. *"Let's work from the Agile BioFoundry DBTL pipeline data. That work is published and the data should be easily accessible. I know the researcher practices immaculate data hygeine, so the data should be trustworthy."*
7. *"Let's revisit the experimental plan. I am less interested in using this to select genes to modify and more interested in picking a subset of genes as a sensor or bioproduct titer. Our goal is to sense, not design."*
8. *"This information looks accurate based on the analysis you have provided. Proceed with literature search and writing."*
9. *"Address the issues. Identifying 1155720 would improve this paper greatly, and we care about reproducibility."*
10. *"Address only the critical correction."*
11. *"Push it to my fork."*
12. *"Please make a visual abstract to go with this work."*

Zero lines of code. Every message is scientific English. Several are
domain-grounded judgments (data quality, methodology choice, validation
of agent output). Message 7 is a mid-flight pivot from "design" to
"sense" — Jacob changed the experimental question after seeing what the
data could support, and steered Claude into the new framing.

## What Claude did

The Bash trace is dominated by PySpark queries against the BERDL
Lakehouse, e.g.:

```python
from berdl_notebook_utils.setup_spark_session import get_spark_session
spark = get_spark_session()
# Check what assay types exist...
```

Schema inspection, joins across `ese_ganymede` / NMDC / Enigma /
Agile-Biofoundry tables, model training (LOOCV across panel sizes,
permutation tests), manuscript drafting, git operations. Jacob never
typed any of this.

## Files produced

15 distinct files (66 writes total), all under his project directory:

- `REPORT.md` (21 edits) — the manuscript draft
- `README.md`, `RESEARCH_PLAN.md`, `references.md` (project docs)
- `beril.yaml`, `requirements.txt` (config)
- 6 Jupyter notebooks: `01_data_acquisition_and_qc.ipynb` through
  `06_cross_study_validation.ipynb`
- `scripts/visual_abstract.py`
- `REVIEW.md` (the automated reviewer agent's feedback)

## The final REPORT.md

252 lines, ~21 KB. Title: *"Minimal Protein Biosensor Panel for 3HP
Titer in Engineered Aspergillus"*. Excerpted findings:

> *Finding 1: A 5-protein panel predicts 3HP titer with R² = 0.94 in*
> A. pseudoterreus*.* In round 1 (n = 17 strains), the panel achieves
> LOOCV R² = 0.94, MAE = 0.025 mmol/gDW/hr, Spearman ρ = 0.895,
> permutation p = 0.001.

> *Finding 2: A single protein explains 56% of 3HP titer variance in*
> A. niger*.* In round 2 (n = 24 strains), protein 1155720 alone
> achieves LOOCV R² = 0.56.

> *Finding 3: Protein 1155720 is a universal 3HP titer predictor
> across* Aspergillus *species.*

Plus the visual abstract Jacob asked for and a push to his fork. The
agent's last assistant text: *"Done. The visual abstract has been added
to `figures/visual_abstract.png`, referenced at the top of REPORT.md,
and pushed to your fork."*

## What this case shows

A wet-lab postdoc with no programming background, in a single afternoon,
directed a research project end-to-end in scientific English and walked
away with: a 252-line manuscript draft with cross-validated quantitative
findings, six analysis notebooks, a generated visual abstract, and a
git-pushed fork.

It doesn't show that the science is correct. Spot-checking the report
against the underlying data, the notebooks, and prior literature is a
separate task; this narrative is about workflow shape, not result
validity.

What it does suggest is that for some non-programming users on some
templated harnesses, "what can Claude do with this person" is bounded
much more by the user's scientific judgment than by their fluency in
any technical stack. Jacob made domain calls Claude could not have made
(which datasets are trustworthy; which framing is more useful; which
review feedback is critical) and Claude did the technical work Jacob
could not have done.

## Caveats specific to this narrative

- One participant, one project, one afternoon. Generalization is
  unwarranted; this is a single point.
- Outcome bucketing under Step 2 hasn't been done. The artifact looks
  paper-shaped, but the labeling pass will decide whether to bucket it
  as `real` or `partial`.
- The agent reports the work; nobody has independently rerun the
  notebooks or verified the statistics.
- Jacob is one of 32 opt-in users. Other opt-in narratives may show
  very different patterns.
