# Subject prompt — no-lakehouse re-run

This is the exact, self-contained task given to a fresh Claude subagent that has
NOT seen the original lakehouse-grounded report. It is the "outside the data
lakehouse" arm of the ablation. The subject may use general scientific knowledge
and public web/databases, but has NO access to the BERDL data lakehouse.

---

You are an AI co-scientist. Your job is to test three pre-registered hypotheses
about the lanthanide-dependent methanol-oxidation system in bacteria and archaea,
and write a scientific report with quantitative results.

## Hard constraints (read carefully)

- You do **NOT** have access to the BERDL data lakehouse, K-BERDL, KBase, any
  curated pangenome Spark/Delta tables, or any pre-computed annotation matrix.
  Assume those simply do not exist for you.
- You **MAY** use your own knowledge and the public web/databases: published
  papers, NCBI, KEGG, UniProt, GTDB, AnnoTree, JGI/IMG, etc. If you can pull
  public data and compute a real number, do so and show your work.
- You **MUST NOT** search for, open, or use any existing "BERIL", "BERDL
  observatory", "Microbial Discovery Forge", "research observatory", or
  "lanthanide methylotrophy atlas" analysis/report/repository. This is meant to
  be YOUR independent attempt. Do not look for someone else's answer. If you
  stumble on such a result, stop and do not use it.
- For **every quantitative claim**, state (a) the number, (b) its source (a
  citation, a database query you actually ran, or "estimate from my own
  knowledge — not verified"), and (c) your confidence (high/medium/low).

## Research question

What is the phylogenomic distribution and cassette-completeness of the
lanthanide-dependent methanol/ethanol oxidation system (xoxF / xoxJ / PQQ /
lanmodulin) across sequenced bacteria and archaea, and does its presence
correspond to environments containing rare earth elements (REEs)?

## Hypotheses to test

- **H1 (xoxF dominance)**: xoxF (KEGG K00114, REE-dependent methanol
  dehydrogenase) is genome-frequent at **≥10×** the rate of mxaF (KEGG K14028,
  Ca-dependent methanol dehydrogenase) across sequenced genomes. Test whether
  this ratio is robust across phyla after accounting for phylogenetic
  non-independence. Report the actual xoxF:mxaF ratio (with an interval if you
  can) and a verdict: supported / not supported / cannot determine.
  - H0: xoxF and mxaF occur at indistinguishable rates once phylogeny and genome
    size are controlled.

- **H2 (environmental enrichment)**: Genomes carrying the *full* lanthanide-MDH
  cassette (xoxF + xoxJ + ≥1 PQQ-biosynthesis gene) are over-represented in
  samples whose environmental metadata reference REEs, mining drainage,
  methylotrophic media, volcanic/geothermal sources, or other mineral-rich
  substrates, versus matched host-associated and generic environmental controls.
  Report effect sizes (e.g. odds ratios) per environment class if you can, and a
  verdict.
  - H0: full-cassette presence is independent of environmental metadata after
    phylogenetic control.

- **H3 (lanmodulin clade restriction)**: Lanmodulin product hits are restricted
  to a small set of α-Proteobacterial methylotroph clades (Beijerinckiaceae,
  Acetobacteraceae, Hyphomicrobiaceae) and co-occur with xoxF in **≥80%** of
  cases. Report the fraction of lanmodulin-bearing genomes inside those clades,
  the xoxF co-occurrence fraction, and a verdict.
  - H0: lanmodulin product hits are taxonomically diffuse and uncorrelated with
    xoxF presence.

## Literature context (public, fair to use)

The lanthanide switch in methylotrophs was discovered when Pol et al. (2014,
Nature) characterized XoxF in *Methylacidiphilum fumariolicum* SolV from a
volcanic mudpot. Subsequent work showed xoxF is widespread (Skovran &
Martinez-Gomez 2015; Chistoserdova 2016) but pangenome-scale surveys remained
limited to a few hundred genomes. Lanmodulin (LanM) was discovered in
*Methylobacterium extorquens* AM1 (Cotruvo et al. 2018, JACS) as a high-affinity
REE-binding protein. Picone & Op den Camp (2019) reviewed REE-dependent enzymes
and the open environmental questions.

## Deliverable

Write a report to:
`/Users/jtr4v/PythonProject/beril_hackathon_reasoning_trace_vibe_analysis/lakehouse-ablation/no_lakehouse_REPORT.md`

Structure it as:
1. **Per-hypothesis findings** (H1, H2, H3) — for each: your best quantitative
   estimate(s), the source/confidence tagging required above, and a verdict.
2. **Methods / what you actually did** — which public resources you queried, what
   you computed vs. estimated, and what you could NOT obtain without genome-scale
   curated data.
3. **Limitations** — be explicit about where you had to guess and where a
   curated, genome-scale annotation resource would have been required to answer
   properly.

Be rigorous and honest. Do not invent precise statistics you cannot support; if
you can only give a qualitative or order-of-magnitude answer, say so.
