"""Check every record of NE5 and Assam V6 against the text of its source paper.

For each record: is the species in the paper? (exact / fuzzy / genus-only / not found),
and near where it is mentioned, do the part used and the disease words appear?
For each paper: which binomials in the paper are NOT in the dataset (candidate omissions).

Usage: .venv/bin/python analysis/06_verify_against_papers.py
Reads  NE-Ethnomedicine/NE5.xlsx, Assam_Ethnomedicine/V6.xlsx, output/source_master.csv, sources/text/*.txt
Writes output/verification_report.xlsx
"""
import difflib, importlib.util, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("clean", ROOT / "analysis/01_clean.py")
clean = importlib.util.module_from_spec(spec); spec.loader.exec_module(clean)

EXCLUDED = {"S13": "PDF not obtained", "S20": "PDF not obtained", "S32": "PDF not obtained"}
PART_WORDS = {
    "Leaf": ["leaf", "leaves", "foliage"], "Fruit": ["fruit", "pulp", "rind", "peel", "pod"], "Root": ["root"],
    "Bark": ["bark"], "Seed": ["seed", "grain", "nut", "kernel"], "Whole plant": ["whole", "entire", "plant"],
    "Stem": ["stem", "wood", "stalk"], "Shoot/twig": ["shoot", "twig", "tender", "culm"],
    "Flower/inflorescence": ["flower", "inflorescence", "bud", "spike"], "Rhizome": ["rhizome"],
    "Tuber/bulb": ["tuber", "bulb", "corm"], "Latex/exudate": ["latex", "sap", "gum", "oil", "juice", "resin"],
    "Aerial part": ["aerial"], "Other": [],
}
AUTH = r"(?:L\.|Linn|Roxb|Wall|DC\.|Benth|Hook|Willd|Lam\.|Retz|Burm|Blume|Sm\.|Jacq|Mill\.|Merr|Kurz|Buch|Ham|Gaertn|Schott|Nees|Pers|Spreng|Thunb|Lour|Hassk|Kunth|Engl|Desv|Schum|Sw\.|Wight|Arn|Gamble|Kuntze|Ridl|Royle|Don|Moon|Rottl|Vahl|Clarke|Griff|Dunn|Craib|Koenig|Rosc|Nakai|Steud|Br\.|Juss|Miq|Mart|Planch|Pierre|Gagnep|Cogn|Decne|Haines|Prain)"
NOT_GENUS = {"The", "This", "These", "Table", "Fig", "India", "Assam", "Department", "Journal", "University", "Plant",
             "Plants", "Local", "Family", "Botanical", "Common", "Leaves", "Leaf", "Root", "Fruit", "Bark", "Used",
             "Vol", "From", "District", "North", "East", "South", "West", "Northeast", "Indian", "Village", "State"}


def letters(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def norm_ref(s):
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


def load_records():
    out = []
    for name, path in [("NE5", "NE-Ethnomedicine/NE5.xlsx"), ("V6", "Assam_Ethnomedicine/V6.xlsx")]:
        d = pd.read_excel(ROOT / path)
        d.columns = [c.strip() for c in d.columns]
        d = d.rename(columns={"Parts used": "Partsused", "System Acted Upon": "ActedUpon", "Way to use": "Way to Use"})
        d["Dataset"] = name
        d["Row"] = range(2, len(d) + 2)        # Excel row number
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    d["Reference"] = d["Reference"].map(norm_ref)
    d["Species"] = (d["Botanical Name"].astype(str).str.upper().str.strip().str.replace(r"\s+", " ", regex=True)
                    .replace(clean.NAME_FIX).str.capitalize())
    d["PartCats"] = d["Partsused"].map(clean.map_parts)
    return d


class Paper:
    def __init__(self, text):
        self.raw = text
        self.flat = letters(text)
        self.low = re.sub(r"\s+", " ", text.lower())

    def find(self, species):
        g, *rest = species.lower().split()
        e = rest[0] if rest else ""
        if letters(g + e) in self.flat:
            return "exact", species
        gl = letters(g)
        best, hit = 0, None
        for m in re.finditer(gl, self.flat):
            cand = self.flat[m.end(): m.end() + len(letters(e)) + 2]
            r = difflib.SequenceMatcher(None, letters(e), cand[: len(letters(e))]).ratio()
            if r > best: best, hit = r, cand
        if best >= 0.8:
            return "fuzzy", f"{g} {hit}"
        if len(gl) >= 4 and gl in self.flat:
            return "genus_only", g
        if letters(e) and len(letters(e)) >= 6 and letters(e) in self.flat:
            return "epithet_only", e
        return "not_found", ""

    def window(self, species, size=600):
        """Text after every mention of the species (all occurrences joined), so table rows are covered."""
        g, *rest = species.lower().split()
        pat = re.escape(g) + r"\W{0,6}" + re.escape((rest or [""])[0][:4])
        ms = list(re.finditer(pat, self.low))[:12] or list(re.finditer(re.escape(g), self.low))[:6]
        return " ".join(self.low[m.start(): m.start() + size] for m in ms)

    def binomials(self, known_genera):
        out = set()
        for m in re.finditer(r"\b([A-Z][a-z]{2,})\s+([a-z]{3,}(?:-[a-z]+)?)\b(.{0,40})", self.raw.replace("\n", " ")):
            g, e, tail = m.groups()
            if g in NOT_GENUS or e in {"and", "the", "for", "used", "with", "plant", "species", "district", "tribe"}:
                continue
            if g.lower() in known_genera or re.match(r"\s*\(?[A-Z]?[a-z]*\.?\)?\s*" + AUTH, tail):
                out.add(f"{g} {e}")
        return out


def main():
    d = load_records()
    master = pd.read_csv(ROOT / "output/source_master.csv")
    sid_of = dict(zip(master["reference"].map(norm_ref), master["SourceID"]))
    d["SourceID"] = d["Reference"].map(sid_of)
    known_genera = {s.split()[0].lower() for s in d["Species"]}
    papers = {}
    for sid in master["SourceID"]:
        p = ROOT / f"sources/text/{sid}.txt"
        if p.exists():
            papers[sid] = Paper(p.read_text(errors="ignore"))

    rows = []
    for r in d.itertuples():
        P = papers.get(r.SourceID)
        if P is None:
            rows.append(dict(status="no_pdf")); continue
        status, matched = P.find(r.Species)
        win = P.window(r.Species) if status in ("exact", "fuzzy") else ""
        parts = [p for p in r.PartCats if p in PART_WORDS]
        part_ok = (any(w in win for p in parts for w in PART_WORDS[p]) if win and parts else None)
        dwords = [w for w in re.findall(r"[a-z]{5,}", str(r.Disease).lower()) if w not in {"problem", "problems", "disease", "diseases", "treatment"}]
        use_ok = (any(w[:6] in win for w in dwords) if win and dwords else None)
        rows.append(dict(status=status, name_in_paper=matched, part_found_nearby=part_ok, use_found_nearby=use_ok))
    v = pd.concat([d.reset_index(drop=True), pd.DataFrame(rows)], axis=1)

    # where else does a missing species occur? (helps find the real source of misattributed records)
    extra = {p.stem: Paper(p.read_text(errors="ignore")) for p in (ROOT / "sources/text").glob("X*.txt")}
    allp = {**papers, **extra}
    def elsewhere(r):
        if r.status not in ("not_found", "epithet_only", "genus_only"):
            return ""
        key = letters(r.Species)
        return ", ".join(s for s, P in allp.items() if s != r.SourceID and key in P.flat)
    v["found_in_other_sources"] = v.apply(elsewhere, axis=1)

    def flag(x):
        if x.status == "no_pdf": return "excluded (no PDF)"
        if x.status in ("not_found", "epithet_only"): return "NOT IN PAPER - check/remove"
        if x.status == "genus_only": return "name differs (synonym/typo?) - check"
        if x.part_found_nearby is False and x.use_found_nearby is False: return "species ok, part & use not found nearby - check"
        if x.part_found_nearby is False: return "species ok, part not found nearby - check"
        if x.use_found_nearby is False: return "species ok, use not found nearby - check"
        return "ok"
    v["verdict"] = v.apply(flag, axis=1)

    # candidate omissions: binomials in paper not represented in that source's records
    omis = []
    for sid, P in papers.items():
        have = {letters(s) for s in d.loc[d.SourceID == sid, "Species"]}
        have_g = {s.split()[0].lower() for s in d.loc[d.SourceID == sid, "Species"]}
        for b in sorted(P.binomials(known_genera)):
            lb = letters(b)
            if lb in have or any(difflib.SequenceMatcher(None, lb, h).ratio() > 0.85 for h in have):
                continue
            omis.append(dict(SourceID=sid, binomial_in_paper=b, genus_in_dataset_for_source=b.split()[0].lower() in have_g))
    omis = pd.DataFrame(omis)

    # paper-level summary
    summ = []
    for r in master.itertuples():
        sub = v[v.SourceID == r.SourceID]
        P = papers.get(r.SourceID)
        claim = ""
        if P is not None:
            m = re.search(r"(\d{2,3})\s+(?:\w+\s+){0,3}(?:plant\s+)?(?:species|plants|taxa)", P.low[:6000])
            claim = m.group(0) if m else ""
        vc = sub["verdict"].value_counts()
        summ.append(dict(SourceID=r.SourceID, reference=r.reference[:120], pdf=P is not None,
                         excluded=EXCLUDED.get(r.SourceID, ""), records_NE5=(sub.Dataset == "NE5").sum(),
                         records_V6=(sub.Dataset == "V6").sum(), paper_claims=claim,
                         ok=vc.get("ok", 0), not_in_paper=vc.get("NOT IN PAPER - check/remove", 0),
                         name_differs=vc.get("name differs (synonym/typo?) - check", 0),
                         part_or_use_check=sum(vc.get(k, 0) for k in vc.index if k.startswith("species ok")),
                         candidate_omissions=(omis.SourceID == r.SourceID).sum() if len(omis) else 0))
    summ = pd.DataFrame(summ)

    cols = ["Dataset", "Row", "SourceID", "Tribe", "Botanical Name", "Species", "name_in_paper", "status",
            "Partsused", "part_found_nearby", "Disease", "use_found_nearby", "verdict", "found_in_other_sources"]
    out = ROOT / "output/verification_report.xlsx"
    with pd.ExcelWriter(out) as xw:
        summ.to_excel(xw, sheet_name="Summary", index=False)
        v[cols].to_excel(xw, sheet_name="Records", index=False)
        v[cols][~v.verdict.isin(["ok", "excluded (no PDF)"])].to_excel(xw, sheet_name="Records_to_check", index=False)
        omis.to_excel(xw, sheet_name="Candidate_omissions", index=False)
    pd.set_option("display.width", 250)
    print(summ.drop(columns=["reference"]).to_string(index=False))
    print("\nVerdicts:\n", v.groupby(["Dataset", "verdict"]).size().to_string())
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
