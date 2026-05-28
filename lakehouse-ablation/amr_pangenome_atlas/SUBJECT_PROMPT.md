# Subject prompt — no-lakehouse re-run (AMR pangenome atlas)

This is the exact, self-contained task given to a fresh Claude subagent that has
NOT seen the original lakehouse-grounded report. It is the "outside the data
lakehouse" arm of the second ablation study (skeptic-proof axis: AMR has rich
public databases, so the subject can make real progress). The subject may use
general knowledge and public web/databases, but has NO access to the BERDL data
lakehouse.

---

You are an AI co-scientist. Your job is to test six pre-registered hypotheses
about the genomic landscape of antimicrobial resistance (AMR) genes across
bacteria, and write a scientific report with quantitative results.

## Hard constraints (read carefully)

- You do NOT have access to the BERDL data lakehouse, K-BERDL, KBase, any curated
  pangenome Spark/Delta tables, or any pre-computed AMR/annotation matrix. Assume
  those do not exist for you.
- You MAY use your own knowledge and the public web/databases. For this topic the
  relevant public resources are excellent and you SHOULD use them: CARD, ResFinder,
  NCBI AMRFinderPlus / Reference Gene Catalog (NDARO), NCBI/GTDB, the Fitness
  Browser (fit.genomics.lbl.gov), AlphaFold/PDB, and the primary literature. If
  you can pull public data and compute a real number, do so and show your work.
- You MUST NOT search for, open, or use any existing "BERIL", "BERDL observatory",
  "Microbial Discovery Forge", "research observatory", or "Pan-Bacterial AMR Gene
  Landscape" analysis/report/repository (e.g. any github.com/kbaseincubator repo).
  This is YOUR independent attempt — do not look for or use someone else's answer.
  If you stumble on such a result, stop and do not use it.
- For EVERY quantitative claim, state (a) the number, (b) its source — a citation,
  a public database query you actually ran, or the explicit label "estimate from
  my own knowledge - not verified" — and (c) your confidence (high/medium/low).

## Research question

What is the distribution, conservation, phylogenetic structure, functional
context, environmental association, and fitness cost of antimicrobial resistance
(AMR) genes across bacterial species — and what does this reveal about the ecology
and evolution of resistance?

## Hypotheses to test

- **H1 (Conservation)**: AMR genes are enriched in the *accessory* genome (vs the
  core genome) relative to the genome-wide average, reflecting conditional
  selection dependent on antibiotic exposure. Report the AMR core fraction vs the
  overall pangenome core fraction and an effect size if you can; verdict.

- **H2 (Phylogenetic distribution)**: AMR genes are concentrated in specific
  lineages (e.g. clinical Gammaproteobacteria such as *Klebsiella*, *Salmonella*,
  Enterobacteriaceae) rather than evenly distributed across phyla, and correlate
  with pangenome openness. Report per-lineage AMR density and any
  openness correlation; verdict.

- **H3 (Functional context)**: AMR clusters are functionally enriched near defense
  systems, membrane/ion transport, and cell-wall biosynthesis ("defense islands"),
  not functionally isolated. Report functional-category enrichment if you can;
  verdict.

- **H4 (Environmental signal)**: Host-associated / clinical species carry more AMR
  genes — and more *acquired* (less core) AMR — than environmental isolates.
  Report per-environment AMR density and a less-core-in-clinical comparison if you
  can; verdict.

- **H5 (Annotation depth)**: A subset of AMR clusters are "AMR-only" — flagged by
  AMR detection but lacking other functional annotation, representing novel or
  poorly characterized resistance. Report the fraction of AMR clusters that are
  annotation-poor; verdict.

- **H6 (Fitness cost)**: AMR genes impose a measurable *fitness cost* in standard
  lab conditions (consistent with their accessory status). Report the fitness
  effect of AMR vs non-AMR genes (e.g. from RB-TnSeq / Fitness Browser data) if
  you can; verdict.

## Literature context (public, fair to use)

AMR is classically studied one pathogen at a time (CARD, NDARO, ResFinder).
Pan-bacterial syntheses exist as reviews (Crofts et al. 2017 Nat Rev Micro;
Larsson & Flach 2022 Nat Rev Micro) rather than uniform data across thousands of
species. AMRFinderPlus / the NCBI Reference Gene Catalog (Feldgarden et al. 2021)
is the standard annotation tool and notably includes stress-response genes (e.g.
mercury/arsenic resistance) under its broad AMR scope. The "cost of resistance"
is a long-standing concept in the literature.

## Deliverable

Write a report to this exact path:
`/Users/jtr4v/PythonProject/beril_hackathon_reasoning_trace_vibe_analysis/lakehouse-ablation/amr_pangenome_atlas/no_lakehouse_REPORT.md`

Structure it as:
1. **Per-hypothesis findings** (H1-H6) — for each: your best quantitative
   estimate(s), the source/confidence tagging required above, and a verdict
   (supported / not supported / cannot determine).
2. **Methods / what you actually did** — which public resources you queried, what
   you computed vs. estimated, and what you could NOT obtain without genome-scale
   curated data.
3. **Limitations** — be explicit about where you had to guess and where a curated,
   genome-scale annotation×conservation×environment×fitness resource would have
   been required to answer properly.

Be rigorous and honest. Do not invent precise statistics you cannot support; if
you can only give a qualitative or order-of-magnitude answer, say so. Genuinely
attempt the best quantitative answers you can with the public resources available.
