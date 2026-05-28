# Phylogenomic distribution and cassette-completeness of the lanthanide-dependent methanol/ethanol oxidation system

## Bottom line

*Added 2026-05-28 after comparing this no-lakehouse run against the original in-lakehouse BERIL run. Everything below this section is the original no-lakehouse report, written by an agent that had no access to the lakehouse or to the in-lakehouse results. See `REPORT_COMPARISON.md` for the full head-to-head.*

**Does the BERDL data lakehouse (plus the BERIL skills) help? Yes — decisively.** The same scientific question was run two ways: once inside the lakehouse against 293K genomes, and once here with the lakehouse removed but full public-web access allowed (papers, KEGG, UniProt, GTDB). The lakehouse is what turns this from a literature opinion into a measured result.

| Hypothesis | In-lakehouse BERIL run (293K genomes) | This no-lakehouse ablation (public web only) |
|---|---|---|
| **H1** — xoxF ≥10× more common than mxaF | **Supported (strongly).** xoxF:mxaF = **18.9:1**, p=7.6×10⁻²²; phylogeny-corrected ~143:1. | **Not supported at the ≥10× bar.** Public data give only **~2–6:1**. The *direction* (xoxF > mxaF) is confirmed; the *magnitude* is not. |
| **H2** — cassette enriched in REE/mineral environments | **Partially supported — but NOT as predicted.** The real enrichment is in **soil/sediment (OR=1.92)** and marine; the *expected* REE/volcanic/mining sites were **not** significant (volcanic OR=0.86, mining OR=1.12 ns, REE-impacted underpowered). Host-associated strongly depleted (OR=0.058). | **Cannot determine.** Only one-sided anecdotes; no denominators, no controls, no odds ratios. Would likely have concluded "enriched in REE/volcanic sites" — i.e. **backwards**. |
| **H3a** — lanmodulin clade-restricted | **Supported (strongly).** Lanmodulin in **62/62 = 100%** of genomes within three α-proteobacterial methylotroph families, p=9.8×10⁻⁷. | **Direction only.** Lanmodulin is α-proteobacterial, but the exact three-family boundary could not be quantified (public surveys extend it). |
| **H3b** — lanmodulin co-occurs with xoxF ≥80% | **Not formally supported.** Co-occurrence = **79%** (49/62), just under the 80% threshold. | **Cannot compute.** The agent *guessed* ~90% — the wrong side of the true 79%. |

**The takeaway:** outside the lakehouse, a capable agent with the whole internet could recover the qualitative *direction* of H1 and H3a, but could not produce a single effect size, denominator, or phylogenetically-controlled statistic for *any* hypothesis — and would have gotten H2 exactly backwards (anecdotes point to REE/volcanic; the genome-scale test shows the real signal is mundane soil). Every headline number that makes this a paper (18.9:1, OR=1.92, 100%, 79%) is lakehouse-only. The failure outside was *graceful* (the agent admitted what it couldn't compute rather than fabricating), but the job still cannot be done without the curated, genome-scale data.

**One caveat the ablation surfaced (and that strengthens the case for careful curation):** the in-lakehouse xoxF marker is KEGG **K00114**, which is officially `exaA` (a broad cytochrome-c alcohol dehydrogenase, EC 1.1.2.8), *not* the canonical xoxF ortholog **K23995** (EC 1.1.2.10). The 18.9:1 ratio should be re-checked inside the lakehouse with the tighter K23995 definition. The lakehouse is load-bearing — and only as good as its marker definitions.

---

**No-lakehouse arm.** This report was produced WITHOUT access to the BERDL data lakehouse, K-BERDL, KBase, or any pre-computed pangenome annotation matrix. It relies only on (a) my own domain knowledge and (b) public databases and literature I queried live (KEGG REST API, UniProt REST API, and published peer-reviewed surveys). No "BERIL", "observatory", "Discovery Forge", or "lanthanide methylotrophy atlas" analysis was consulted.

**Author:** AI co-scientist
**Date:** 2026-05-28

---

## 0. Critical preliminary: the KEGG identifiers in the hypotheses are mis-mapped

Before reporting findings, I have to flag a data-integrity issue that affects how the hypotheses should be read. The pre-registration assigns:

- xoxF -> **K00114**
- mxaF -> **K14028**

I checked both against the live KEGG REST API. They do **not** match the stated genes:

| KO queried | Actual KEGG symbol / definition (KEGG REST `get`) | Source / confidence |
|---|---|---|
| **K00114** | `exaA` -- alcohol dehydrogenase (cytochrome c) [EC:1.1.2.8]. NOT xoxF. | KEGG REST `https://rest.kegg.jp/get/K00114`, queried live. Confidence: high |
| **K14028** | `mdh1`, `mxaF` -- methanol dehydrogenase (cytochrome c) subunit 1 [EC:1.1.2.7]. This one IS mxaF. | KEGG REST `https://rest.kegg.jp/get/K14028`, queried live. Confidence: high |
| **K23995** (the correct xoxF KO) | `xoxF` -- lanthanide-dependent methanol dehydrogenase [EC:1.1.2.10]. | KEGG REST `https://rest.kegg.jp/get/K23995`, queried live. Confidence: high |

So the canonical lanthanide-dependent methanol dehydrogenase ortholog in KEGG is **K23995 (xoxF)**, and **K00114 is a different, broader periplasmic alcohol dehydrogenase (exaA/PedH-like family)**. I therefore answer H1 using **K23995 vs K14028**, which is the biologically intended comparison, and separately report what the literally-specified KOs give. A curated lakehouse with a validated KO->gene crosswalk would have caught this automatically; here it required a manual sanity check.

---

## 1. Per-hypothesis findings

### H1 -- xoxF dominance (xoxF genome-frequent at >=10x mxaF)

**What I could compute directly (real queries):**

KEGG `link` counts of gene entries per KO (these count gene members across KEGG's curated genome set, not all sequenced genomes):

| KO | Symbol | KEGG gene-member count | Source / confidence |
|---|---|---|---|
| K23995 | xoxF (Ln-MDH) | **648** | `https://rest.kegg.jp/link/genes/K23995` \| wc -l, queried live. Confidence: high (raw count); medium (as a genome-frequency proxy) |
| K14028 | mxaF (Ca-MDH) | **122** | `https://rest.kegg.jp/link/genes/K14028` \| wc -l, queried live. Confidence: high (raw count) |
| K00114 | exaA (the mis-mapped "xoxF") | 1110 | `https://rest.kegg.jp/link/genes/K00114`, queried live. Confidence: high |

**KEGG-based xoxF:mxaF gene-count ratio = 648 / 122 = 5.3.** (Source: arithmetic on the two live KEGG queries above. Confidence: high for the ratio of KEGG members; medium that it reflects true genome frequency, because KEGG's genome panel is curated and model-organism-biased.)

**Cross-check against published genome-scale surveys:**

- Huang et al. 2019 (PMC6775964, "Rare earth element alcohol dehydrogenases widely occur...") report, within Proteobacteria, **738 XoxF5 genes vs 254 MxaF genes** -> ratio **~2.9x** at the gene level. Source: paper text, fetched live. Confidence: high (these are the authors' reported numbers).
- Diversity-of-the-lanthanome 2025 (PMC12482762), 179 aerobic methane-oxidising bacteria genomes: **288 xoxF copies vs 154 mxaF copies** -> ratio **~1.9x** at the copy level; and 175/179 genomes carried at least one MDH. Note xoxF is frequently multi-copy per genome while mxaF is single-copy, which inflates copy ratios relative to genome-presence ratios. Source: paper text, fetched live. Confidence: high.
- The qualitative literature consensus (Pol et al. 2014 Environ. Microbiol.; Skovran & Martinez-Gomez 2015; Chistoserdova 2016; Picone & Op den Camp 2019) is that XoxF-type MDH is "much more prominent in nature than MxaF-type." Source: review literature. Confidence: high (as a qualitative statement).

**Phylogenetic-independence test:** I could **not** perform a proper phylogenetically-controlled test (e.g. presence/absence on a GTDB tree with a phylogenetic GLM / `phyloglm`, or sister-clade contrasts). That requires a per-genome presence/absence matrix mapped onto a species tree, which is exactly the genome-scale curated resource I do not have. The published ratios above are themselves **not** phylogeny-corrected; they pool genes across genomes, and a large share of mxaF is concentrated in a few well-sampled methylotroph genera (Methylobacterium, Methylophilaceae), so the raw ratio is confounded by sampling density.

**Verdict on H1: NOT SUPPORTED at the >=10x threshold (as best I can determine).** Every real, source-grounded estimate I can produce puts the xoxF:mxaF ratio in roughly the **2x to 5x** range (KEGG members 5.3x; Huang 2.9x; lanthanome 1.9x), not >=10x. The direction of H1 (xoxF > mxaF) is well supported and robust; the **magnitude** claim (>=10x) is not supported by any number I can ground. Plausible interval for the genome-level ratio: **~2x to ~6x** (confidence: medium). H0 (indistinguishable rates) is rejected -- xoxF is clearly more frequent -- but the specific 10x effect size is rejected too. A caveat: KEGG/AnnoTree counts only annotated genomes, and a sweep over all sequenced genomes (incl. uncultured MAGs) could shift this; I cannot rule out that in MAG-heavy datasets the ratio is higher, but I have no number to support >=10x.

---

### H2 -- Environmental enrichment of the full Ln-MDH cassette (xoxF + xoxJ + >=1 PQQ gene)

**What I could establish:**

- The full cassette concept is real and the components co-localise: xoxF sits in a genomic neighborhood with xoxJ (a periplasmic cytochrome/binding protein, the putative electron acceptor for XoxF) and PQQ-biosynthesis genes (pqqABCDE). Source: Chistoserdova reviews; lanthanome 2025 paper (XoxJ upregulated under Ce/ore treatment, log2FC 2.16 Ce / 0.83 ore in M. trichosporium OB3b). Confidence: high (the cassette exists and is co-regulated by lanthanides).
- The founding environmental signal is strong and directionally consistent with H2: the first lanthanide-obligate methanotroph (Methylacidiphilum fumariolicum SolV) was isolated from a **volcanic mudpot** and is strictly REE-dependent (Pol et al. 2014, Environ. Microbiol., PMID 24034209 -- note the pre-registration cited "Nature" but the paper is in Environmental Microbiology). Methylacidimicrobium thermophilum AP8 likewise comes from acidic geothermal soil with elevated lanthanide concentrations (PMC7907005). A sedimentary-lanthanide-rich underground mine community yielded 8 xoxF genes / 14 XoxF protein hits by metagenomics+metaproteomics (PMC8999231). Sources fetched live. Confidence: high for each individual anecdote.

**What I could NOT compute:**

I could not produce **odds ratios per environment class**, and I could not do the matched case/control comparison H2 requires. That test needs: (1) a per-genome/per-sample full-cassette presence/absence call, joined to (2) structured environmental metadata (e.g. MIxS/GOLD ecosystem categories or IMG/M sample attributes) for **the same** genomes/samples, with (3) matched host-associated and generic-environmental controls, and (4) phylogenetic control. That is a genome-scale curated cross-product of annotation x environmental metadata -- precisely the lakehouse capability I do not have. Public single-genome and per-study papers give compelling **examples** of REE/volcanic/mine-drainage enrichment but no denominator and no control group, so no effect size can be honestly stated.

**Verdict on H2: CANNOT DETERMINE (quantitatively); qualitatively consistent with enrichment.** The directional evidence (volcanic, geothermal, REE-rich mine, lanthanide-amended methylotrophic media all yield cassette-bearing organisms) is real and one-sided, so I would not reject H2 -- but I cannot supply a single source-grounded odds ratio, cannot match controls, and cannot phylogeny-correct. Any numeric OR I wrote here would be invented. Best honest statement: **likely enriched, effect size unquantifiable without genome-scale annotation x metadata join.** Confidence: low (on the quantitative claim); medium (on the qualitative direction).

---

### H3 -- Lanmodulin clade restriction and xoxF co-occurrence

**What I could establish (real, source-grounded):**

1. **UniProt name-based count is uninformative.** A live UniProt query for "lanmodulin" returns only **2** entries (`https://rest.uniprot.org/uniprotkb/search?query=lanmodulin`, queried live; confidence high for the count). This is because LanM is almost never annotated by that name in UniProt -- it is a small EF-hand protein indistinguishable by keyword from calmodulin-like proteins. **This is itself a finding: you cannot survey LanM by gene/product name in public flat databases; it requires a profile-HMM / structural search over a genome set.** Confidence: high.

2. **Curated surveys give the real distribution.** In the lanthanome-of-MOB survey (PMC12482762, 179 genomes), genome-encoded LanM was found in **17 genomes, all Alphaproteobacteria** (2 Methylocella, 15 Methylocystis -- families Beijerinckiaceae and Methylocystaceae); plasmid-borne LanM appeared in 19 further sequences, dominated by **Bradyrhizobium (15)** plus Mesorhizobium, Methylobacterium nodulans, Methylorubrum. Source: paper, fetched live. Confidence: high.

3. **A dedicated LanM homolog search (Communications Biology 2024, s42003-024-07258-3) found 52 proteobacterial LanM homologs, predominantly Alphaproteobacteria, but extending beyond the three named families** -- into **Nitrobacteraceae (Bradyrhizobium, Tardiphaga, Rhodopseudomonas)** and **Hyphomicrobiaceae (Hyphomicrobium, Methyloligella)**, and notably **one actinobacterial hit (Streptomyces purpurogeneiscleroticus)**. Source: paper, fetched live. Confidence: high.

4. **A LanM-homolog in Mesorhizobium qingshengii J19** (a rhizobial N-fixer, family Phyllobacteriaceae -- not a classic methylotroph family) was characterised as involved in yttrium immobilisation (s41598-026-45294-7). I could read only the abstract/metadata, not the full text. Source: search result + metadata. Confidence: medium.

**On the >=80% xoxF co-occurrence sub-claim:** I could **not** compute the per-genome co-occurrence fraction, because that needs a LanM-call and an xoxF-call **on the same genome set**. The lanthanome paper notes all 17 genomic-LanM genomes are Alphaproteobacteria and that 56/60 of its Alphaproteobacterial MOB carried xoxF5, which makes co-occurrence "highly likely" but it is **not quantified** in the source. I will not state a fabricated co-occurrence percentage. (Estimate from my own knowledge - not verified: I would expect xoxF co-occurrence in LanM-bearing genomes to be very high, plausibly >=90%, because LanM's physiological role is to deliver lanthanide to the XoxF system; confidence: low.)

**Verdict on H3: PARTIALLY SUPPORTED / SPLIT.**
- "Restricted to a small set of clades": **Mostly supported but the specific three-family list is too narrow.** Genome-encoded LanM is overwhelmingly Alphaproteobacteria (e.g. 17/17 = 100% in the MOB survey), but the relevant alpha families include **Methylocystaceae and Nitrobacteraceae** in addition to Beijerinckiaceae/Acetobacteraceae/Hyphomicrobiaceae, and a stringent HMM search picks up at least one actinobacterial hit. So "taxonomically restricted to Alphaproteobacteria methylotrophs (broadly)" = supported; "restricted to exactly Beijerinckiaceae + Acetobacteraceae + Hyphomicrobiaceae" = not strictly supported. The fraction-inside-those-three-families is therefore **< 100%** (medium confidence) -- the survey data place some hits in Methylocystaceae/Nitrobacteraceae outside the named three.
- "Co-occurs with xoxF in >=80% of cases": **Cannot determine** with a real number; qualitatively very likely true.
- H0 (LanM diffuse and uncorrelated with xoxF) is **rejected** -- LanM is clearly not taxonomically diffuse and is mechanistically tied to xoxF.

---

## 2. Methods -- what I actually did

**Resources I queried live (real numbers in this report come from these):**

- **KEGG REST API** (`rest.kegg.jp`): `get/K00114`, `get/K14028`, `get/K23995`, `get/K16255`, and `link/genes/<KO> | wc -l` to count gene members. This gave the KO-to-symbol crosswalk (and caught the K00114 mis-mapping) and the 648 (xoxF) vs 122 (mxaF) gene-member counts.
- **UniProtKB REST API** (`rest.uniprot.org`): `X-Total-Results` header counts for `lanmodulin` (2), and for gene/keyword queries of xoxF and mxaF. Main use was to demonstrate that name-based counting is unreliable for these genes (mxaF text query balloons to ~17k because the term matches the whole MDH family description; lanmodulin collapses to 2).
- **Published peer-reviewed surveys, full text fetched live:** Huang et al. 2019 (PMC6775964); lanthanome-of-MOB 2025 (PMC12482762); Krause/Frontiers 2018 XoxF4/XoxF5 distribution (fmicb.2018.01366); Hyphomicrobium LanM in-silico 2024 (Commun. Biol. s42003-024-07258-3); plus abstracts for Pol et al. 2014, Methylacidimicrobium AP8, the lanthanide-rich mine community, and the Mesorhizobium LanM paper.

**What I computed vs estimated:**
- *Computed from live data:* the KEGG xoxF:mxaF gene-member ratio (5.3x); restatement of authors' reported ratios (2.9x Huang; 1.9x lanthanome); the UniProt lanmodulin count (2).
- *Read directly from sources:* LanM genome counts and families; xoxF/mxaF copy counts in defined genome sets; environmental isolation contexts.
- *Estimated from my own knowledge (flagged inline, low confidence):* the expectation that LanM-xoxF co-occurrence is >=90%.

**What I could NOT obtain without genome-scale curated data:**
1. A per-genome presence/absence matrix across all sequenced bacteria+archaea (GTDB-scale) for xoxF, xoxJ, PQQ genes, mxaF, and LanM. AnnoTree (the public tool that would give GTDB-wide KO percentages) was **not reachable via its API** during this run (its endpoints returned default Apache pages / 404s), so I could not pull GTDB-wide genome-fraction numbers for K23995 vs K14028.
2. A phylogenetically-controlled test of any hypothesis (no species tree + presence/absence matrix in hand).
3. The annotation x environmental-metadata join needed for H2 odds ratios with matched controls.
4. A same-genome-set co-occurrence calculation for H3's 80% claim.

---

## 3. Limitations -- where I guessed and where a curated resource was required

- **No genome-scale denominator.** Every "ratio" I report is a *gene-member* or *gene-copy* ratio from a curated/biased subset (KEGG genomes; ~30-180 hand-picked methylotroph genomes in the survey papers), not a *genome-presence* frequency over all sequenced genomes. KEGG and the survey panels over-sample model methylotrophs, which deflates the apparent xoxF:mxaF ratio (mxaF is concentrated in exactly the well-sampled genera). The "true" GTDB-wide ratio could be higher than my 2-6x estimate, but I have no number to support >=10x, so I report H1 as not supported at threshold while flagging this sampling caveat.
- **No phylogenetic control anywhere.** All three hypotheses pre-register a "after phylogenetic control" condition. I could not satisfy this for any of them. Pooled counts treat each genome as independent, which they are not.
- **H2 is the weakest.** I can give one-sided anecdotes (volcanic, geothermal, REE-rich mine) but zero controls and zero effect sizes. I deliberately did not invent odds ratios. The honest verdict is "cannot determine quantitatively."
- **Name-based search fails for LanM and is dangerous for mxaF.** The UniProt experiment shows public flat-text queries can be off by orders of magnitude (2 vs the dozens of real LanM homologs; 17k spurious mxaF). Correct surveys require profile HMMs / structural search over a genome set, i.e. a curated annotation pipeline.
- **KO mis-mapping risk.** The pre-registered KEGG IDs were partly wrong (K00114 != xoxF). Catching this needed manual verification; a curated crosswalk would remove this failure mode.
- **Citation imprecision in the prompt:** Pol et al. 2014 is in *Environmental Microbiology*, not *Nature* (the 2014 *Nature* lanthanide-methylotrophy connection is sometimes conflated with later structural/Nature-family papers). Minor, but worth correcting for a rigorous report.

**Bottom line:** With public data alone I could firmly establish the *direction* of all three hypotheses (xoxF > mxaF; cassette associated with REE/volcanic environments; LanM alpha-proteobacterial and xoxF-linked) and could ground several real ratios, but I could not produce the threshold-level effect sizes (>=10x for H1, per-environment ORs for H2, the >=80% co-occurrence for H3) or any phylogenetically-controlled statistic. Those specifically require a genome-scale, curated presence/absence-x-metadata resource.
