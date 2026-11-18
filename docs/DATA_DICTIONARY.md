# Data dictionary

## output/NE_combined_v3.xlsx — sheet `Data` (one row per record as published)
| Column | Meaning |
|---|---|
| SourceID | S## = NE5 / V6 source, N## / G## = sources added in this project (see `data/survey_metadata.csv`) |
| Dataset, Row | origin (NE5, V6, NEW, GAP) and row in that origin file |
| Botanical Name, Family Name, Common Name | as entered (spelling-corrected names are resolved later, not overwritten) |
| Partsused, Disease, ActedUpon, Way to Use | as entered / extracted; `ActedUpon` for added sources is auto-assigned |
| Tribe, Tribe_original | harmonised and original community label |
| State, Reference | state; full citation |
| status | verification against the paper (exact / fuzzy / genus_only / extracted_from_paper / verified_in_corrected_source) |
| qc_flag | warnings kept on the record (parser, review source, non-ST, single-theme study, …) |
| found_in_other_sources | other corpus papers containing a species missing from its cited paper |

Sheets `Quarantine` (records held back, with `qc_reason`), `Changelog`, `Added_sources`, `Not_yet_added`.

## data/survey_metadata.csv (one row per source)
`fieldwork_group` links publications sharing fieldwork · `design` ∈ general, single_ailment, plant_group,
food_and_medicine, selected_ailments, review · `attribution` ∈ single_community, multi_community_explicit, pooled ·
`is_primary` · `non_st` · `citation_note` (corrections).

## data/taxonomy_gbif.csv
GBIF Backbone match per name in the data: match type, confidence, accepted key / species / family; `usable` = species-level match with confidence ≥ 80.

## output/evidence_units.csv (one row per independent unit)
Key: `fieldwork_group × community × taxon × condition`. Also `source_ids`, `n_records`, `design`, `attribution`,
`parts`, `use_found_in_source` (condition wording found within 700 characters after the species name in the source text),
`parser_flag`, `original_use_wording` (verbatim, joined).

## output/condition_vocabulary.csv
Specific conditions and the regular expressions that assign them from the original wording.

## output/recurrence_pairs.csv
Per taxon × condition: reports under tiers A/B/C, `species_any_use`, `same_part`, `A_leave_one_out_min`, states, communities.

## output/use_specificity.csv, output/availability_species.csv
Binomial use-specificity test (with BH q-values); GBIF regional occurrence counts and negative-binomial residuals.

## output/jha2023_study_crosswalk.csv, output/jha2023_species_comparison.csv
Study-level overlap with Jha & Smith-Hall 2023 and species-level comparison.
