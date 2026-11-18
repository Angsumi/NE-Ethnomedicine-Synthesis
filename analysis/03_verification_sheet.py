"""Build output/NE_verification.xlsx: a per-source and per-record checklist for checking NE5
against the original papers.

Usage: .venv/bin/python analysis/03_verification_sheet.py output/NE_clean.xlsx output/sources_crossref.csv output/NE_verification.xlsx
"""
import sys
import pandas as pd

# Problems found so far, by reference prefix (from reading the data + Crossref lookup).
SOURCE_ISSUES = {
    "Kala, C. P.": ("doi_confirmed", "", "Primary field study. Check 157 records vs species table in paper."),
    "Laldingliani": ("doi_confirmed", "", "Primary field study (JEE, open access). Check 93 records vs Table."),
    "Konyak, Z.": ("not_found", "Tribe label 'Naga' -> should be 'Konyak' (Mon district).",
                   "Crossref matched a different Konyak 2021 Plant Archives paper (bamboos); confirm title/pages. "
                   "'Underutilized' plants may include non-medicinal uses."),
    "Chase, P.": ("not_found", "Tribe label 'Naga' -> should be 'Angami'.", "Find PDF; journal has no DOI."),
    "Bhuyan, A.": ("not_found", "", "Find PDF (IJAR, open access)."),
    "Bairagi, Juli": ("not_found", "", "Reference incomplete: journal, volume, pages missing."),
    "Borah, S.": ("doi_confirmed", "", "Open access (HRPUB)."),
    "Baishya, A. K.": ("doi_confirmed", "Tribe label 'Khamti' for all 53 records, but the paper is a CROSS-COMMUNITY "
                       "study of Dibru-Saikhowa (several communities). Re-assign tribe per record from the paper.", ""),
    "Hynniewta": ("not_found", "", "Reference incomplete: journal, volume, pages missing (likely Indian J Trad Knowl 2008)."),
    "Sharma, B. M.": ("not_found", "", "Book chapter (Recent Progress in Medicinal Plants 7); needs physical/PDF copy."),
    "Bordoloi, R.": ("not_found", "", "Find PDF (AJST, open access)."),
    "Das, A. K., & Tag": ("not_found", "", "Reference incomplete: journal, volume, pages missing (likely Indian J Trad Knowl 2006)."),
    "Basumatary, N.": ("not_found", "", "Find PDF."),
    "Jaiswal, V.": ("not_found", "SECONDARY SOURCE ('mini review'). Its plants may duplicate primary studies; "
                    "replace with the primary Jaintia study it cites, or flag as review.",
                    "Reference incomplete (likely Indian J Trad Knowl 2010)."),
    "Kutum, A.": ("not_found", "", "Find PDF (CIBTech, open access)."),
    "ADHIKARY, P.": ("not_found", "18 records (RecordID 462-479) are tribe 'Moran' but cite this Rabha paper -> "
                     "the Moran source reference is missing/wrong.", "Fix citation text ('94-to')."),
    "Das, H. B.": ("not_found", "Tribe label 'Kokborok' is a language; paper covers Tripuri and Reang tribes.",
                   "Reference incomplete (likely Indian J Trad Knowl 2009)."),
    "Baruah, S.": ("not_found", "Tribe label 'Adi' -> 'Adi-Minyong' (sub-tribe)", "Reference incomplete (likely Indian J Trad Knowl 2013)."),
    "Moyong, S.": ("not_found", "", "Reference incomplete: year, journal missing."),
    "Nath, M.": ("not_found", "", "Find PDF (AUJST)."),
    "Ratan, O.": ("not_found", "", "Pleione 10(2) - has DOI prefix 10.26679; search directly."),
    "Sharma, C.": ("not_found", "", "Find PDF."),
    "Tripathi, A. K.": ("doi_confirmed", "", ""),
    "Gibji, N.": ("not_found", "", "Science and Culture 77; find PDF."),
    "Das, R. J.": ("not_found", "", "Find PDF (IJHM, open access)."),
    "Rinyo, R.": ("doi_confirmed", "", "Only 8 records taken - check whether the paper lists more medicinal plants."),
}


def lookup(ref):
    for k, v in SOURCE_ISSUES.items():
        if ref.startswith(k):
            return v
    return ("not_found", "", "")


def main(clean, crossref, dst):
    d = pd.read_excel(clean, "Records_clean")
    cr = pd.read_csv(crossref)
    src = d.groupby("Reference").agg(
        first_record=("RecordID", "min"), records=("RecordID", "size"),
        state=("State", lambda s: "; ".join(s.unique())), tribe_in_data=("Tribe", lambda s: "; ".join(s.unique())),
    ).reset_index().merge(cr[["reference", "doi", "cr_title", "score"]], left_on="Reference", right_on="reference", how="left")
    src[["doi_status", "data_problem", "todo"]] = src["Reference"].map(lookup).apply(pd.Series)
    src.loc[src.doi_status != "doi_confirmed", "doi"] = ""
    src = src.drop(columns=["reference", "cr_title", "score"]).sort_values("first_record")
    src.insert(0, "SourceID", [f"S{i:02d}" for i in range(1, len(src) + 1)])
    src["pdf_in_hand"] = ""            # Y/N
    src["study_type"] = ""             # primary field survey / review / book chapter
    src["species_in_paper"] = ""       # number of medicinal species the paper reports
    src["include"] = ""                # Y/N per inclusion criteria

    sid = dict(zip(src.Reference, src.SourceID))
    rec = d[["RecordID", "Reference", "Botanical Name", "Species", "Family", "Common Name", "Partsused",
             "Disease", "ActedUpon", "Tribe", "State"]].copy()
    rec.insert(1, "SourceID", rec.pop("Reference").map(sid))
    for c in ["found_in_paper (Y/N)", "page_or_table", "name_as_in_paper", "part_ok", "use_ok",
              "tribe_ok", "correction", "checked_by"]:
        rec[c] = ""
    # pre-fill known tribe problems
    rec.loc[rec.RecordID.between(462, 479), "correction"] = "Moran records cite Rabha paper: find real source"
    rec.loc[rec.SourceID == sid[next(r for r in sid if r.startswith("Baishya"))], "tribe_ok"] = "CHECK (cross-community study)"

    with pd.ExcelWriter(dst) as xw:
        src.to_excel(xw, sheet_name="Sources", index=False)
        rec.to_excel(xw, sheet_name="Records_to_verify", index=False)
    print(src[["SourceID", "records", "tribe_in_data", "doi_status", "data_problem"]].to_string(max_colwidth=60))
    print(f"\nWrote {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
