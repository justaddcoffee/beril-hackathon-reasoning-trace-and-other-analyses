# Is the BERDL data lakehouse load-bearing? A controlled ablation

**Experiment date:** 2026-05-28
**Project re-run:** `lanthanide_methylotrophy_atlas` (from `kbaseincubator/BERIL-research-observatory`)
**Question:** When a BERIL hackathon job is run *outside* the data lakehouse, does it fail — and would the in-lakehouse results have been "much better"?

---

## TL;DR

**Yes, the lakehouse is load-bearing — decisively for the things that make this a quantitative paper, and the no-lakehouse arm could not have produced this report.** But the failure mode is more interesting than "it crashes":

1. **H2 (environmental enrichment) is simply impossible without the lakehouse.** No denominators, no matched controls, no per-environment odds ratios. The no-lakehouse agent could only cite one-sided anecdotes (a volcanic mudpot, a geothermal soil, a REE-rich mine). Verdict outside: *cannot determine.* Inside: soil/sediment OR=1.92 (p_BH=6×10⁻³⁹), host-associated depletion OR=0.058 across 293K genomes. **The surprise — and the reason this needed the lakehouse — is that the *expected* dramatic environments did NOT pan out: volcanic/geothermal came back OR=0.86 (if anything de-enriched), mining OR=1.12 (ns), and REE-impacted (n=37) OR=3.51 but underpowered (p_BH=0.082). The real enrichment is mundane soil/sediment + marine, not the rare-earth/volcanic sites the field associates with XoxF.** That counterintuitive result is exactly what you can only get from a genome-scale enrichment test, and exactly what the anecdote-only outside arm would have gotten backwards.

2. **Every phylogenetically-controlled statistic is impossible without the lakehouse.** All three hypotheses pre-register an "after phylogenetic control" condition. The no-lakehouse arm could not satisfy it for *any* of them — that needs a per-genome presence/absence matrix on a species tree, which is exactly the curated genome-scale resource it lacks.

3. **H1's headline verdict flips — and that's the most valuable result.** Inside: xoxF:mxaF = **18.9:1**, "strongly supported." Outside, from public KEGG + published surveys: **2–6:1**, "NOT supported at the ≥10× threshold." The reason is a **marker-definition issue the no-lakehouse arm caught and I independently verified**: the lakehouse defines xoxF as KEGG **K00114**, but K00114 is officially `exaA` (a broad cytochrome-c alcohol dehydrogenase, EC 1.1.2.8), *not* the canonical xoxF ortholog **K23995** (lanthanide-dependent methanol dehydrogenase, EC 1.1.2.10). The 19:1 ratio may be partly inflated by a broad KO definition that captures non-xoxF alcohol dehydrogenases.

4. **The no-lakehouse agent degraded *gracefully*, not *dangerously*.** It did not fabricate. Of ~12 numeric claims, ~11 were grounded in live KEGG/UniProt queries or fetched papers; exactly 1 (LanM–xoxF ≥90% co-occurrence) was explicitly flagged "estimate — not verified." A *careful* agent outside the lakehouse says "I can't compute this" rather than inventing an odds ratio. The practical result is the same: you cannot get the answer. But it means the risk isn't hallucinated numbers — it's confident-sounding *direction* with no defensible *magnitude*.

**Bottom line for the hypothesis on the calendar TODO** ("run outside the lakehouse → expect it to fail"): **confirmed**, with nuance. The job cannot be done outside the lakehouse — not because the code throws an error (we deliberately tested the harder version), but because the *science* (effect sizes, phylogenetic control, genome-scale denominators) requires the curated data. And the curated data is only as good as its marker definitions — the ablation surfaced a real one to double-check.

---

## Method (controlled ablation)

- **Subject:** a fresh Claude subagent (same model family as the original hackathon runs, so the *only* variable is data access). It never saw the original REPORT.
- **What was removed:** all BERDL / K-BERDL / KBase / curated-pangenome access.
- **What was allowed:** the subject's own knowledge + the public web/databases (KEGG, UniProt, GTDB, AnnoTree, papers). It was even allowed to download public data and compute real numbers. This *steelmans* the no-lakehouse arm: the question becomes "can public resources substitute for the curated lakehouse?"
- **Contamination guard:** the subject was explicitly forbidden from accessing any BERIL/observatory/"lanthanide methylotrophy atlas" material (the real REPORT is in a public GitHub repo). Subject prompt saved in `SUBJECT_PROMPT.md`; subject output in `no_lakehouse_REPORT.md`.
- **Judge:** this analysis (a separate Claude instance that *did* read the ground-truth REPORT). I independently verified the subject's two load-bearing factual claims against the live KEGG REST API (KO definitions and gene-member counts — both confirmed exactly).
- **Caveats:** not compute-matched (the original was a multi-notebook effort; this was a single agent session); single run; AnnoTree's API was unreachable during the run, which handicapped the no-lakehouse arm's H1 (though "the public tool you needed was down" is itself part of the outside-the-lakehouse reality).

---

## Head-to-head by hypothesis

| | **Inside lakehouse** (ground-truth REPORT) | **Outside lakehouse** (public web only) | **Was the lakehouse load-bearing?** |
|---|---|---|---|
| **H1** xoxF:mxaF ≥10× | **18.9:1** (3,690 vs 195 genomes), p=7.6×10⁻²²; phylogeny-corrected GLMM ~143:1. **Strongly supported.** | **2–6:1** (KEGG members 5.3×; Huang 2019 2.9×; lanthanome 2025 1.9×). Direction supported; **magnitude NOT supported at ≥10×.** No phylo control possible. | **Yes — verdict flips.** And the ablation flagged that the lakehouse's xoxF=K00114 definition is broader than canonical xoxF (K23995); see below. |
| **H2** cassette enriched in REE/mineral environments | **Partially supported, but not as predicted:** enrichment is in soil/sediment OR=**1.92** (p_BH=6×10⁻³⁹) and marine 1.31 — *not* the expected REE/volcanic/mining sites (volcanic OR=0.86; mining OR=1.12 ns; REE-impacted n=37 OR=3.51 but p_BH=0.082, underpowered). Host-associated strongly depleted (OR=**0.058**). | **Cannot determine.** Only one-sided anecdotes; no denominators, no controls, no odds ratios. Refused to invent ORs. (Would likely have concluded "enriched in REE/volcanic sites" from the anecdotes — i.e. backwards.) | **Yes — completely.** Impossible without the annotation×metadata join over 293K genomes; and the genome-scale test *overturns* the intuitive REE/volcanic expectation. |
| **H3a** lanmodulin clade-restricted | **62/62 = 100%** in Beijerinckiaceae/Acetobacteraceae/Hyphomicrobiaceae, p=9.8×10⁻⁷. **Strongly supported.** | LanM overwhelmingly Alphaproteobacteria, but published surveys place hits in **Methylocystaceae/Nitrobacteraceae** (and 1 *Streptomyces*) — i.e. "the exact 3-family list is too narrow." Fraction-in-those-3 < 100%. | **Yes** for the exact, quantified clade boundary; the broad qualitative shape ("alpha methylotrophs") is reachable from public surveys. |
| **H3b** xoxF co-occurrence ≥80% | **79.0%** (49/62), p=0.65. **Not formally supported.** | **Cannot compute** (needs LanM+xoxF calls on the *same* genome set). Flagged a guess of "≥90%" — which would have been *wrong* (true value is just under 80%). | **Yes.** Note the one place the no-lakehouse agent guessed, its guess was on the wrong side of the threshold. |

---

## The marker-definition finding (independently verified)

This is the non-obvious result worth escalating. Verified against the live KEGG REST API on 2026-05-28:

| KO | KEGG symbol & definition | EC |
|---|---|---|
| **K00114** (lakehouse's "xoxF") | `exaA` — alcohol dehydrogenase (cytochrome c) | 1.1.2.8 |
| **K14028** (mxaF) | `mdh1, mxaF` — methanol dehydrogenase (cytochrome c) subunit 1 ✓ | 1.1.2.7 |
| **K23995** (canonical xoxF) | `xoxF` — lanthanide-dependent methanol dehydrogenase | 1.1.2.10 |

KEGG gene-member counts (live): K00114 = **1,110**, K23995 = **648**, K14028 = **122**.

**Implication:** K00114 is a broader periplasmic-ADH ortholog (exaA/PedH-like) that subsumes more than canonical xoxF. The lakehouse REPORT used `KEGG_ko LIKE '%K00114%'` as its primary xoxF definition (its own NB01 calibration even *notes* "the eggNOG K00114 set is broader"). So the headline 18.9:1 is partly a function of that choice. Using the canonical xoxF KO (K23995) against mxaF (K14028) gives 5.3:1 in KEGG's curated set — still clearly xoxF-dominant in direction, but well under the pre-registered 10× threshold.

**This does not mean the lakehouse is "wrong"** — it has bakta cross-validation, vastly more genomes than KEGG's curated panel, and the broad-ADH set may legitimately reflect XoxF-family enzymes that KEGG splits across KOs. But it *is* a genuine validity check that the in-lakehouse analysis would benefit from. **Recommended follow-up: re-run H1 inside the lakehouse with K23995 (and a bakta-`product='lanthanide-dependent methanol dehydrogenase'` intersection) and report whether 19:1 survives a tightened xoxF definition.**

---

## What the no-lakehouse arm could NOT see at all (lakehouse-only findings)

These are in the ground-truth REPORT and have no public substitute — they are the affirmative case for the lakehouse:

- **Non-canonical high-rate xoxF carriers:** Acidobacteriota (28% of genomes), Gemmatimonadota (25%), Methylomirabilota (29%) — phyla rarely cited in the methylotrophy literature. Discoverable only by scanning all 293K genomes.
- **The REE-AMD community structure:** 37 MAGs from rare-earth acid-mine-drainage water are dominated by acidophiles (*Acidocella*, *Acidiphilium*, *Thiomonas*, *Metallibacterium*) — *not* methylotrophs (only 4/37 carry xoxF), including the previously uncharacterised `f__REEB76` clade. This flips the naive "REE environments are full of REE-users" narrative.
- **Marker-source calibration:** eggNOG `Preferred_name='lanM'` produces 505 false positives in unrelated gut Bacillota; bakta `product` is the trustworthy source. (Notably, the no-lakehouse arm independently re-derived a version of this: it found UniProt name-search for "lanmodulin" returns only 2 entries and is useless — same underlying lesson, reached from the outside.)
- **The PQQ-supply asymmetry resolution:** of ~2,300 xoxF-without-PQQ genomes, 59% are eggNOG annotation gaps that bakta rescues; ~24% genuinely lack PQQ evidence.
- **Exact effect sizes with CIs and FDR correction** for every claim.

---

## Groundedness / honesty tally (no-lakehouse arm)

| Category | Count |
|---|---|
| Numeric claims grounded in a live query or fetched paper | ~11 |
| Numeric claims explicitly flagged "estimate — not verified" | 1 (LanM–xoxF ≥90%, low confidence) |
| Covert fabrications (confident numbers with no source) | **0** |
| Effect sizes refused rather than invented | H2 odds ratios; H3b co-occurrence % |

The agent also independently caught two things the prompt got slightly wrong (the K00114 mis-mapping; Pol et al. 2014 being in *Environmental Microbiology*, which the real REPORT's reference list also corrects). This is a well-behaved agent: when it lacked the data it said so, rather than confabulating.

---

## Conclusion

Re-running a BERIL job outside the lakehouse **does effectively fail** — confirming the calendar-TODO hypothesis — but the precise sense matters:

- It does *not* fail by throwing an exception (we tested the harder, fairer version: same scientific question, public web allowed).
- It fails because the **science requires the curated, genome-scale data**: you cannot produce effect sizes, denominators, matched controls, or any phylogenetically-controlled statistic from public single-genome papers and KEGG's model-organism-biased panel. The lakehouse-grounded report is "much better" in exactly the way the original hypothesis predicted.
- A careful agent fails *honestly* (admits ignorance) rather than *dangerously* (fabricates) — but it still cannot do the job.
- **Unexpected dividend:** forcing the analysis through first-principles public reasoning surfaced a real marker-definition concern (xoxF = K00114 vs K23995) that is worth verifying *inside* the lakehouse. The ablation is therefore useful not just as a "lakehouse is load-bearing" demo, but as a free validity check on the headline H1 number.

## Recommended next steps

1. **Share the marker-definition finding with the analysis authors** and re-run H1 inside the lakehouse with the canonical xoxF KO (K23995) ± bakta intersection; report whether 19:1 holds under a tightened definition.
2. If a cleaner "lakehouse is load-bearing" demo is wanted for a talk, **H2 is the single best illustration**: effect sizes that are flatly impossible outside, vs. richly quantified inside.
3. Optional robustness: repeat the ablation with a different model (e.g. Codex) to confirm the failure isn't Claude-specific.
