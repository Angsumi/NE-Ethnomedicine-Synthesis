#!/usr/bin/env bash
# Rebuild everything from the two input datasets and the (locally held) source texts.
# Source PDFs/texts are not redistributed; scripts 06-12 need them under sources/.
set -euo pipefail
PY=${PY:-.venv/bin/python}
$PY analysis/01_clean.py NE-Ethnomedicine/NE5.xlsx output/NE_clean.xlsx
$PY analysis/06_verify_against_papers.py
$PY analysis/07_apply_fixes.py
$PY analysis/08_extract_new.py
$PY analysis/09_merge_v2.py
$PY analysis/11_extract_gap.py
$PY analysis/12_merge_v3.py
$PY analysis/01_clean.py output/NE_combined_v3.xlsx output/NE_combined_v3_summary.xlsx
$PY analysis/10_coverage.py
$PY analysis/14_taxonomy_gbif.py
$PY analysis/13_evidence_units.py
$PY analysis/15_recurrence.py
$PY analysis/16_pilot_trace.py
$PY analysis/17_availability.py
$PY analysis/18_crosswalk_jha2023.py
$PY analysis/19_geocode_districts.py
$PY analysis/20_similarity.py
$PY analysis/21_completeness_network.py
$PY analysis/22_figures.py
$PY analysis/23_supplementary_and_docx.py
$PY analysis/24_unscreened_links.py
