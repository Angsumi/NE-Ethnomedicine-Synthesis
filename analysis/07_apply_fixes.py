"""Apply the verified fixes and build one combined dataset (NE5 + Assam V6), without touching the originals.

Fixes:
  1. Drop sources whose PDF could not be obtained (S13, S20, S32).
  2. Keep one copy of sources present in both NE5 and V6 (the NE5 copy); add V6-only sources.
  3. Re-label tribes: S03 -> Konyak Naga, S04 -> Angami Naga, S17 -> Tripuri/Reang,
     S08 -> per-plant communities from the paper (Asm/Mor/Mis/Ben), not "Khamti".
  4. Quarantine (move to a separate sheet, not delete):
       - the 18 "Moran" records citing the Rabha paper (S16) - real source unknown
       - records whose species does not occur anywhere in the cited paper
  5. Flag (keep): reviews used as data (S15), names that differ from the paper, part/use not found nearby.

Usage: .venv/bin/python analysis/07_apply_fixes.py
Writes output/NE_combined_v1.xlsx  (sheets: Data, Quarantine, Changelog)
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"S13": "PDF not obtained", "S20": "PDF not obtained", "S32": "PDF not obtained"}
TRIBE_FIX = {"S03": "Konyak Naga", "S04": "Angami Naga", "S17": "Tripuri; Reang"}
REVIEW = {"S15"}
COMM = {"asm": "Assamese (non-tribal)", "asrn": "Assamese (non-tribal)", "mor": "Moran", "mis": "Mishing",
        "ben": "Bengali (non-tribal)"}


def letters(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def s08_communities():
    """species letters-key -> communities, parsed from the 'Local name: ... (Asm, Mor)' line of each entry."""
    txt = (ROOT / "sources/text/S08.txt").read_text(errors="ignore").split("=== RAW ===")[0]
    out = {}
    entries = re.split(r"\n\W{0,3}\d{1,3}\.\s+(?=[A-Z][a-z]+ [a-z])", txt)
    for e in entries[1:]:
        m = re.match(r"([A-Z][a-z]+ [a-z\-]+)", e)
        ln = re.search(r"Local name[s]?:([^\n]*(?:\n(?!\s*Diseases)[^\n]*)?)", e)
        if not (m and ln):
            continue
        ab = {COMM[a.lower()] for a in re.findall(r"\b(Asm|Asrn|Mor|Mis|Ben)\b", ln.group(1), flags=re.I)}
        out[letters(m.group(1))] = "; ".join(sorted(ab))
    return out


def main():
    ver = pd.read_excel(ROOT / "output/verification_report.xlsx", "Records")
    ver = ver[["Dataset", "Row", "SourceID", "Species", "status", "name_in_paper", "part_found_nearby",
               "use_found_nearby", "verdict", "found_in_other_sources"]]
    frames = []
    for name, path in [("NE5", "NE-Ethnomedicine/NE5.xlsx"), ("V6", "Assam_Ethnomedicine/V6.xlsx")]:
        d = pd.read_excel(ROOT / path)
        d.columns = [c.strip() for c in d.columns]
        d = d.rename(columns={"Parts used": "Partsused", "System Acted Upon": "ActedUpon", "Way to use": "Way to Use"})
        d["Dataset"], d["Row"] = name, range(2, len(d) + 2)
        frames.append(d)
    d = pd.concat(frames, ignore_index=True).merge(ver, on=["Dataset", "Row"], how="left")
    log = []

    # 1. excluded sources
    ex = d.SourceID.isin(EXCLUDE)
    log.append(("drop", "sources without PDF " + ", ".join(EXCLUDE), int(ex.sum())))
    d = d[~ex]

    # 2. de-duplicate shared sources: keep NE5 copy
    ne5_src = set(d.loc[d.Dataset == "NE5", "SourceID"])
    dup = (d.Dataset == "V6") & d.SourceID.isin(ne5_src)
    log.append(("drop", "V6 copies of sources already in NE5", int(dup.sum())))
    d = d[~dup].copy()
    d["Tribe_original"] = d["Tribe"]

    # 3. tribe labels
    for sid, t in TRIBE_FIX.items():
        m = d.SourceID == sid
        d.loc[m, "Tribe"] = t
        log.append(("relabel tribe", f"{sid}: {sorted(d.loc[m, 'Tribe_original'].unique())} -> {t}", int(m.sum())))
    comm = s08_communities()
    m08 = d.SourceID == "S08"
    d.loc[m08, "Tribe"] = d.loc[m08, "Species"].map(lambda s: comm.get(letters(s), "")).replace("", "UNRESOLVED")
    log.append(("relabel tribe", f"S08: 'Khamti' -> communities from paper ({len(comm)} entries parsed)", int(m08.sum())))

    # 4. quarantine
    d["qc_reason"] = ""
    moran = (d.SourceID == "S16") & (d.Tribe_original == "Moran")
    d.loc[moran, "qc_reason"] = "Moran records cite Rabha paper (S16); real source missing"
    nf = (d.status == "not_found") & ~moran
    d.loc[nf, "qc_reason"] = "species not found anywhere in cited paper"
    q = d.qc_reason != ""
    log.append(("quarantine", "S16 Moran records (wrong source)", int(moran.sum())))
    log.append(("quarantine", "species not found in cited paper", int(nf.sum())))

    # 5. flags on kept records
    d["qc_flag"] = ""
    d.loc[d.SourceID.isin(REVIEW), "qc_flag"] = "secondary source (review)"
    d.loc[d.status.isin(["genus_only", "epithet_only"]), "qc_flag"] += "; name differs from paper - check"
    d.loc[(d.part_found_nearby == False), "qc_flag"] += "; part not confirmed"
    d.loc[(d.use_found_nearby == False), "qc_flag"] += "; use not confirmed"
    d.loc[m08 & (d.Tribe == "UNRESOLVED"), "qc_flag"] += "; S08 community unresolved"
    d["qc_flag"] = d.qc_flag.str.strip("; ")

    master = pd.read_csv(ROOT / "output/source_master.csv")[["SourceID", "reference"]]
    d = d.merge(master, on="SourceID", how="left")
    q = (d.qc_reason != "").values
    d["Reference"] = d["reference"]
    keep = ["SourceID", "Dataset", "Row", "Botanical Name", "Family Name", "Common Name", "Partsused", "Disease",
            "ActedUpon", "Way to Use", "Tribe", "Tribe_original", "State", "Reference", "status", "name_in_paper",
            "qc_flag", "qc_reason", "found_in_other_sources"]
    data, quar = d.loc[~q, keep], d.loc[q, keep]
    data = data.sort_values(["SourceID", "Dataset", "Row"])
    out = ROOT / "output/NE_combined_v1.xlsx"
    with pd.ExcelWriter(out) as xw:
        data.to_excel(xw, sheet_name="Data", index=False)
        quar.to_excel(xw, sheet_name="Quarantine", index=False)
        pd.DataFrame(log, columns=["action", "detail", "records"]).to_excel(xw, sheet_name="Changelog", index=False)
    for a in log:
        print(f"{a[0]:15} {a[2]:5}  {a[1]}")
    print(f"\nData: {len(data)} records, {data.SourceID.nunique()} sources | Quarantine: {len(quar)}")
    print("Flags:", data.qc_flag.replace("", "none").str.split("; ").explode().value_counts().to_dict())
    print("S08 tribes:", data[data.SourceID == "S08"].Tribe.value_counts().to_dict())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
