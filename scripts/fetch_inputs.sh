#!/usr/bin/env bash
# Fetch the two input datasets this synthesis starts from.
set -euo pipefail
[ -d NE-Ethnomedicine ] || git clone https://github.com/axomrank/NE-Ethnomedicine.git
[ -d Assam_Ethnomedicine ] || git clone https://github.com/Angsumi/Assam_Ethnomedicine.git
