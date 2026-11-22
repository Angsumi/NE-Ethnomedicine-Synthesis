# NE India ethnomedicine: paper and reproducibility

Authors: Angsuman Das and Ananda Prasad.
Archive: https://doi.org/10.5281/zenodo.24332943

## Paper files

- `docs/manuscript/manuscript.docx`: Word manuscript with figures.
- `docs/manuscript/manuscript.md`: editable manuscript source.
- `docs/manuscript/Table_S1_sources.csv`: supplementary source table.
- `output/figures/pub/`: publication figures in PDF and PNG.
- `docs/METHODS.md`: methods specification; planned steps must be distinguished from completed work.
- `docs/SCREENING_LIST.md` and `output/screening_list.csv`: screening record.
- `docs/DATA_DICTIONARY.md`: data definitions.

## Reproduce the analyses

From the repository root, using Python 3:

```bash
python3 -m venv /tmp/ne-paper-venv
/tmp/ne-paper-venv/bin/python -m pip install -r requirements.txt
PY=/tmp/ne-paper-venv/bin/python bash run_all.sh
```

The runner starts from the released `output/evidence_units.csv`, combined workbook,
metadata, and cached taxonomy, geography, and GBIF occurrence data. It rebuilds
recurrence, availability, similarity, completeness, networks, publication figures,
the supplementary source table, and the Word manuscript. It overwrites derived
results and manuscript.docx. Dependencies are currently unpinned; identical results
across library versions have not been established. Availability code may contact
GBIF if a cache entry is missing.

## Data and provenance

`output/NE_combined_v3.xlsx` is the consolidated corpus. `output/evidence_records.csv`
and `output/evidence_units.csv` preserve the coded records and independent reports,
including released source-verification flags. All existing tabular data, intermediate
workbooks, and the authors' checked `output/pilot_trace.xlsx` are retained so that
extraction and corrections remain traceable. `output/VERIFICATION_REPORT.md` records
verification decisions.

`analysis/01_clean.py` and scripts 06–14 document corpus construction;
16 documents the pilot; 18 documents the review crosswalk; 19 documents geocoding.
These are provenance and optional reconstruction steps, excluded from the default
runner because some require source texts or external services. Rebuilding evidence
with script 13 without the original texts would change source-verification flags.
The checked pilot and review crosswalk are supplied as released inputs.

For reconstruction from the original upstream datasets, `scripts/fetch_inputs.sh`
fetches the two source repositories. Their separate Git histories are not needed
for the default analysis. Source PDFs and extracted texts are not distributed;
full extraction and source-text verification therefore cannot be reproduced from
this repository alone.

Code: MIT; data, figures, and documents: CC BY 4.0, as specified in `LICENSE`.
Citation metadata is in `CITATION.cff` and `.zenodo.json`.
