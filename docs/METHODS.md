# Methods specification

Status: 2026-11-18. Items marked **[fixed]** were set before the pilot output was inspected.

## 1. Review question
Which medicinal plant uses recur across independently documented communities in the seven northeastern states of India (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Tripura), and how much does recurrence depend on survey design, community attribution, reused fieldwork, and use coding?

**Scope:** Sikkim is excluded. It belongs to the North Eastern Council, but its Himalayan flora and communities fall outside the "Seven Sisters" frame used here. A sensitivity analysis that includes Sikkim studies can be added.

## 2. Eligibility
- **Include:** primary field studies documenting human medicinal plant use, in which the community or communities are named and plants are identified to species, and which were published in a journal, a book chapter, or a thesis with a full text available.
- **Exclude as data:** reviews (they are used only to find primary studies), preprints (sensitivity only), and studies without species-level identification.
- **Record but analyse separately:** veterinary uses; food-only uses; non-ST communities (stratum).

## 3. Search
- **Databases:** Scopus, Web of Science, PubMed, CAB Abstracts, J-Gate.
- **Indian and grey literature:** CSIR-NOPR (*IJTK*, *IJNPR*, *NPR*), Shodhganga, Google Scholar (first 300 hits per string).
- **Snowballing:** Jha & Smith-Hall 2023 (Supplementary Tables 1 and 2), Barbhuiya et al. 2022, the review of 14 Arunachal tribes, Begum et al. 2024.
- **Search string template:** (ethnomedic\* OR ethnobotan\* OR "traditional medicine" OR "folk medicine" OR "medicinal plant\*") AND (each state OR district OR community name).
- Report dates, strings and hits per source (PRISMA-S).

## 4. Screening and extraction
- **Two independent screeners** at title/abstract and full-text stages; Cohen's κ reported, and disagreements resolved by discussion.
- **Extraction fields per record:** source, table and row, verbatim plant name, accepted name (GBIF backbone; WFO check for the final set), family, community (as written and harmonised), state, district, village, field dates, plant part, preparation, route, verbatim use wording, harmonised condition, and study design.
- **Study-level fields** (`data/survey_metadata.csv`): fieldwork group (links publications that reuse fieldwork), design, attribution, primary or review, ST status.

## 5. Unit of evidence **[fixed]**
An **independent report** is one taxon × specific condition, counted once per (fieldwork group × community).
- A pooled multi-community observation counts once and is labelled *pooled*.
- Publications sharing fieldwork share one fieldwork group.

## 6. Evidence tiers **[fixed]**
- **A:** all primary reports.
- **B:** A, with explicit community attribution only (pooled records removed).
- **C:** B, general medicinal surveys only, with the use wording verified near the species in the source text.

## 7. Outcomes and analyses **[fixed]**
- **Recurrent pair:** ≥ 3 independent reports (MIN_REC = 3).
- **Agreement ladder:** species (any use) → species + condition → + the same plant part → tier C.
- **Permutation null:** conditions are shuffled among each fieldwork group's own units, keeping each survey's ailment profile and species list. 300 permutations; one-sided *p*.
- **Robustness:** the minimum count when each fieldwork group is left out in turn; the design-effect share for each condition.
- **Use specificity:** binomial tail of the pair's reports, given the species' total reports and the condition's base rate; Benjamini–Hochberg FDR.
- **Availability (exploratory):** GBIF georeferenced occurrences in the region as a proxy, plus regional floras if obtainable. Reported as exploratory because of known coverage gaps.

## 8. Pilot **[fixed rule]**
- **Selection:** the 5 pairs with the most tier-A reports, plus 5 drawn at random (seed 2026) from pairs with 3–5 tier-A reports.
- **Audit:** two readers independently trace every supporting unit to the original table row and confirm the identification, plant part, community attribution, and that the use is the same specific use. Report the share of fields that can be recovered and the inter-reader agreement.

## 9. Not done, by design
No pooled UV, ICF or FL. No efficacy or drug-discovery claims. No knowledge-loss claims. No composite quality score.

## 10. Data and code
- **Code and derived data:** on GitHub, with a Zenodo DOI at submission.
- **Source PDFs:** not redistributed.
- **Before public release:** community and regional review of names and sensitive details (CARE principles).
