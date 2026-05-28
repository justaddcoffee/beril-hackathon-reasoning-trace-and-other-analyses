# Is the BERDL data lakehouse load-bearing? Study 2 — the skeptic-proof case (AMR)

**Experiment date:** 2026-05-28
**Project re-run:** `amr_pangenome_atlas` (Pan-Bacterial AMR Gene Landscape) from `kbaseincubator/BERIL-research-observatory`
**Why this project:** Study 1 (lanthanide) tested the *easy* case — a niche topic with no public substitute, where the lakehouse trivially wins. AMR is the *hard* case: it has excellent public databases (CARD, ResFinder, NCBI AMRFinderPlus/NDARO) and a huge literature, so a no-lakehouse agent can make real progress. The question here is sharper: **does the lakehouse still add decisive value even when the public data is good?**

---

## TL;DR

**Yes — and this is the more convincing of the two studies, because the no-lakehouse arm did *well* and the lakehouse still owned everything that matters.**

1. **Direction is recoverable from public data; effect sizes are not.** With CARD/AMRFinderPlus/literature, the no-lakehouse agent recovered the correct *direction* on all six hypotheses (vs. lanthanide, where H2 was flatly "cannot determine"). But it **measured zero effect sizes.** Every number that makes this a paper — OR=0.49 core depletion, 2.7× clinical/environmental ratio, COG-V 7.05× enrichment, AlphaEarth diversity ρ=0.466, per-genus AMR density — is lakehouse-only. Outside, each was either lifted from a single non-uniform study or explicitly flagged as a domain estimate.

2. **Where the agent *did* give magnitudes, they were materially wrong — because a literature number isn't the right number for this dataset.** For H1 it estimated the pangenome core fraction at ~10–15% and AMR depletion at ~2–5×. The lakehouse *measured* a 46.8% baseline, 30.3% AMR-core, ~1.5× depletion (OR=0.49). The agent's estimate came from *E. coli* open-pangenome papers, a different construction than GTDB species-clade pangenomes — so it was off by ~3× on the baseline and overstated the depletion. "You can get a number from the literature" ≠ "you can get the right number for these genomes."

3. **H6 is the AMR analog of lanthanide's "soil, not volcanoes."** The textbook prior is "resistance carries a fitness cost," and that is exactly the verdict the no-lakehouse agent defaulted to (chromosomal ~21% cost, plasmid ~9%, citing Vogwill & MacLean 2015). The lakehouse's **direct measurement contradicts it** for the population in question: across 178 AMR genes in 37 Fitness Browser organisms (29,386 measurements), AMR genes show *slightly less* cost than baseline (median −0.007 vs −0.012, p=3.7×10⁻⁶) — essentially neutral, even slightly beneficial. The agent actually *intuited* this ("most accessory AMR genes would show fitness ≈ 0") but, unable to run the measurement, hedged back to the textbook cost figure as its headline. Only the fitness×pangenome join settles it.

4. **The lakehouse's real contribution is the *integration*, not any single table.** The one thing the agent said it lacked, over and over, was a uniform `annotation × conservation × environment × fitness` matrix. Notably, the raw inputs are largely *public* — the Fitness Browser data exists (the agent was just blocked by a 403; I confirmed the site refuses scripted access), CARD/AMRFinderPlus are open. What's missing outside is the **pre-built join** (e.g. the lakehouse's 177,863-link DIAMOND Fitness-Browser↔pangenome table). The lakehouse is load-bearing as an *integration layer*, which is a stronger and more general claim than "it has private data."

5. **Graceful again, not dangerous.** ~12 numeric claims grounded in cited sources, ~4 explicitly flagged as estimates, **0 covert fabrications.** The agent refused to manufacture CIs/ORs it couldn't support.

---

## Method (controlled ablation)

Identical design to Study 1. Subject = a fresh Claude subagent (same model family; only data access removed; never saw the original REPORT). Web was allowed and the prompt **explicitly pointed it at the strong public AMR resources** (CARD, ResFinder, AMRFinderPlus/NDARO, the Fitness Browser) — this steelmans the no-lakehouse arm as hard as possible. Contamination guard: forbidden from any BERIL/observatory/"Pan-Bacterial AMR" material. Judge = this analysis (read the ground-truth REPORT; independently confirmed the Fitness Browser blocks scripted access, 403). Subject prompt in `SUBJECT_PROMPT.md`; subject output in `no_lakehouse_REPORT.md`. Caveats: not compute-matched; single run.

---

## Head-to-head by hypothesis

| | **Inside lakehouse** (ground-truth REPORT, 83,008 AMR hits / 14,723 species) | **Outside lakehouse** (public web incl. CARD/AMRFinderPlus) | **Lakehouse load-bearing?** |
|---|---|---|---|
| **H1** AMR enriched in accessory genome | **Supported, measured.** AMR 30.3% core vs 46.8% baseline, **OR=0.49**, χ²=23,117, p≈0; paired 4,252 species, 63.7% less-core (Wilcoxon p=1.1×10⁻¹³⁰). | **Direction supported, magnitude wrong.** Estimated baseline ~10–15%, depletion ~2–5× (from *E. coli* lit) — both off; flagged low-confidence. | **Yes** — owns the effect size; the public-literature estimate was ~3× off on the baseline. |
| **H2** concentrated in clinical lineages + openness | **Supported, measured.** Klebsiella **206** AMR clusters/sp, Salmonella 198; Gammaproteobacteria **45%** of all AMR clusters; openness ρ=0.219 (Bacillota, p=1×10⁻¹⁶). | **Direction supported.** Proteobacteria 66.3% / Firmicutes 20.4% (one synthesis); Klebsiella median 4 vs 1. Openness coefficient: cannot determine. | **Yes** for the uniform per-lineage densities + openness ρ; direction was reachable publicly. |
| **H3** functional enrichment (defense/transport) | **Supported, measured.** COG V (defense) **7.05×** (14.9% vs 2.1%); COG P (ion transport) 1.93×; COG J 1.50×. | **Concept supported (Makarova 2011 defense islands); AMR-specific effect size cannot determine.** | **Yes** — the AMR-specific enrichment statistic is lakehouse-only. |
| **H4** clinical carry more / more-acquired AMR | **Supported, measured.** Clinical **10.6** AMR/sp vs soil 4.6 (**2.7×**); clinical less-core 30.8% vs soil 58.1%; AlphaEarth env-diversity **ρ=0.466** (p=1.6×10⁻¹⁴⁴). | **Direction supported** (env ARGs ~21% identity to clinical refs; clinical accumulate plasmid AMR). No densities/ratios. Correctly flagged the metal-resistance scope caveat. | **Yes** — every density/ratio + the AlphaEarth result is lakehouse-only. |
| **H5** "AMR-only" annotation-poor clusters | **Measured.** 93% have 2 annotation sources, 7% Bakta-only; sparse clusters 55.4% singletons vs 34.6%; zero Pfam overlap. | **Principle supported** (dark-matter resistome real; 671 novel polar ARGs). Exact fraction estimated ~5–25% (low conf). | **Yes** — the actual fraction is a join the agent couldn't run. |
| **H6** AMR genes impose a fitness cost | **Refuted for this population (surprise).** 178 AMR genes / 37 FB orgs / 29,386 measurements: AMR median fitness **−0.007 vs −0.012** baseline (p=3.7×10⁻⁶) — *less* cost, near-neutral. | **Textbook verdict: cost is real.** Chromosomal 0.79 (~21%), plasmid 0.91 (~9%), mono-plasmid ~1.02 (≈0), citing Vogwill & MacLean 2015. Intuited neutrality but hedged to the cost figure. | **Yes — decisively.** The prior says "cost"; the data says "neutral." Only the fitness×pangenome join (177,863-link table) resolves it. |

---

## The two cross-cutting results

**(a) Direction ≠ magnitude.** This is the skeptic-proof headline. A capable agent with the best public AMR resources reproduced the *shape* of all six findings — but produced not a single defensible effect size, and where it estimated magnitudes (H1), it was ~3× off because public pangenome numbers come from a different data construction. The lakehouse's value is precise, uniform, dataset-consistent measurement.

**(b) Public priors can mislead, and only the integrated data corrects them (H6).** Just as lanthanide's H2 expectation (REE/volcanic) was overturned by the genome-scale test (soil), AMR's H6 expectation (cost of resistance) is overturned for the measured population (intrinsic AMR in environmental FB organisms is neutral/beneficial). An analyst working from the literature alone would have reported "AMR is costly"; the lakehouse measurement says otherwise for exactly the accessory genes this study cares about.

---

## Groundedness / honesty tally (no-lakehouse arm)

| Category | Count |
|---|---|
| Numeric claims grounded in a cited source | ~12 |
| Numeric claims explicitly flagged "estimate — not verified" | ~4 (H1 baseline/ratio, H2 openness coeff, H5 AMR-only fraction) |
| Covert fabrications | **0** |
| Effect sizes/CIs refused rather than invented | H1 OR, H2 openness ρ, H3 AMR enrichment, H4 densities, H5 fraction |

Same well-behaved pattern as Study 1: honest about what it could not compute. It also independently surfaced the correct, important caveat that AMRFinderPlus's broad scope (mercury/arsenic/biocide genes) inflates "AMR" counts — which the lakehouse REPORT also flags.

---

## How this complements Study 1 (lanthanide)

| | **Study 1 — lanthanide** (no public substitute) | **Study 2 — AMR** (rich public data) |
|---|---|---|
| Could the agent get *direction*? | Only partly (H2 = cannot determine at all) | Yes, on all six |
| Could the agent get *effect sizes*? | No | No |
| Public prior overturned by the data | H2: soil, not volcanoes | H6: neutral, not costly |
| Main lakehouse contribution | The data itself (293K-genome scan) | The **integration** (annotation×conservation×environment×fitness join) |

**Together they bracket the argument:** the lakehouse is load-bearing both when public data is *absent* (lanthanide) and when it is *abundant* (AMR). In the abundant case it wins not by hoarding data but by being the integration layer that turns scattered public inputs into uniform, dataset-consistent effect sizes — and by catching where the public prior is simply wrong.

---

## Conclusion

Re-running `amr_pangenome_atlas` outside the lakehouse **does not crash and does not produce nothing** — a capable agent with CARD/AMRFinderPlus/literature recovers the qualitative story. But it cannot measure a single effect size, gets the one magnitude it estimates ~3× wrong, and returns the textbook "AMR is costly" verdict that the lakehouse's own fitness data refutes. The lakehouse is load-bearing as the **integration and measurement layer**, which is the harder and more valuable claim.

## Recommended next steps

1. **Use H6 as the flagship demo for a talk:** "the literature says resistance is costly; our integrated fitness×pangenome data says it's neutral for environmental intrinsic AMR." It's a crisp, counterintuitive, integration-only result.
2. If continuing the series, the natural third axis is a **pure-integration / dark-matter** job (e.g. `functional_dark_matter`), where even *direction* is unreachable outside.
3. Optional: re-run H6 inside the lakehouse split by acquired vs intrinsic / clinical vs environmental, to show explicitly where (if anywhere) the textbook cost reappears.
