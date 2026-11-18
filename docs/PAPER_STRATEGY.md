# Paper strategy: what to add and what to cut for a high-impact journal

*Working title:* **When do communities agree? Recurrence of medicinal plant uses across independently documented communities of Northeast India, and how much it depends on survey design**

*Working description:* a systematic evidence synthesis with a source-traced audit. Don't call it a "meta-analysis" until there is a pooled estimate with defensible denominators.

## 1. The question the paper answers
Which medicinal plant uses recur across *independently* documented communities in Northeast India? And how much does that conclusion depend on how the original surveys were done: their design, how communities were attributed, whether fieldwork was reused, and how uses were coded?

The previous regional synthesis (Jha & Smith-Hall 2023, *ERA*; 255 publications) ranked species by the number of groups using them. This project adds four things:
- **Independent units:** each report is counted once per independent fieldwork survey × community.
- **Same-use agreement:** two reports agree only if they cite the same specific condition, not just the same plant.
- **Source tracing:** every claim keeps its original wording, and an automatic check records whether that wording occurs near the plant name in the source text.
- **Explicit tests:** whether design and pooling change the result, and whether agreement exceeds a chance baseline.

## 2. What the data already show (v3 corpus; preliminary)
| Finding | Number |
|---|---|
| Records → independent evidence units | 2,742 → 5,004 units (56 fieldwork groups, 59 communities, 1,040 taxa after GBIF synonymy) |
| Plant–use pairs with ≥ 3 independent reports, tier A (all primary) | **214** |
| … tier B (explicit community attribution) | 189 |
| … tier C (explicit attribution, general surveys, wording verified in source) | **137** |
| Expected by chance (conditions shuffled within each survey), A / C | 123 (95th pct 135) / 65 (95th pct 75); permutation *p* = 0.003 for both |
| Recurrent pairs (tier A) that survive dropping any single survey | 116 / 214 |
| Species-level recurrence (≥ 3 reports, any use) vs same-use recurrence | 245 species vs 214 pairs; with the same plant part as well, 155 pairs |
| Uses converging beyond the plant's overall popularity (binomial, FDR q < 0.05, ≥ 3 reports) | 137 pairs |
| Share of reports for a condition that come from single-theme surveys | jaundice 48%, abortion/contraception 46%, lactation 43%, childbirth 40% |
| Popular ≠ agreed | *Centella asiatica*: 35 groups in Jha & Smith-Hall; in our data, 28 independent reports spread over 23 conditions, and only 21% agree on any single use. *Ageratum conyzoides* (wounds) and *Clerodendrum glandulosum* (hypertension): 83% |

Taken together:
- **Real agreement exists.** Same-use agreement is about twice what each survey's own ailment mix would produce.
- **It is fragile.** Roughly 35% of the recurrent pairs are lost under strict evidence rules, and about 45% rest on a single survey.

Both halves are publishable. The paper should lead with what survives, and why.

## 3. Additions (ranked by how much they raise the ceiling)
1. **Report the search transparently** (PRISMA 2020 + PRISMA-S; ROSES for an ecology venue): counting unit, tiers, MIN_REC = 3, pilot rule and null model were fixed before the pilot output was inspected (see `docs/METHODS.md`).
2. **A systematic re-search, to replace the convenience corpus.** The Jha & Smith-Hall crosswalk already lists 135 studies they reviewed that we haven't screened (`output/jha2023_study_crosswalk.csv`). Two independent screeners, with κ reported.
3. **A source audit (done for the pilot by the authors)** of the claims that drive the headline result. Start with the 100 units in `output/pilot_trace.xlsx`, then all tier-C recurrent pairs. Report agreement for: row found, identification, part, community attribution, and same specific use. Keep the original wording next to the harmonised condition.
4. **Link reused fieldwork** in `data/survey_metadata.csv` (`fieldwork_group`): theses vs papers, the same team publishing twice (e.g. N06/N07). Add field dates and villages where the papers give them.
5. **A generalisability test.** Run the same pipeline on a second published regional synthesis, such as the West Bengal synthesis (Vineeta et al. 2022), or Jha & Smith-Hall's own supplementary table. If evidence inflation appears in two regions, the paper becomes a methods contribution, which is what high-impact journals look for.
6. **Local availability done properly.** GBIF has no georeferenced record in the region for 32% of the species, including *Vitex negundo* and *Acorus calamus*, so it can't measure availability. Use regional floras or checklists (state floras, the India Biodiversity Portal, herbarium databases such as ASSAM, ARUN and the BSI Shillong herbarium) for a site-level species pool. If that isn't achievable, report the GBIF gap as a finding and keep availability out of the main claims.
7. **Comparative case study:** West Kameng, where the Monpa, Miji, Aka and Bugun live in one district. It compares nearby communities on the same flora and asks whether they use the same species, the same genus, or the same preparation for a given use.
8. **Community and regional review:** regional ethnobotanists and community scholars review the community names, the pooled attributions, and which details are appropriate to publish (CARE principles). State the scope clearly: 7 states, with Sikkim excluded and the reason given.

## 4. What to cut or move
- Move the species catalogue, family ranks, plant-part frequencies and community tables to the **supplement**.
- **Drop pooled UV, ICF and FL indices.** Without respondent-level denominators, publication counts measure recurrence in the literature, not agreement among healers.
- **No claims about efficacy, drug discovery, knowledge loss, or a "richest" community.** Describe gaps as gaps in the retrieved literature.
- **No composite quality score.** Test each limitation separately (voucher, attribution, design, verification).
- Phylogenetic hot-node and family over-use analyses become optional extensions; they don't serve the central question.

## 5. Figures planned
1. **Fig. 1:** the agreement ladder. Species → species + condition → + same part → tier C (`fig_agreement_ladder.png`).
2. **Fig. 2:** observed vs permutation null for recurrent pairs (`fig_null_recurrence.png`).
3. **Fig. 3:** the pilot pairs under tiers A/B/C and leave-one-out, with a short example of the original wording for each (`fig_pilot_pairs.png` plus a wording panel after the audit).
4. **Fig. 4:** the design effect. Share of each condition's reports coming from single-theme surveys.
5. **Supplementary:** coverage map (tribes and districts), GBIF availability, Jha & Smith-Hall comparison.

## 6. Target journals
- *Journal of Ethnopharmacology*: needs the ConSEFS-aligned audit and taxonomy.
- *Journal of Ethnobiology and Ethnomedicine*.
- *People and Nature* or *Ecology and Society*, for the evidence-inflation framing.
- *PNAS Nexus*, only if the generalisability test (addition 5) holds in a second region.

## 7. Decision point (from the pilot)
- If most pilot pairs keep independent support after the two-reader audit, lead with **what recurs and under which conditions**.
- If support repeatedly collapses (reused fieldwork, pooled communities, merged uses), lead with **how regional syntheses overstate agreement**. That is potentially the stronger paper.
