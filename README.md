# NE India Ethnomedicine — evidence synthesis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24332943.svg)](https://doi.org/10.5281/zenodo.24332943)

**Authors:** Angsuman Das (Pachhunga University College, Mizoram University; ORCID [0000-0001-8146-7697](https://orcid.org/0000-0001-8146-7697)) and
Ananda Prasad (Rajiv Gandhi University; ORCID [0009-0005-1736-8148](https://orcid.org/0009-0005-1736-8148)).

**Manuscript draft:** [`docs/manuscript/manuscript.md`](docs/manuscript/manuscript.md) (also `.docx`) · figures in [`output/figures/pub/`](output/figures/pub/) ·
cite via [`CITATION.cff`](CITATION.cff) · licence: MIT (code), CC BY 4.0 (data, figures, documents)

Source-traced synthesis of published ethnomedicinal plant records from the seven northeastern states of India
(Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Tripura).

**Question:** which medicinal plant uses recur across *independently* documented communities, and how much does
that depend on how the original surveys were done?

- Paper strategy and preliminary results: [`docs/PAPER_STRATEGY.md`](docs/PAPER_STRATEGY.md)
- Methods specification: [`docs/METHODS.md`](docs/METHODS.md)
- Data dictionary: [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md)
- Source verification history: [`output/VERIFICATION_REPORT.md`](output/VERIFICATION_REPORT.md), coverage: [`output/COVERAGE_AND_QUALITY_PLAN.md`](output/COVERAGE_AND_QUALITY_PLAN.md)

## Current corpus (v3)
2,742 records · 57 sources · 56 independent fieldwork groups · 59 communities · 1,040 taxa (GBIF backbone) ·
5,004 independent evidence units.

## Headline (preliminary)
- 214 plant–use pairs have ≥ 3 independent community reports. Chance expectation, from shuffling conditions within each survey: 123 (permutation p = 0.003).
- Under strict evidence rules (explicit attribution, general surveys, wording verified in the source), 137 remain, against a chance expectation of 65.
- 116 of the 214 pairs survive dropping any single survey.
- Species popularity is not the same as agreement. *Centella asiatica* is the most widely used plant in the previous regional review. In our data its reports spread over 23 conditions, and only 21% agree on any single use.

## Reproduce
```bash
bash scripts/fetch_inputs.sh          # clones the two input datasets (NE5.xlsx, Assam V6.xlsx)
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
bash run_all.sh                       # needs the source PDFs/texts under sources/ (not redistributed)
```
Scripts 13–18 run from the derived files in `output/` and `data/`. They don't need the PDFs, except for the source-text verification and the pilot snippets.

## Layout
| Path | Contents |
|---|---|
| `analysis/01–12` | cleaning, verification against papers, extraction of added sources, merges (v1→v3) |
| `analysis/13_evidence_units.py` | independent evidence units, condition vocabulary, source-text verification |
| `analysis/14_taxonomy_gbif.py` | name resolution to GBIF Backbone (cached in `data/taxonomy_gbif.csv`) |
| `analysis/15_recurrence.py` | recurrence tiers, agreement ladder, leave-one-out, permutation null, design effect |
| `analysis/16_pilot_trace.py` | 10-pair pilot with source snippets and two-reader audit sheet |
| `analysis/17_availability.py` | GBIF occurrence availability proxy and use-specificity test |
| `analysis/18_crosswalk_jha2023.py` | bibliography and species crosswalk with Jha & Smith-Hall 2023 |
| `analysis/19_geocode_districts.py` | district coordinates (OpenStreetMap Nominatim; cached in `data/district_coords.csv`) |
| `analysis/20_similarity.py` | plant overlap and use congruence vs distance, language, state (MRM; permutation nulls) |
| `analysis/21_completeness_network.py` | Chao2 completeness, accumulation curves, consensus network |
| `analysis/22_figures.py` | publication figures (PNG/PDF) |
| `analysis/23_supplementary_and_docx.py` | Supplementary Table S1 and Word manuscript |
| `data/survey_metadata.csv` | per-source design, attribution, fieldwork group, communities, districts |
| `output/` | derived datasets, figures, reports |

## Not included
- **Source PDFs and their extracted text** (copyright). They are kept in a private companion repository and are available to editors and reviewers on request. `sources/` is git-ignored here.
- **Licence and data release:** to be decided with co-authors after community review (CARE principles).
