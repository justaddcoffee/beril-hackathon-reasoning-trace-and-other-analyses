# The Genomic Landscape of Antimicrobial Resistance Across Bacteria

**An independent co-scientist attempt using only public resources (no curated genome-scale lakehouse)**

Date: 2026-05-28
Author: AI co-scientist (Claude)

---

## Preamble: what this report is and is not

I was asked to test six pre-registered hypotheses about the pan-bacterial genomic landscape of antimicrobial resistance (AMR) genes. I did **not** have access to any curated, genome-scale matrix of `annotation x conservation x environment x fitness` (e.g. a BERDL/KBase-style pangenome lakehouse, a precomputed AMR-by-cluster table, etc.). Those resources, per the task constraints, do not exist for me.

So this is a hybrid effort. Where a public resource lets me pull or recall a **real number with a citable source**, I do so and label it. Where the honest answer is a domain estimate, I label it **"estimate from my own knowledge — not verified"**. Where the hypothesis genuinely requires a uniform genome-scale dataset that no public review or single database provides at the needed granularity, I say **cannot determine** and explain exactly which data object would have been required.

**Confidence tagging convention** used throughout: each quantitative claim gets `[source; confidence: high/medium/low]`.

A key conceptual caveat that recurs below: the standard "AMR gene" annotation tool, **NCBI AMRFinderPlus** and its **Reference Gene Catalog** (Feldgarden et al. 2021), uses a *broad* definition of AMR that includes ~210 stress-response genes — biocide, heat, acid, and especially **metal resistance (mercury, arsenic, etc.)**. This broad scope materially changes the verdicts on several hypotheses (notably H1, H3, H4), and I flag it where relevant.

---

## 1. Per-hypothesis findings

### H1 — Conservation: AMR genes are enriched in the accessory genome vs the core genome

**Verdict: SUPPORTED (qualitatively and by mechanism), but I cannot give a clean genome-scale AMR-core-fraction vs pangenome-core-fraction effect size without curated data.**

What I can ground:

- **The overall bacterial pangenome is mostly accessory, not core.** For *E. coli*, the core genome at ~20 genomes was ~1,976 genes, roughly **11% of the pangenome** at that sampling; the soft-core (~95% of strains) stabilizes near ~3,000 gene families while the pangenome is estimated at ~25,000 gene families — i.e. core is on the order of **~10–15% of the pangenome** for an open-pangenome species. `[Tettelin-type / E. coli pangenome literature, link below; confidence: high for E. coli, medium as a generalization]`
- **AMR genes acquired by horizontal gene transfer (HGT) are, by construction, accessory.** Plasmid-, integron-, and transposon-borne resistance genes are present in only a subset of isolates of a species — that is the definition of accessory. Reviews and pangenome studies repeatedly localize acquired AMR genes to the accessory/flexible genome and to mobile genetic elements (MGEs). `[Neisseria gonorrhoeae pangenome study; Crofts 2017; confidence: high]`

The quantitative comparison the hypothesis actually asks for is:
> AMR core fraction (what % of AMR gene clusters are core) vs the genome-wide / pangenome-wide core fraction.

My best **estimate** of the contrast, reasoning from mechanism rather than a uniform measurement:

- Genome-wide / pangenome-wide core fraction (fraction of all gene clusters that are core): order **~10–40%** depending on species and how many genomes are sampled (open pangenomes lower, closed pangenomes higher). `[derived from pangenome literature above; confidence: medium]`
- AMR-gene core fraction: **substantially lower** than that, because the *acquired* resistome is dominated by mobile, sporadically distributed genes. I would estimate the acquired-AMR core fraction in the **single-digit to low-double-digit percent** range for a clinically diverse species. `[estimate from my own knowledge — not verified; confidence: low–medium]`
- **Important counterweight:** some "AMR" determinants are core or near-core housekeeping genes — e.g. intrinsic chromosomal efflux pumps (AcrAB-TolC in *E. coli*), intrinsic/species-defining beta-lactamases (e.g. *ampC*-like, the chromosomal *bla* genes that define some species), and target genes carrying resistance point mutations (*gyrA*, *rpoB*, *rrs*). Because AMRFinderPlus reports point mutations in core genes as resistance determinants, a naive "AMR cluster" tally will include some genuinely **core** members. This blunts the effect size but does not reverse the direction. `[Feldgarden 2021; confidence: high]`

**Effect-size statement (best I can responsibly give):** the AMR (acquired) core fraction is plausibly ~2–5x lower than the pangenome-wide core fraction, i.e. AMR genes are enriched in the accessory compartment. Direction is well supported; the precise ratio is an estimate, not a measured value. `[estimate; confidence: low for the exact ratio, medium-high for the direction]`

**What I could not do:** compute, over thousands of species with uniform clustering, `P(core | AMR)` vs `P(core | any gene)` with a confidence interval / odds ratio. That requires a curated pan-bacterial gene-cluster x species-occupancy matrix joined to an AMR flag — exactly the lakehouse object I was told I do not have.

---

### H2 — Phylogenetic distribution: AMR is concentrated in specific clinical lineages, not even across phyla; correlates with pangenome openness

**Verdict: SUPPORTED (strongly for the "concentrated in few phyla / lineages" claim; the openness correlation is plausible but I can only assert it qualitatively).**

Grounded numbers:

- **Acquired ARGs are concentrated in a handful of phyla.** Across a large host-survey analysis, ARGs were most common in **Proteobacteria (~66.3% on average)**, then **Firmicutes (~20.4%)**, with much lower shares in Actinobacteria (~8.4%), Bacteroidetes (~3.9%), Cyanobacteria (~0.22%), Chloroflexi (~0.18%). `[ARG host-phylogeny analysis, link below; confidence: medium-high — figures are from one synthesis, directionally consistent across the literature]`
- These two dominant phyla contain essentially all the **ESKAPE / Enterobacterales** clinical pathogens (Klebsiella, E. coli, Salmonella, Acinetobacter, Pseudomonas, Enterococcus, Staphylococcus). `[ESKAPE literature; confidence: high]`
- **Per-lineage AMR density (real number):** *Klebsiella* isolates carried a **median of 4 acquired AMR genes (range 1–18)** vs a **median of 1 (range 0–23)** in other Enterobacteriaceae in a One-Health genomic survey — a concrete demonstration that even within one family, density varies by lineage/niche. `[Klebsiella One-Health genomics study, link below; confidence: medium-high]`

Openness correlation:

- *Klebsiella pneumoniae* is described as having an **open pangenome** with high plasmid burden and the highest AMR-gene diversity among the Gram-negative opportunists — consistent with the hypothesized "openness correlates with AMR" pattern. `[Klebsiella trafficker review; confidence: medium]`
- The mechanistic logic is sound: lineages with high HGT/MGE traffic have both more open pangenomes *and* more acquired AMR, so a positive correlation is expected. But I have **not** computed a per-species (pangenome-openness parameter alpha/gamma from Heap's law) vs (AMR density) regression. That correlation coefficient is **cannot determine** at the quantitative level. `[estimate of direction; confidence: medium for direction, none for a coefficient]`

**Net:** "concentrated in specific lineages, not even across phyla" is **supported** with real per-phylum and per-lineage numbers. The openness↔AMR correlation is **directionally supported / quantitatively cannot-determine**.

---

### H3 — Functional context: AMR clusters are enriched near defense systems, membrane/ion transport, and cell-wall biosynthesis ("defense islands")

**Verdict: PARTIALLY SUPPORTED — strong, well-established mechanistic and qualitative support; I cannot supply a clean genome-scale functional-category enrichment statistic for AMR specifically.**

What is solidly grounded:

- **"Defense islands" are real and statistically demonstrated.** Makarova, Wolf, Snir & Koonin (2011, J Bacteriol) showed *statistically significant clustering* of antivirus defense systems (restriction-modification, toxin-antitoxin) and mobilome components in genomic islands across bacteria and archaea (CRISPR-Cas being a partial exception). `[Makarova et al. 2011, link below; confidence: high]`
- **Acquired AMR genes co-localize with MGEs**, which themselves co-localize with and carry anti-defense / defense functions; resistance genes, defense genes, and mobility genes are repeatedly found together on the same plasmids / integrative elements. The "leading region" of conjugative plasmids is enriched for anti-defense genes, and AMR cargo rides the same elements. `[MGE / anti-defense island reviews, links below; confidence: medium-high]`
- **Membrane/ion transport and cell-wall biosynthesis are mechanistically intrinsic to resistance:** efflux pumps (RND/MFS transporters), porin modifications (membrane transport), and cell-wall/peptidoglycan and LPS modification enzymes (e.g. *mcr* phosphoethanolamine transferases for colistin, *van* operons for vancomycin, PBP variants) are themselves resistance mechanisms. So AMR being "functionally near" transport and cell-wall biosynthesis is partly a *definitional* truth, not just a colocalization signal. `[AMR mechanism literature / CARD ontology; confidence: high]`

The specific quantitative claim ("AMR clusters are functionally enriched near defense systems vs functionally isolated") requires a genome-scale **gene-neighborhood enrichment analysis**: for each AMR cluster, take its genomic neighbors, assign functional categories (COG/Pfam/KEGG), and test enrichment vs a genomic background. I cannot run that without the curated cluster-coordinate-plus-functional-annotation dataset.

**Net:** the *direction* (AMR is embedded in mobile, defense-/transport-/cell-wall-rich neighborhoods, not isolated) is **supported** by named primary literature; the **enrichment effect size for AMR specifically is cannot-determine** from public reviews alone.

---

### H4 — Environmental signal: host-associated/clinical species carry more AMR, and more acquired (less-core) AMR, than environmental isolates

**Verdict: SUPPORTED for "clinical carry more acquired AMR"; the "less-core in clinical" sub-claim is mechanistically expected but I cannot quantify it; one important nuance argues for caution.**

Grounded points:

- **The environmental resistome is huge but largely intrinsic/divergent.** Soil is described as one of the largest environmental resistomes on Earth, but functional-metagenomic studies repeatedly find environmental resistance genes share **low sequence identity (~21% minimum in soil studies)** with clinical reference genes — i.e. environmental AMR is ancient, diverse, and mostly *not* the mobile, recently-acquired AMR seen clinically. `[functional-metagenomics resistome reviews, links below; confidence: medium-high]`
- **Clinical/host-associated lineages carry more *acquired* AMR.** The Klebsiella One-Health data (above) and the broad Proteobacteria/Firmicutes concentration both point this way: human- and animal-associated Enterobacterales accumulate plasmid-borne multi-drug cassettes. The soil↔human resistome "connectivity" has increased over time, consistent with mobile genes flowing into clinical hosts. `[soil↔human resistome connectivity study; Klebsiella study; confidence: medium]`
- **"Less core in clinical" is expected** precisely because clinical AMR is enriched in *acquired* (plasmid/transposon) genes, which are accessory, whereas an environmental organism's intrinsic resistance (e.g. a chromosomal beta-lactamase) is core *to that organism*. So acquired-vs-core composition should skew "more acquired / less core" in clinical isolates. This is the same direction as H1, and I can only state it qualitatively. `[estimate / mechanism; confidence: medium]`

**Important nuance / counter-signal:** because AMRFinderPlus counts **metal and biocide resistance (mercury, arsenic)** as "AMR," some *environmental* organisms (heavy-metal-rich soils, mining sites) can score high on "AMR gene" counts via metal-resistance operons, which inflates environmental AMR under the broad definition. The clinical>environmental gap is clearest when restricted to **drug** resistance genes, not the full AMRFinderPlus scope. `[Feldgarden 2021 scope; confidence: high for the scope fact, medium for its effect on this comparison]`

**What I could not do:** compute per-environment (host-associated vs environmental) mean AMR density and a formal "fraction-acquired" contrast across a balanced, metadata-tagged set of thousands of genomes. That needs genomes joined to standardized isolation-source/environment metadata plus AMR annotation — a curated lakehouse join I do not have.

---

### H5 — Annotation depth: a subset of AMR clusters are "AMR-only" (flagged as AMR but lacking other functional annotation) = novel/poorly-characterized resistance

**Verdict: SUPPORTED in principle (the "dark-matter resistome" is real and well-documented); I cannot give the exact fraction of *clusters* that are AMR-only without the curated cluster-x-annotation matrix.**

Grounded points:

- **A genuine "dark-matter resistome" exists.** Functional metagenomics routinely recovers resistance genes with **little-to-no similarity to known references** (e.g. ~21% minimum identity in soil; **671 novel polar ARGs** experimentally verified against multiple clinical antibiotics in one polar-soil study). These are functionally AMR but would be missed or left otherwise-unannotated by homology-based pipelines. `[functional-metagenomics reviews + polar-soil study, links below; confidence: medium-high]`
- **The AMRFinderPlus catalog itself is curated against many "hypothetical-protein"-like families;** many AMR families have minimal additional functional annotation beyond the resistance call, which is exactly the "AMR-only" pattern the hypothesis predicts. `[Feldgarden 2021 / NCBI Reference Gene Catalog; confidence: medium]`

The exact quantity requested — *the fraction of AMR clusters that are annotation-poor (AMR flag but no other functional annotation)* — is a property of a specific clustered dataset (how clusters are defined, which annotation sources are joined). Different pipelines will give wildly different fractions. My **order-of-magnitude estimate** is that a **non-trivial minority — roughly 5–25%** — of AMR-flagged clusters in a homology-based pan-bacterial annotation would lack rich orthogonal functional annotation, concentrated in the environmental/novel tail. `[estimate from my own knowledge — not verified; confidence: low]`

**What I could not do:** join an AMR-cluster list to a full functional-annotation table and count clusters with `AMR_flag = TRUE AND other_annotation = NULL`. That is a single SQL-style join on the curated matrix I do not have.

---

### H6 — Fitness cost: AMR genes impose a measurable fitness cost in standard lab conditions

**Verdict: PARTIALLY SUPPORTED / NUANCED — chromosomal resistance mutations carry a clear, measurable cost; acquired AMR *genes* (the kind that are accessory, per H1) often carry small-to-negligible cost in lab conditions. So the cost is real but smaller and more variable for exactly the accessory genes this study cares about.**

Grounded numbers (this is my strongest real effect size):

- **Meta-analysis of 77 papers / 822 resistant mutants** (Vogwill & MacLean 2015, the "genetic basis of fitness costs" meta-analysis): mean **relative fitness 0.79 ± 0.024 for chromosomal resistance mutations** (≈ 21% cost) vs **0.91 ± 0.024 for plasmid-acquired resistance** (≈ 9% cost); difference significant (P < 0.005). Restricting to **mono-resistant plasmids, mean fitness ≈ 1.02 (± 0.112)** — i.e. **no detectable cost** for a single acquired resistance gene on its own. `[Vogwill & MacLean 2015 meta-analysis, link below; confidence: high]`
- **A 13-gene multidrug-resistance plasmid (pUUH239.2) reduced fitness by ~2.9% per generation**, and the cost was traced to specific gene clusters, not all 13 genes equally. `[plasmid fitness-cost study, link below; confidence: medium-high]`
- **General framing** (Andersson & Hughes 2010, Nat Rev Micro): most *resistance mutations* reduce fitness, but costs are frequently **ameliorated by compensatory mutations**, and some determinants are cost-free. `[Andersson & Hughes 2010; confidence: high]`

RB-TnSeq / Fitness Browser:

- The **Fitness Browser** (Price/Deutschbauer/Arkin, fit.genomics.lbl.gov) holds genome-wide RB-TnSeq fitness data for **dozens of bacteria across thousands of conditions**, where a negative gene-fitness value = the gene is important for fitness in that condition and a value near 0 = no measurable effect. `[Fitness Browser / Wetmore 2015 RB-TnSeq methodology; confidence: high for what the resource is]`
- **I could not pull a specific AMR-vs-non-AMR fitness contrast from the Fitness Browser**: the site blocks automated fetching (HTTP 403 / robots.txt disallow), so I could not programmatically query, e.g., the mean fitness of efflux/resistance genes vs all genes under no-antibiotic conditions. `[direct fetch attempt failed; confidence: high that I was blocked]`. Conceptually, RB-TnSeq measures *gene importance*, not *cost of carriage of an acquired plasmid gene*, so it is not a perfect instrument for this hypothesis anyway: most accessory AMR genes are non-essential and would show fitness ≈ 0 (neutral) in standard conditions, which is *consistent with* low carriage cost.

**Net:** The hypothesis ("AMR genes impose a measurable cost, consistent with accessory status") is **supported for chromosomal-mutation resistance (~21% cost)** but only **weakly/variably supported for acquired AMR genes (~0–9% cost, often not significant individually)**. The honest reading actually *strengthens* the H1 logic: acquired AMR genes are accessory and near-neutral when antibiotics are absent, which is why they are conditionally retained rather than fixed.

---

## 2. Methods — what I actually did

**Resources I queried (web/literature):**
- NCBI AMRFinderPlus / Reference Gene Catalog paper (Feldgarden et al. 2021, *Sci Rep*) — pulled exact catalog composition: **6,428 total genes = 5,588 AMR + 210 stress (2 acid, 52 biocide, 8 heat, 148 metal) + 630 virulence**, 627 HMMs, 682 point mutations; AMR genes cover 31 drug classes. This grounds H5 and the broad-scope caveat affecting H1/H3/H4.
- Makarova, Wolf, Snir & Koonin 2011 (*J Bacteriol* 193:6039–6056) — defense-islands "guilt-by-association" clustering — grounds H3.
- Vogwill & MacLean 2015 fitness-cost meta-analysis (77 papers / 822 mutants) and Andersson & Hughes 2010 review, plus the pUUH239.2 plasmid study — grounds H6.
- Klebsiella One-Health genomic surveys (median 4 vs 1 acquired AMR genes) and an ARG host-phylogeny synthesis (Proteobacteria 66.3% / Firmicutes 20.4%) — grounds H2.
- E. coli / Tettelin-type pangenome literature (core ≈ 10–15% of pangenome, open pangenome ~25,000 gene families) — grounds H1.
- Functional-metagenomics resistome reviews + polar-soil study (671 novel ARGs; ~21% min identity) and a soil↔human resistome connectivity study — ground H4 and H5.

**What I computed vs estimated:** I did not run a bespoke statistical computation over genomes (I had no genome-scale matrix). Every "number" above is either (a) lifted from a named publication, or (b) explicitly labeled an estimate from domain knowledge. I performed live web searches/fetches; one direct database fetch (Fitness Browser) was blocked by the server.

**What I could NOT obtain without curated genome-scale data:**
- A uniform pan-bacterial gene-cluster x species-occupancy matrix to compute AMR-core-fraction vs pangenome-core-fraction with an effect size and CI (H1).
- A per-species pangenome-openness vs AMR-density regression coefficient (H2).
- A gene-neighborhood functional-enrichment statistic for AMR clusters vs genomic background (H3).
- A balanced, metadata-tagged environment-vs-clinical AMR-density and fraction-acquired contrast (H4).
- The exact fraction of AMR clusters that are "AMR-only / annotation-poor" from a real cluster-x-annotation join (H5).
- A direct AMR-vs-non-AMR RB-TnSeq fitness contrast under no-drug conditions (H6) — both because the Browser blocked automated access and because RB-TnSeq measures gene importance, not plasmid-carriage cost.

---

## 3. Limitations — where I guessed and where curated data was required

1. **The "AMR gene" definition is not fixed.** My verdicts shift depending on whether "AMR" means *drug* resistance only or the broad AMRFinderPlus scope (which includes mercury/arsenic/biocide). I flagged this for H1, H3, H4. A curated resource would let me re-run each hypothesis under both definitions; I could only reason about the direction of the bias.
2. **Single-source numbers.** The cleanest per-phylum figures (Proteobacteria 66.3% / Firmicutes 20.4%) and the per-lineage Klebsiella medians come from individual studies with their own sampling biases (clinical over-representation, database composition). I treated them as directional, not canonical, and capped confidence at medium-high.
3. **Estimates clearly labeled.** The AMR-core-fraction ratio (H1, ~2–5x), the openness↔AMR coefficient (H2, none), and the AMR-only cluster fraction (H5, ~5–25%) are domain estimates, not measurements. I assigned them low confidence and did not dress them up as precise statistics.
4. **No CIs / no hypothesis tests of my own.** Because I had no row-level data, I could not attach confidence intervals, odds ratios, or p-values to *my* claims (only to claims I cited). A genome-scale `annotation x conservation x environment x fitness` matrix is precisely what would let an analyst compute all six effect sizes with proper statistics in one place — that single joined object is the load-bearing thing I lacked.
5. **Live-data access gaps.** The Fitness Browser blocked automated queries, so H6's RB-TnSeq component rests on the published meta-analysis rather than a fresh extraction.

### Source links
- AMRFinderPlus / Reference Gene Catalog (Feldgarden 2021): https://pmc.ncbi.nlm.nih.gov/articles/PMC8208984/
- Defense islands (Makarova et al. 2011): https://pmc.ncbi.nlm.nih.gov/articles/PMC3194920/ and https://journals.asm.org/doi/10.1128/jb.05535-11
- Fitness-cost meta-analysis (Vogwill & MacLean 2015): https://pmc.ncbi.nlm.nih.gov/articles/PMC4380922/
- Andersson & Hughes 2010 (cost / reversibility): https://www.nature.com/articles/nrmicro2319
- pUUH239.2 multiresistance-plasmid fitness cost: https://pmc.ncbi.nlm.nih.gov/articles/PMC8764527/
- Klebsiella One-Health genomics (median AMR per genome): https://www.thelancet.com/journals/lanmic/article/PIIS2666-5247(23)00208-2/fulltext
- Klebsiella as trafficker of resistance genes: https://www.sciencedirect.com/science/article/pii/S1369527418300225
- Neisseria gonorrhoeae accessory genome & AMR: https://pmc.ncbi.nlm.nih.gov/articles/PMC9241924/
- E. coli pangenome structure / openness: https://journals.asm.org/doi/10.1128/jb.00619-08
- Soil↔human resistome connectivity: https://www.nature.com/articles/s41467-025-61606-3
- Functional-metagenomics novel resistome / dark matter: https://pmc.ncbi.nlm.nih.gov/articles/PMC3675766/ and polar soils: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12371247/
- Fitness Browser (Price/Deutschbauer/Arkin): https://fit.genomics.lbl.gov/ (RB-TnSeq method: Wetmore et al. 2015)

---

## Summary table

| Hyp | Claim | Verdict | Best grounded number | Confidence |
|-----|-------|---------|----------------------|------------|
| H1 | AMR enriched in accessory genome | Supported (direction) | pangenome core ≈10–15%; acquired-AMR core estimated ~2–5x lower | med (dir) / low (ratio) |
| H2 | AMR concentrated in clinical lineages | Supported | Proteobacteria 66.3%, Firmicutes 20.4%; Klebsiella median 4 vs 1 AMR genes | med-high |
| H3 | AMR near defense/transport/cell-wall islands | Partially supported | defense-island clustering statistically significant (Makarova 2011) | high (concept) / cannot-determine (AMR effect size) |
| H4 | Clinical carry more / more-acquired AMR | Supported (w/ metal-scope caveat) | env ARGs ~21% identity to clinical refs; clinical lineages accumulate plasmid AMR | medium |
| H5 | Subset of AMR clusters are annotation-poor/novel | Supported (principle) | 671 novel verified polar ARGs; AMR-only fraction estimated ~5–25% | med (concept) / low (fraction) |
| H6 | AMR genes impose measurable lab fitness cost | Partially / nuanced | chromosomal 0.79 (~21% cost); plasmid 0.91 (~9%); mono-plasmid ~1.02 (≈0) | high |
