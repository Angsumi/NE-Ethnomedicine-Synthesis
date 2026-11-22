# Agreement, not popularity: a source-traced synthesis of which medicinal plant uses recur across independently documented communities of Northeast India

**Angsuman Das**<sup>1,\*</sup> (ORCID: 0000-0001-8146-7697) and **Ananda Prasad**<sup>2</sup> (ORCID: 0009-0005-1736-8148)

<sup>1</sup> Pachhunga University College (a constituent college of Mizoram University), Aizawl, Mizoram, India
<sup>2</sup> Rajiv Gandhi University, Rono Hills, Doimukh, Arunachal Pradesh, India

\*Corresponding author: Angsuman Das, angsuman.das@rgu.ac.in

---

## Abstract

**Ethnopharmacological relevance.** Northeast India lies where the Himalaya and Indo-Burma biodiversity hotspots meet. More than a hundred communities live there, and their plant medicine has been documented in hundreds of local surveys. Regional syntheses rank plants by how many groups use them. That count confounds a widely known plant with a widely agreed use, and it treats every published record as independent evidence.

**Aim of the study.** We asked which medicinal plant uses recur across *independently* documented communities of the seven northeastern states, and how much that conclusion depends on how the original surveys were done.

**Materials and methods.**
- **Corpus:** 2,742 published records from 57 sources (56 primary field studies from 55 independent fieldwork campaigns, and one review used only for cross-checking), each traced back to its source paper. 154 records whose species was absent from the cited paper were corrected or quarantined.
- **Evidence units:** records were converted into 5,004 evidence units. Each unit is one plant taxon × specific condition × community × fieldwork campaign. Support for a plant–use pair was counted as community–campaign reports, and also as distinct communities and as distinct campaigns.
- **Taxonomy:** names were resolved against the GBIF Backbone Taxonomy, giving 1,040 taxa.
- **Evidence tiers:** recurrence (≥3 reports) was estimated under three tiers. These removed pooled multi-community attributions, then theme-restricted surveys (single-ailment, plant-group), and kept only claims whose wording an automated proximity check found near the plant name in the source text.
- **Null model and robustness:** recurrence was compared with a margin-preserving null that randomises plant–condition links within each survey while keeping each plant's number of uses and each condition's number of plants (999 permutations), and was tested by leaving out each survey in turn.
- **Further analyses:** use specificity beyond plant popularity; and plant overlap and use congruence among 41 community-surveys against distance, language and state.

**Results.**
- **Recurrence:** 214 plant–use pairs recurred across ≥3 community–campaign reports, against 138 expected by chance (95th percentile 151; *p* = 0.001, the smallest attainable with 999 permutations). Counting each fieldwork campaign only once, 202 pairs remained (134 expected). Under the strictest tier 137 remained, against 72 expected.
- **Robustness:** only 116 of the 214 pairs (54%) survived the removal of any single survey.
- **Survey design:** theme-restricted surveys supplied 48% of all jaundice reports and 40–46% of reproductive-health reports.
- **Popularity is not agreement:**
  - *Centella asiatica* is the region's most widely cited medicinal plant, yet only 21% of its 28 reports agree on any one of its 23 uses.
  - *Ageratum conyzoides* for wounds and *Clerodendrum glandulosum* for hypertension each drew 83% agreement.
- **Plant overlap between communities** was low (median Jaccard 0.06) and was associated only with sharing a state.
- **Use congruence:** among plants two communities share, the same condition was cited 2.5 times more often than under the margin-preserving null (0.29 vs 0.12; *p* = 0.001). We detected no association of congruence with distance, language family or state (MRM on the 569 comparable pairs, *R*² = 0.004, *p* = 0.90), and this held across sensitivity analyses.

**Conclusions.** Shared use of specific plants for specific conditions recurs across Northeast India's communities well beyond chance, and we found no evidence that it is structured by distance, language or state; but it is narrower than species-popularity rankings imply. Half of it rests on single surveys, and its apparent extent is shaped by survey design. Counting independent, use-specific, source-checked reports changes which plants a synthesis should prioritise for pharmacological, conservation and documentation effort.

**Keywords:** ethnobotany; evidence synthesis; cross-cultural consensus; Northeast India; traditional medicine; survey design; null models

---

## 1. Introduction

Northeast India comprises Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland and Tripura. It lies at the junction of the Himalaya and Indo-Burma biodiversity hotspots (Myers et al., 2000), and it is home to more than a hundred Scheduled Tribes and other communities. These communities speak Tibeto-Burman, Austroasiatic, Tai-Kadai and Indo-Aryan languages. Their medicinal plant knowledge has been documented in hundreds of local surveys, most of them published in regional journals. The most comprehensive synthesis to date reviewed 255 publications and ranked species by the number of indigenous groups using them (Jha and Smith-Hall, 2023). State and district reviews follow the same logic (e.g. Barbhuiya et al., 2022; Das, 2021).

Counting groups per species has two problems, both well known in the comparative ethnobotany literature, though rarely quantified at a regional scale.

The first problem is that agreement on a species is not agreement on a use. A plant may be cited by many communities because it is common, cultivated or versatile, while each community uses it for something different. Cross-cultural convergence on the *same* use is the stronger signal. It is the one usually interpreted as reflecting shared observation of efficacy (Heinrich et al., 1998; Saslis-Lagoudakis et al., 2012; Gaoue et al., 2017).

The second problem is that published records are not independent evidence. Several things can multiply one observation into many records:
- one fieldwork campaign is published twice;
- a multi-community survey is split into community records;
- a survey restricted to one ailment fills a synthesis with remedies for that ailment;
- coding distinct local uses into broad categories makes reports appear to agree.

Written sources can themselves propagate uses (Leonti, 2011). Best-practice standards ask that field claims be traceable to vouchers and original wording (Heinrich et al., 2018). Syntheses rarely carry that traceability through to their counts.

Here we build a source-traced synthesis for the seven northeastern states and ask three questions:
1. Which medicinal plant uses recur across independently documented communities, and does that recurrence exceed what each survey's own mix of ailments would produce by chance?
2. How much does recurrence depend on community attribution, survey design, and verification against the source?
3. Is shared use associated with geography or language?

## 2. Materials and methods

### 2.1 Corpus and source verification
**Starting point.** We started from two community datasets compiled from the published literature:
- a seven-state dataset (1,214 records, 26 studies);
- an Assam dataset (749 records, 18 studies; Das, 2021).

**Verification.** Every study was retrieved as a PDF, or as full-text XML for open-access articles. Scanned documents were read with optical character recognition. Each record was then checked against the text of its cited source:
- whether the species occurs in the source, matched exactly, approximately, or at genus level only;
- whether the recorded plant part and use occur near the species name;
- whether the community attribution matches the paper.

**Corrections.** Records whose species was absent from the cited source were quarantined (Supplementary Data). Three sources whose full text could not be obtained were excluded. Community labels were corrected where a language name or a generic label had been used in place of the community studied. In one case a block of records was found to belong to a different publication than the one cited, and was re-attributed after verification.

**Additions.** To reduce geographic and community gaps, we added 27 further field studies, which we found by targeted searches of open-access repositories (CSIR-NOPR, Europe PMC, journal archives). Their plant tables were extracted with table parsers or transcribed, and each extracted species was checked against the source text. Species counts matched the totals reported in the papers to within 0–6 species.

**Scope of the corpus.** This is an analysis of a selected, source-traced corpus, not a systematic review. We deliberately built a corpus in which every record can be traced to and checked against its source text, rather than re-extracting every study listed in earlier reviews. Studies were included when their full text could be obtained, the community and study area were stated, and plants were identified to species. Our aim is to test how counting rules, survey design and verification change conclusions, so traceability was prioritised over exhaustiveness. Overlap with the study list of the previous regional synthesis (Jha and Smith-Hall, 2023) is reported in Section 2.9. *[Authors to complete: search dates, exact search strings per repository, number of records screened, studies excluded with reasons, and who performed screening and extraction (Supplementary Table S1). The 135 further studies in the screening list (docs/SCREENING_LIST.md) were not screened for this analysis.]*

**Final corpus:** 2,742 records from 57 sources, covering all seven states (Supplementary Table S1): 2,699 records from 56 primary field studies, which represent 55 independent fieldwork campaigns (two papers report one campaign), and 43 records from one secondary review (source S15 in Table S1). Records from the review are excluded from every analysis of primary evidence.

### 2.2 Survey metadata
For every study we recorded the following (Supplementary Table S1):
- **Design:** general medicinal survey; single-ailment or selected-ailment; plant-group (e.g. trees of sacred groves, leaves only, underutilised plants); food and medicine; or review.
- **Community attribution:** single community; several communities attributed per plant; or pooled.
- **Study districts.**
- **Whether the community is a Scheduled Tribe.**
- **A fieldwork group** linking publications likely to share fieldwork (e.g. two 2024 Mizoram studies by the same team in overlapping districts).

Reviews were retained only to locate primary studies. They were excluded from all analyses of recurrence.

### 2.3 Taxonomy and condition coding
Plant names were resolved against the GBIF Backbone Taxonomy (GBIF Secretariat, 2023) and synonyms were merged. 1,082 of 1,177 names matched at species level with ≥80% confidence. Unmatched names were kept as unresolved taxa and never merged with other names.

The original use wording of each record was coded to 65 specific conditions (e.g. dysentery, jaundice, wounds/cuts, hypertension). The coding used a published vocabulary of regular expressions (Supplementary Data) rather than broad body-system categories (Cook, 1995), so that "agreement" refers to a specific use. The original wording was preserved alongside the code.

### 2.4 Unit of evidence and evidence tiers
A **report** was defined as one taxon × condition, counted once per community within a fieldwork campaign (fieldwork group, Section 2.2). Records of the same claim from one survey therefore count once, however many times they appear.

Because a campaign can document several communities, and one community can be studied by several campaigns, community–campaign reports are not fully independent. We therefore also counted support for each pair as (i) distinct communities, merging repeat surveys of one community, and (ii) distinct fieldwork campaigns, counting a multi-community campaign once. The campaign count is the conservative definition and is reported alongside the main count.

Recurrence was estimated in three nested tiers:
- **A:** all primary reports.
- **B:** A, restricted to explicit community attribution (pooled multi-community observations removed).
- **C:** B, restricted to general medicinal surveys and to claims that passed an automated proximity check: the condition wording occurred within 700 characters after the plant name (matched as an abbreviated species pattern, with a genus-only fallback) in the source text. This check does not confirm that the claim comes from the same table row (Section 4.5).

A pair was called **recurrent** if supported by ≥3 reports. This threshold, the tiers, and the pilot selection rule (Section 2.7) were fixed before results were inspected.

### 2.5 Null models and robustness
**Recurrence beyond chance.** Within every community–campaign report we randomised the plant × condition incidence matrix with the curveball algorithm (Strona et al., 2014), and recounted recurrent pairs (999 permutations; burn-in of 50 sweeps, then 5 sweeps between samples). This null keeps each report's species list, the number of conditions cited for each plant, and the number of plants cited for each condition, including the over-representation of one ailment in a single-ailment survey. It breaks only which plant is linked to which condition. Plants and conditions are treated as exchangeable only within a report, never across surveys. The test was repeated with recurrence counted by distinct campaigns. An earlier, less constrained null (condition labels shuffled among a fieldwork group's units, duplicates removed) did not preserve the number of uses per plant; it gave the same conclusion and is reported in the Supplementary Data.

**Robustness.** For each recurrent pair we recorded the minimum number of reports remaining when each fieldwork group was removed in turn.

**Survey design.** The influence of design was summarised as the share of each condition's reports contributed by theme-restricted surveys.

**Use specificity.** To separate use-specific convergence from popularity, we computed for each taxon × condition the binomial probability of at least the observed number of reports, with Benjamini–Hochberg correction (Benjamini and Hochberg, 1995). Trials and baseline use the same unit: a trial is one report of the taxon (community–campaign × plant), and the baseline probability is the share of all report × plant combinations in the corpus that cite the condition. The binomial treats reports as independent; as a sensitivity analysis the test was repeated with fieldwork campaigns as the unit, which removes dependence among communities documented by one campaign.

### 2.6 Geography, language and use congruence
**Assemblages.** Each community within an independent general survey with ≥10 resolved species and explicit attribution was treated as an assemblage (*n* = 41). Each assemblage was located at the mean coordinates of its study districts (OpenStreetMap Nominatim).

**Measures.** For every pair of assemblages we computed two quantities:
- **Plant overlap:** Jaccard similarity of their plant sets.
- **Use congruence:** among the plants both used (≥3 shared), the proportion cited for at least one common condition. Because use congruence is computed only on shared plants, it is insensitive to differences in available flora. It is undefined for pairs sharing fewer than three plants (251 of 820 pairs).

**Regression.** Both measures were regressed on log distance, same language family, same linguistic subgroup and same state, using multiple regression on distance matrices (MRM) with 9,999 permutations of assemblage labels (Lichstein, 2007), which accounts for the dependence among pairs that share an assemblage. Pairs without a congruence value were not imputed. The congruence model was fitted to the comparable pairs only; in each permutation the pattern of missing pairs moved with the permuted labels, and the model was refitted to the pairs comparable after permutation.

**Sensitivity of the congruence model.** We refitted the model (i) weighting pairs by the number of shared plants, (ii) requiring ≥5 and ≥10 shared plants, and (iii) modelled missingness itself, regressing whether a pair was comparable (≥3 shared plants) on the same predictors, to check whether which pairs could be compared depended on geography or language.

**Null for congruence.** Use congruence was compared with a curveball null applied within each assemblage, which keeps its plants, the number of conditions per plant and the number of plants per condition (999 permutations).

### 2.7 Pilot source audit
Ten pairs were selected by a rule fixed in advance: the five with the most tier-A reports, and five drawn at random (seed 2026) from pairs with 3–5 reports. All 100 supporting units were exported with a verbatim snippet of the source text and the original use wording. The authors checked each unit against the original table row for plant identification, plant part, community attribution and use (Supplementary Data).

### 2.8 Completeness and availability
**Completeness (exploratory).** Incidence-based Chao2 with bias correction and log-normal 95% confidence intervals (Chao, 1987; Chao et al., 2009) was computed over the 74 community-survey units, with accumulation curves averaged over 200 random orders. Chao2 assumes exchangeable sampling units of comparable effort. Our units mix general and targeted surveys, pooled observations and very unequal effort, drawn from a corpus selected for availability, so we treat the estimates as exploratory. We report their sensitivity to unit definition, survey design, attribution and effort, and to leaving out each unit in turn (Supplementary Fig. S3).

**Availability.** As an exploratory proxy for plant availability, we counted georeferenced GBIF occurrence records of each accepted taxon in India within 21.9–29.5°N, 89.7–97.5°E. We related them to reports by Spearman correlation and by a negative-binomial GLM.

### 2.9 Comparison with the previous regional synthesis
We parsed the study list (Supplementary Table 1) and species table (Supplementary Table 2) of Jha and Smith-Hall (2023). We matched studies by first author and year, and species through the same taxonomic backbone. We then compared their counts of groups per species with our reports, both for any use and for the best-supported single use.

### 2.10 Software and data
All analyses used Python (pandas, NumPy, SciPy, statsmodels, NetworkX, GeoPandas). The code, derived data, figures and verification logs are openly available (see Data availability). Source PDFs are not redistributed.

## 3. Results

### 3.1 The corpus
The 57 sources (56 primary field studies and one review) cover the following:

| | Count |
|---|---|
| Communities | 59 |
| Independent fieldwork campaigns (primary studies) | 55 |
| Taxa | 1,040 |
| States | all 7 |
| Independent evidence units (from 2,742 records) | 5,004 |

Coverage was uneven (Fig. 1):
- **Arunachal Pradesh:** 15 of 24 listed communities.
- **Assam:** 12 of 23.
- **Nagaland:** 5 of 17.
- **Manipur:** 6 of 17.

No accessible primary study was found for several major Naga communities (Sumi, Phom, Chang, Yimkhiung, Khiamniungan, Zeliang) or for Chakma communities in Tripura.

**Verification errors.** Source verification identified 154 records (8% of the original datasets) whose species did not occur in the cited paper. It also found one 53-record block labelled with a community that does not occur in the source.

**Extent of auto-extraction.** 35% of evidence units came from tables extracted automatically for this study. For 86% of all units, the coded use was found near the plant name in the source text.

**Pilot check.** All 100 units supporting the ten pilot pairs were confirmed against the original sources by the authors. The automated checks had flagged 17 of them: in some the use wording was not located near the plant name, and in others the extracted wording joined text from adjacent table rows. On inspection the plant–use claims were correct; only the extracted wording needed cleaning.

### 3.2 Recurrence exceeds chance but is fragile
| | Tier A | Tier C |
|---|---|---|
| Recurrent pairs, community–campaign reports (≥3) | 214 (87 taxa) | 137 |
| Expected by chance: mean (95th percentile) | 138 (151) | 72 (82) |
| Recurrent pairs, distinct campaigns (≥3) | 202 | 129 |
| Expected by chance: mean (95th percentile) | 134 (147) | 69 (79) |
| Permutation *p* (all four tests) | 0.001 | 0.001 |

No permutation reached the observed value (null maxima: 162 and 95 pairs for tiers A and C), so *p* = 0.001 is the resolution limit of 999 permutations. The strict tier removes 36% of recurrent pairs, yet the excess over chance remains (Figs. 2, 3a–b).

**Replication unit.** Counted by distinct communities, 207 of the 214 tier-A pairs remained recurrent; counted by distinct campaigns, 202 did. Twelve pairs owe their recurrence to campaigns that documented several communities, and seven to repeat surveys of one community. These are flagged in the Supplementary Data.

**Robustness.** 116 of the 214 tier-A pairs (54%) retained ≥3 reports when any single fieldwork campaign was removed.

**Agreement ladder.** Agreement thinned rapidly as it was made more specific (Fig. 2b):

| At ≥3 reports | Count |
|---|---|
| Species (any use) | 245 |
| Species + same condition | 214 pairs |
| + same plant part | 155 pairs |
| Tier C (strictest evidence) | 137 pairs |

The best-supported pairs are listed below (Fig. 6b). Each was reported from four to six states, retained most of its support under leave-one-out, and was use-specific under both the report and the campaign unit (Section 3.3):

| Plant | Use | Independent reports (tier A) |
|---|---|---|
| *Clerodendrum glandulosum* | hypertension | 20 |
| *Ageratum conyzoides* | wounds and cuts | 19 |
| *Houttuynia cordata* | dysentery | 15 |
| *Psidium guajava* | dysentery | 14 |
| *Ocimum tenuiflorum* | cough | 12 |
| *Catharanthus roseus* | diabetes | 10 |

### 3.3 Popular is not agreed
**Use specificity.** 72 of 3,335 taxon–condition pairs converged on a use more than the plant's overall popularity and the condition's frequency predict (binomial, FDR *q* < 0.05, ≥3 reports). With fieldwork campaigns as the unit, 69 pairs did, and 68 were significant under both definitions. An earlier version of this test used a baseline with a different denominator (the condition's share of plant × condition units) and was anti-conservative.

**Popularity and agreement are distinct (Fig. 4):**
- **Versatile plants.** *Centella asiatica* is the most widely cited plant in the previous regional synthesis (35 groups). In our data it had 28 reports spread over 23 conditions, and only 21% agreed on any single use. *Azadirachta indica*, *Carica papaya* and *Curcuma longa* behaved similarly.
- **Convergent plants.** *Ageratum conyzoides* (wounds) and *Clerodendrum glandulosum* (hypertension) each drew 83% agreement on one use. So did *Syzygium cumini* (diabetes) and *Spilanthes* spp. (toothache) at smaller reach.

**Comparison with the previous synthesis.** Across the species we could match, its group counts correlated with our reports for any use (Spearman ρ = 0.76) and for the best single use (ρ = 0.75). The ranking at the top, however, changed.

**Consensus network.** The tier-C recurrent pairs formed a modular network (Fig. 5): 61 plants and 34 conditions, 9 modules, modularity 0.64. Its modules correspond to recognisable therapeutic clusters:
- dysentery–diarrhoea–stomach ache;
- cough–cold–bronchitis;
- wounds–bleeding;
- jaundice–diabetes–hypertension;
- urinary–kidney stone–oral care.

### 3.4 Survey design shapes apparent agreement
Theme-restricted surveys contributed a disproportionate share of some conditions (Fig. 6a):

| Condition | Share of reports from single-ailment or selected-ailment surveys |
|---|---|
| Jaundice | 48% |
| Abortion/contraception | 46% |
| Lactation | 43% |
| Childbirth | 40% |
| Liver disorders | 39% |
| Bone fracture | 25% |

Restricting to general surveys therefore changes which conditions appear to attract consensus. Among the pilot pairs, *Clerodendrum glandulosum* for hypertension fell from 20 tier-A reports to 8 under tier C. The pairs with fewer reports changed little (Fig. 6b).

### 3.5 No detectable geographic or linguistic structure in shared use
**Plant overlap.** Overlap between community-surveys was low (median Jaccard 0.058; 820 pairs). It was weakly but significantly higher within states (MRM *R*² = 0.07, *p* = 0.024; same state *b* = 0.025, *p* < 0.001). We detected no association with distance (*p* = 0.94), language family (*p* = 0.51) or subgroup (*p* = 0.28) (Supplementary Fig. S1).

**Use congruence.** Among shared plants, use congruence averaged 0.29, 2.5 times its expectation under the margin-preserving null (0.12; 95th percentile 0.13; *p* = 0.001; Fig. 3c). On the 569 comparable pairs, we detected no association with any predictor (*R*² = 0.004, *p* = 0.90; all coefficients *p* ≥ 0.47). The result was the same when pairs were weighted by shared plants (*p* = 0.93) and when ≥5 (386 pairs; *p* = 0.77) or ≥10 shared plants (130 pairs; *p* = 0.95) were required. Whether a pair was comparable at all (69% of pairs) was likewise not associated with distance, language or state (*R*² = 0.017, *p* = 0.45). With 41 assemblages, these tests can rule out only moderate-to-strong effects; weak geographic or linguistic structure cannot be excluded.

**Repeat surveys of one community.** Independent surveys of the same community (*n* = 7 pairs) overlapped no more in plants (Jaccard 0.02–0.12) or uses than surveys of different communities.

### 3.6 Documentation is sparse
**Singletons.** The 74 community-survey units document 956 taxa, and 567 of them (59%) were reported by only one unit.

**Exploratory richness estimates (Supplementary Fig. S3).** Under the assumptions of Chao2, the observed taxa would be 44–49% of the estimated total across seven alternative definitions of the sampling unit and subsets of the corpus. The estimated total itself was less stable (1,758–2,081 taxa; 1,929–2,105 when leaving out one unit at a time). These figures indicate that much of the regional medicinal flora is undocumented, but they are not a measured share of it.

**Availability.** Reach correlated with GBIF occurrence records (ρ = 0.40; *p* < 10⁻³⁰). However, 277 of 875 taxa (32%) had no georeferenced record in the region, including *Vitex negundo* and *Acorus calamus* (Supplementary Fig. S2).

## 4. Discussion

### 4.1 A shared practice, narrower than popularity rankings suggest
Communities of Northeast India agree on specific uses of specific plants far more often than their surveys' own ailment profiles would produce, even when each plant keeps its number of uses and each fieldwork campaign is counted once. Among plants that two communities both use, they use them for the same purpose two and a half times as often as chance. We detected no association of this congruence with distance, language family or state, although our design can exclude only moderate-to-strong effects.

Taken alone, this pattern is consistent with, though it does not establish, a region-wide therapeutic repertoire, maintained across linguistic boundaries by exchange, markets and shared ecological experience. Cross-cultural convergence on the same use has long been read as evidence of efficacy or salience (Heinrich et al., 1998; Saslis-Lagoudakis et al., 2012). Our data identify where that reading is best supported. Examples are *Ageratum conyzoides* for wounds, *Clerodendrum glandulosum* for hypertension, *Houttuynia cordata* and *Psidium guajava* for dysentery, *Ocimum tenuiflorum* for cough and *Catharanthus roseus* for diabetes. Each was reported independently from four to six states and survives the strictest evidence rules.

The same analysis shows that the shared repertoire is narrower than species rankings imply. The region's most widely cited plants are often the most versatile, not the most agreed. *Centella asiatica* is cited by dozens of groups for twenty-odd different conditions. That makes it culturally prominent, but it is weak evidence for any particular therapeutic claim. Ranking species by groups using them therefore mixes two different kinds of importance. Separating reach from agreement (Fig. 4) gives pharmacological follow-up a better-targeted list. In this list, convergent uses are candidates for efficacy testing, and versatile plants are candidates for cultural and conservation study.

### 4.2 How much the evidence base shapes the conclusion
Three features of the literature change the result.

**Pooled and multi-community surveys.** Removing pooled attributions reduced recurrent pairs by 12%.

**Theme-restricted surveys.** These concentrate reports on particular conditions. A jaundice survey creates many opportunities to record jaundice remedies, and a sacred-grove tree survey creates none for herbs. Nearly half of all jaundice reports come from such surveys. Syntheses that pool them with general surveys will over-represent their conditions among apparently consensual uses.

**Dependence on single surveys and campaigns.** Only half of the recurrent pairs survive the removal of any single campaign, and 12 depend on counting several communities from one campaign separately. In addition, 8% of records in the starting datasets did not occur in the paper they cited. Errors of this kind propagate silently through syntheses that count records.

These effects do not overturn the main finding: the excess over chance persists in the strictest tier. But they change which claims a synthesis can defend, and by how much. We therefore recommend four reporting practices for regional ethnobotanical syntheses:
- state the counting unit;
- link publications that share fieldwork;
- keep pooled observations identifiable;
- report recurrence separately for general and theme-restricted surveys.

### 4.3 Low overlap and incomplete documentation
**Low overlap.** Plant overlap between community-surveys was low. Repeat surveys of the same community overlapped as little as surveys of different communities. Two explanations, not mutually exclusive, fit this pattern:
- medicinal knowledge is genuinely local and heterogeneous;
- each survey samples a small, partly random subset of a community's knowledge, depending on informants, season and the investigator's focus.

**Sparse documentation.** Most documented taxa were recorded by a single survey, which is consistent with the second explanation. Exploratory richness estimates point the same way, but they rest on assumptions (exchangeable units of comparable effort) that this corpus does not meet, so we do not attach a precise percentage to them.

The practical implication is direct. The absence of a plant from a community's published list is weak evidence that the community does not use it. Apparent differences between communities should not be read as cultural differences, nor as knowledge loss, without repeated sampling.

**Uneven coverage.** Gaps are concentrated in Nagaland and Manipur, where several major communities lack any accessible primary study. They are also concentrated in the southern Mizo hills, where minority communities appear in only one multi-community survey. These are gaps in the retrieved literature and set priorities for future documentation.

### 4.4 Availability
Whether shared use simply reflects shared availability could not be tested adequately. Reach correlated moderately with GBIF records, but a third of the taxa had no georeferenced record in the region. These included some of the most widely used medicinal plants, which reflects the limited digitisation of herbarium and survey data from Northeast India.

Our congruence measure partly sidesteps the problem by comparing uses only among plants both communities use. A proper test requires site-level species pools from regional floras and herbaria. Assembling these is a priority for future work.

### 4.5 Limitations
- **The corpus is selected and source-traced, not exhaustive.** It was assembled by targeted retrieval, not by a systematic search, and we did not re-extract every study listed by the previous synthesis (Jha and Smith-Hall, 2023). Absolute counts would grow with more studies. The comparisons we report (between evidence tiers, against permutation nulls, and with each survey left out in turn) are relative, and are designed to remain valid as surveys are added.
- **Condition coding uses a fixed vocabulary.** Some local concepts do not map cleanly onto biomedical conditions.
- **Some extraction is automatic.** Automatic table extraction can carry text over from neighbouring rows. We retain the original wording and a source-verification flag for every claim. The pilot check was done by the authors rather than by independent readers, so no inter-reader agreement is reported; the audit sheet is published so that others can repeat it.
- **Verification is approximate.** Our source-verification test is an automated proximity check: it searches a 700-character window after an abbreviated species pattern and can fall back to the genus alone, so a condition may belong to a neighbouring species or row. Tier C therefore means "passed an automated proximity check", not "verified in its original row". The pilot audit covered 100 units supporting ten pre-selected pairs and cannot establish accuracy across the corpus. *[Authors to complete: results of the stratified validation sample (parser-extracted records, ambiguous names, community attribution, positive and negative automated flags), with agreement statistics.]*
- **Reports are not fully independent.** Communities studied by one campaign share investigators and methods, and the binomial and permutation tests treat reports as exchangeable within the stated constraints. Counting by distinct campaigns changed few results, but residual dependence (shared written sources, regional markets) cannot be removed with these data.
- **Locations are coarse.** Community locations are approximated by district centroids.

## 5. Conclusions
Medicinal plant knowledge in Northeast India includes recurrent, specific plant–use pairs that exceed chance under conservative null models and counting rules, with no detectable association with distance, language or state. That repertoire is narrower than popularity rankings suggest. It rests heavily on a few surveys, and it is shaped by survey design. Counting independent, use-specific, source-checked reports gives a different and more defensible picture than counting records or groups per species.

We provide the source-traced dataset and code so that the claims can be checked, extended and corrected as new surveys are added.

---

## Declarations

**Funding.** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors. The work was self-funded by the authors.

**Competing interests.** The authors declare no competing interests.

**CRediT authorship contribution statement.**
- **Angsuman Das:** Data curation, Formal analysis, Investigation, Software, Validation, Visualization, Writing – review & editing.
- **Ananda Prasad:** Conceptualization, Methodology, Project administration, Writing – original draft, Writing – review & editing.

**Ethics.** This study analyses published literature only and involved no human participants. Community names follow the source publications and the Census of India Scheduled Tribe lists. No knowledge marked as restricted in the source studies is reproduced, and data handling follows the CARE Principles for Indigenous Data Governance (Carroll et al., 2020).

**Declaration of generative AI use.** Generative AI tools were used to assist language editing and formatting of the manuscript draft and preparation of submission documents. The authors take responsibility for the final text and its scientific content.

**Data availability.** Code, the source-traced dataset, evidence units, verification logs and figures are available at https://github.com/Angsumi/NE-Ethnomedicine-Synthesis and archived on Zenodo (https://doi.org/10.5281/zenodo.24332943). Source publications are cited in Supplementary Table S1 and are not redistributed.

**Acknowledgements.** We thank the communities whose knowledge is documented in the studies synthesised here, and the authors of those studies.

---

## Figure legends

**Fig. 1.** Community-surveys included in the synthesis (general medicinal surveys with explicit community attribution). Points are placed at the mean coordinates of study districts and sized by the number of species documented; colours show language family. Boundaries are schematic.

**Fig. 2.** (a) Evidence funnel from published records to evidence units and evidence tiers, with the number of recurrent plant–use pairs (≥3 reports) under each rule, when each fieldwork campaign is counted once, and the number expected under the margin-preserving null. (b) Agreement ladder: species, species + condition, + same plant part, and tier C, at increasing minimum numbers of reports (log scale).

**Fig. 3.** Agreement beyond chance. Observed values (orange) against 999 draws of a curveball null that randomises plant–condition links within each survey while keeping each plant's number of conditions and each condition's number of plants: (a) recurrent pairs, tier A; (b) recurrent pairs, tier C; (c) mean use congruence on plants shared by two community-surveys.

**Fig. 4.** Popularity is not agreement. Each point is a taxon with ≥5 reports. The *x*-axis is reach (reports for any use); the *y*-axis is the share of reports agreeing on the single most-cited use; point size is the number of distinct conditions. Blue: taxa with at least one use converging beyond popularity (binomial with report × plant trials, FDR *q* < 0.05).

**Fig. 5.** Consensus network of plant–use pairs with ≥3 reports under the strictest evidence tier. Inner ring: conditions. Outer ring: plants, sized by total reports. Colours: network modules. Line width: number of reports.

**Fig. 6.** (a) Share of each condition's reports contributed by single- or selected-ailment surveys (dark) and by plant-group or food-and-medicine surveys (light). (b) Pilot pairs, selected by a rule fixed in advance, under tiers A, B and C and the worst case when one survey is left out.

**Supplementary Fig. S1.** Plant overlap (a) and use congruence (b) between community-surveys against distance, by same or different language family, with medians in distance bins and MRM statistics.

**Supplementary Fig. S2.** Community–campaign reports against GBIF georeferenced occurrence records in the region.

**Supplementary Fig. S3.** Exploratory completeness estimates, under the exchangeable-unit assumptions of Chao2. (a) Accumulation of taxa and plant–use pairs over independent community-surveys (mean and 95% interval of 200 random orders), with Chao2 estimates. (b) Documented and Chao2-estimated medicinal taxa by state (95% CI) and percentage documented; *n* is the number of community-survey units.

---

## References

Barbhuiya, P.A., Laskar, A.M., Mazumdar, H., Dutta, P.P., Pathak, M.P., Dey, B.K., Sen, S., 2022. Ethnomedicinal practices and traditional medicinal plants of Barak Valley, Assam: a systematic review. Journal of Pharmacopuncture 25, 149–185. https://doi.org/10.3831/KPI.2022.25.3.149

Benjamini, Y., Hochberg, Y., 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. Journal of the Royal Statistical Society B 57, 289–300.

Carroll, S.R., Garba, I., Figueroa-Rodríguez, O.L., Holbrook, J., Lovett, R., Materechera, S., et al., 2020. The CARE Principles for Indigenous Data Governance. Data Science Journal 19, 43. https://doi.org/10.5334/dsj-2020-043

Chao, A., 1987. Estimating the population size for capture–recapture data with unequal catchability. Biometrics 43, 783–791.

Chao, A., Colwell, R.K., Lin, C.W., Gotelli, N.J., 2009. Sufficient sampling for asymptotic minimum species richness estimators. Ecology 90, 1125–1133.

Cook, F.E.M., 1995. Economic Botany Data Collection Standard. Royal Botanic Gardens, Kew.

Das, A., 2021. Green heritage of Assam: a comprehensive meta-analysis of traditional medicinal practices. Journal of Advanced Zoology 42(1), 171–178.

Gaoue, O.G., Coe, M.A., Bond, M., Hart, G., Seyler, B.C., McMillen, H., 2017. Theories and major hypotheses in ethnobotany. Economic Botany 71, 269–287.

GBIF Secretariat, 2023. GBIF Backbone Taxonomy. Checklist dataset. https://doi.org/10.15468/39omei (accessed November 2026).

Heinrich, M., Ankli, A., Frei, B., Weimann, C., Sticher, O., 1998. Medicinal plants in Mexico: healers' consensus and cultural importance. Social Science & Medicine 47, 1859–1871.

Heinrich, M., Lardos, A., Leonti, M., Weckerle, C., Willcox, M., et al., 2018. Best practice in research: Consensus Statement on Ethnopharmacological Field Studies – ConSEFS. Journal of Ethnopharmacology 211, 329–339.

Jha, K.K., Smith-Hall, C., 2023. Three models to illustrate plant–people relationships in the medicinal plant hotspots of North East India. Ethnobotany Research and Applications 26, 7. https://doi.org/10.32859/era.26.7.1-48

Leonti, M., 2011. The future is written: impact of scripts on the cognition, selection, knowledge and transmission of medicinal plant use and its implications for ethnobotany and ethnopharmacology. Journal of Ethnopharmacology 134, 542–555.

Lichstein, J.W., 2007. Multiple regression on distance matrices: a multivariate spatial analysis tool. Plant Ecology 188, 117–131.

Myers, N., Mittermeier, R.A., Mittermeier, C.G., da Fonseca, G.A.B., Kent, J., 2000. Biodiversity hotspots for conservation priorities. Nature 403, 853–858.

Saslis-Lagoudakis, C.H., Savolainen, V., Williamson, E.M., Forest, F., Wagstaff, S.J., Baral, S.R., Watson, M.F., Pendry, C.A., Hawkins, J.A., 2012. Phylogenies reveal predictive power of traditional medicine in bioprospecting. Proceedings of the National Academy of Sciences USA 109, 15835–15840.

Strona, G., Nappo, D., Boccacci, F., Fattorini, S., San-Miguel-Ayanz, J., 2014. A fast and unbiased procedure to randomize ecological binary matrices with fixed row and column totals. Nature Communications 5, 4114. https://doi.org/10.1038/ncomms5114

Vineeta, Shukla, G., Bhat, J.A., Chakravarty, S., 2022. Species richness and folk therapeutic uses of ethnomedicinal plants in West Bengal, India – a meta-analysis. Phytomedicine Plus 2, 100158. https://doi.org/10.1016/j.phyplu.2021.100158

*All 57 sources (56 primary field studies and one review) are listed in Supplementary Table S1.*
