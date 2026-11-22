#!/usr/bin/env bash
# Reproduce the paper analyses from the released evidence tables and caches.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
"$PY" analysis/15_recurrence.py
"$PY" analysis/17_availability.py
"$PY" analysis/20_similarity.py
"$PY" analysis/21_completeness_network.py
"$PY" analysis/22_figures.py
"$PY" analysis/23_supplementary_and_docx.py
