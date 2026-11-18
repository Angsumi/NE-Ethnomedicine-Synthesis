"""Crosswalk with Jha & Smith-Hall 2023 (Ethnobotany Research and Applications 26:7; 255 publications on NE India).

1. Bibliography: their Supplementary Table 1 (study list, author-year) vs our sources -> overlap, studies they
   reviewed that we have not screened (candidate additions), and our sources absent from their review.
2. Species: their Supplementary Table 2 gives, per species, the number of indigenous groups using it (any use).
   We compare that with our independent community reports at species level and at species x specific-condition level,
   to show how much 'popularity' shrinks when agreement must be on the same use.

Usage: .venv/bin/python analysis/18_crosswalk_jha2023.py
Reads sources/reviews/JhaSmithHall2023.txt (PDF text, not redistributed), output/evidence_units.csv
Writes output/jha2023_study_crosswalk.csv, output/jha2023_species_comparison.csv
"""
import re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
T = (ROOT / "sources/reviews/JhaSmithHall2023.txt").read_text(errors="ignore").splitlines()


def section(start, end):
    a = next(i for i, l in enumerate(T) if l.startswith(start))
    b = next((i for i, l in enumerate(T) if i > a and l.startswith(end)), len(T))
    return T[a:b]


def key(author, year):
    return f"{re.sub(r'[^a-z]', '', author.lower())}{year}"


def main():
    # ---- 1. study list ----
    st1 = section("Supplementary Table 1.", "Supplementary Table 2.")
    studies, state = [], None
    for l in st1:
        s = re.match(r"^\s*(Arunachal Pradesh|Assam|Manipur|Meghalaya|Mizoram|Nagaland|Sikkim|Tripura);", l)
        if s: state = s.group(1)
        m = re.search(r"([A-Z][A-Za-z'\-]+)(?:\s+(?:&|and)\s+[A-Z][A-Za-z'\-]+|\s+et al\.)?\s+(\d{4})[a-z]?\s*$", l)
        if m:
            studies.append(dict(state=state, citation=m.group(0).strip(), first_author=m.group(1), year=m.group(2), key=key(m.group(1), m.group(2))))
    js = pd.DataFrame(studies).drop_duplicates("citation")
    meta = pd.read_csv(ROOT / "data/survey_metadata.csv")
    d = pd.read_excel(ROOT / "output/NE_combined_v3.xlsx", "Data")
    refs = d.groupby("SourceID").Reference.first()
    ours = []
    for sid, ref in refs.items():
        ref = str(ref)
        a = re.match(r"\s*([A-Za-z'\-]+)", ref)
        y = re.search(r"\((\d{4})\)|\b(19|20)\d{2}\b", ref)
        yr = (y.group(1) or y.group(0)) if y else ""
        ours.append(dict(source_id=sid, first_author=a.group(1).capitalize() if a else "", year=yr, key=key(a.group(1), yr) if a else "", reference=ref[:140]))
    ours = pd.DataFrame(ours)
    js["in_our_corpus"] = js.key.isin(ours.key)
    ours["in_jha2023"] = ours.key.isin(js.key)
    cross = pd.concat([js.assign(side="Jha2023"), ours.assign(side="ours")], ignore_index=True)
    cross.to_csv(ROOT / "output/jha2023_study_crosswalk.csv", index=False)
    print(f"Jha & Smith-Hall study rows parsed: {len(js)} (paper reports 255) | ours: {len(ours)}")
    print(f"overlap: {int(js.in_our_corpus.sum())} | theirs not in ours (screen these): {int((~js.in_our_corpus).sum())} | ours not in theirs: {int((~ours.in_jha2023).sum())}")
    print("their studies by state, not yet in ours:", js[~js.in_our_corpus].state.value_counts().to_dict())

    # ---- 2. species comparison ----
    st2 = section("Supplementary Table 2.", "zzzz")
    rows, cur = [], None
    for i, l in enumerate(st2):
        m = re.match(r"^\s{0,4}(Very high|High|Moderate|Medium|Low|Very low|Rare)?\s*(frequency use)?\s{2,}([A-Z][a-z]+)(?: ([a-z][a-z\-]+))?", l)
        if m and m.group(1) and l.find(m.group(3)) < 32:
            if cur: rows.append(cur)
            epi = m.group(4)
            if not epi and i + 1 < len(st2):   # genus on this line, epithet on the next ("Clerodendron" / "colebrookianum Walp.")
                col = l.find(m.group(3))
                e = re.match(r"\s*([a-z][a-z\-]+)", st2[i + 1][col:col + 30])
                epi = e.group(1) if e else ""
            cur = {"species_in_review": f"{m.group(3)} {epi}".strip(), "category": m.group(1), "n_groups": None}
        if cur and cur["n_groups"] is None:
            n = re.match(r"^\s{0,4}\((\d+)\)", l)
            if n: cur["n_groups"] = int(n.group(1))
    if cur: rows.append(cur)
    jsp = pd.DataFrame(rows).dropna(subset=["n_groups"]).drop_duplicates("species_in_review")
    # resolve their names through the same GBIF backbone so synonyms line up with ours
    import importlib.util
    spec = importlib.util.spec_from_file_location("tax", ROOT / "analysis/14_taxonomy_gbif.py")
    tx = importlib.util.module_from_spec(spec); spec.loader.exec_module(tx)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex:
        res = dict(zip(jsp.species_in_review, ex.map(lambda n: tx.match(n).get("accepted_species"), jsp.species_in_review)))
    jsp["species"] = jsp.species_in_review.map(res).fillna(jsp.species_in_review)
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    A = u[(u.is_primary == 1) & (u.condition != "unspecified/other")].assign(report=lambda x: x.fieldwork_group + "|" + x.community)
    sp_any = A.groupby("taxon").report.nunique()
    pair = A.groupby(["taxon", "condition"]).report.nunique()
    top_pair = pair.groupby("taxon").max()
    top_cond = pair.groupby("taxon").idxmax().map(lambda t: t[1])
    n_cond = A.groupby("taxon").condition.nunique()
    jsp["our_reports_any_use"] = jsp.species.map(sp_any)
    jsp["our_reports_best_specific_use"] = jsp.species.map(top_pair)
    jsp["best_specific_use"] = jsp.species.map(top_cond)
    jsp["n_distinct_conditions"] = jsp.species.map(n_cond)
    jsp["share_agreeing_on_best_use"] = (jsp.our_reports_best_specific_use / jsp.our_reports_any_use).round(2)
    jsp.to_csv(ROOT / "output/jha2023_species_comparison.csv", index=False)
    both = jsp.dropna(subset=["our_reports_any_use"])
    rho1 = stats.spearmanr(both.n_groups, both.our_reports_any_use)[0]
    rho2 = stats.spearmanr(both.n_groups, both.our_reports_best_specific_use)[0]
    print(f"\nTheir species with group counts: {len(jsp)}; matched to ours: {len(both)}")
    print(f"Spearman (their group count vs our any-use reports) = {rho1:.2f}; vs our best same-use reports = {rho2:.2f}")
    print(both.sort_values("n_groups", ascending=False).head(20)[["species", "n_groups", "our_reports_any_use", "best_specific_use",
          "our_reports_best_specific_use", "n_distinct_conditions", "share_agreeing_on_best_use"]].to_string(index=False))


if __name__ == "__main__":
    main()
