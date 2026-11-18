"""Merge the verified v1 data with records from newly added sources -> output/NE_combined_v2.xlsx.

Usage: .venv/bin/python analysis/09_merge_v2.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
v1 = pd.read_excel(ROOT / "output/NE_combined_v1.xlsx", sheet_name=None)
new = pd.read_excel(ROOT / "output/new_sources_extracted.xlsx", sheet_name=None)
n = new["Records"].copy()
n["Dataset"] = "NEW"
n["Row"] = range(2, len(n) + 2)
n["Tribe_original"] = n["Tribe"]
n["status"] = "extracted_from_paper"
n["qc_flag"] = "ActedUpon auto-assigned from disease text"
n.loc[n.SourceID == "N10", "qc_flag"] += "; non-ST community (Bishnupriya Manipuri)"
n.loc[n.SourceID == "N05", "qc_flag"] += "; single-ailment study (bone fracture)"
data = pd.concat([v1["Data"], n[[c for c in v1["Data"].columns if c in n.columns] + ["parts_as_in_paper"]]],
                 ignore_index=True)
log = pd.concat([v1["Changelog"], pd.DataFrame(
    [("add source", f"{r.SourceID}: {r.reference[:90]}", int((n.SourceID == r.SourceID).sum()))
     for r in new["Sources"].itertuples() if (n.SourceID == r.SourceID).any()],
    columns=["action", "detail", "records"])], ignore_index=True)
not_added = pd.DataFrame([
    ("N01", "Moran - Borah, reproductive health (Neliti)", "download blocked - get PDF manually"),
    ("N02", "Reang - Shil & Dutta Choudhury 2009 (CORE)", "download blocked - get PDF manually"),
    ("N04", "Garo - Marak & Lalnundanga 2019 (Science Vision)", "site certificate error - get PDF manually"),
    ("N11", "Tripura tribes - AJTCAM", "download blocked - get PDF manually"),
    ("N12", "Ao Naga diabetes - Pegu et al. 2024, Plant Science Today", "plant list is in Supplementary Table 1 (not in PDF)"),
], columns=["ID", "paper", "reason"])
out = ROOT / "output/NE_combined_v2.xlsx"
with pd.ExcelWriter(out) as xw:
    data.to_excel(xw, sheet_name="Data", index=False)
    v1["Quarantine"].to_excel(xw, sheet_name="Quarantine", index=False)
    log.to_excel(xw, sheet_name="Changelog", index=False)
    new["Sources"].to_excel(xw, sheet_name="New_sources", index=False)
    not_added.to_excel(xw, sheet_name="Not_yet_added", index=False)
print(f"v1 {len(v1['Data'])} + new {len(n)} = {len(data)} records; wrote {out}")
