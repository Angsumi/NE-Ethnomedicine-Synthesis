"""Screening list: studies in Jha & Smith-Hall (2023) that are not yet in our corpus, with full citation and search links.

Full citations come from the review's Literature Cited (matched by first-author surname + year).
Usage: .venv/bin/python analysis/24_unscreened_links.py
Writes output/screening_list.csv, docs/SCREENING_LIST.md
"""
import re, urllib.parse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def references():
    t = (ROOT / "sources/reviews/JhaSmithHall2023.txt").read_text(errors="ignore").splitlines()
    # the review has two reference lists (main text and supplementary tables): read every paragraph after Literature Cited
    a = next(i for i, l in enumerate(t) if l.strip() == "Literature Cited")
    refs, cur = [], []
    for l in t[a + 1:]:
        if l.startswith("   ") and not cur:      # table rows are indented; references start at column 0
            continue
        if re.match(r"^\s*\d+\s*$", l) or "Ethnobotany Research and Applications" in l:
            continue
        if not l.strip():
            if cur: refs.append(" ".join(cur)); cur = []
        else:
            cur.append(l.strip())
    if cur: refs.append(" ".join(cur))
    out = []
    for r in refs:
        m = re.match(r"^([A-Z][A-Za-z'\- ]+?)\s+[A-Z]{1,4}[,.]?.*?\b((?:19|20)\d{2})[a-z]?\.\s*(.*)$", r)
        if not m: continue
        surname, year, rest = m.group(1).split()[-1], m.group(2), m.group(3)
        title = re.split(r"\.\s", rest, maxsplit=1)[0]
        doi = (re.search(r"(10\.\d{4,9}/[^\s]+)", r) or [None, ""])[1].rstrip(".")
        out.append(dict(key=re.sub(r"[^a-z]", "", surname.lower()) + year, full_reference=r, title=title, doi=doi))
    return pd.DataFrame(out)


def main():
    cw = pd.read_csv(ROOT / "output/jha2023_study_crosswalk.csv")
    js = cw[(cw.side == "Jha2023") & (cw.in_our_corpus == False)].copy()
    refs = references()
    js = js.merge(refs.drop_duplicates("key"), on="key", how="left")
    js["in_scope"] = js.state.ne("Sikkim")
    def link(r):
        if isinstance(r.doi, str) and r.doi:
            return f"https://doi.org/{r.doi}"
        q = f'"{r.title}"' if isinstance(r.title, str) and len(r.title) > 15 else f"{r.first_author} {int(float(r.year))} ethnomedicinal {r.state}"
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(q + " pdf")
    js["link"] = js.apply(link, axis=1)
    js = js.sort_values(["in_scope", "state", "year"], ascending=[False, True, True])
    js["ScreenID"] = [f"J{i:03d}" for i in range(1, len(js) + 1)]
    cols = ["ScreenID", "state", "citation", "full_reference", "doi", "link", "in_scope"]
    js[cols].to_csv(ROOT / "output/screening_list.csv", index=False)

    lines = ["# Studies to screen (from Jha & Smith-Hall 2023, not yet in our corpus)", "",
             "For each study decide: is it a primary field survey of medicinal plants from the 7 states, with community named and plants",
             "identified to species? If yes and the full text can be obtained, save it as `sources/gap/<ScreenID>.pdf`.",
             "Sikkim studies are listed last and are outside the 7-state scope.", ""]
    for st, g in js.groupby("state", sort=False):
        lines += [f"## {st} ({len(g)})", "", "| ID | Study | Link |", "|---|---|---|"]
        for r in g.itertuples():
            ref = (r.full_reference if isinstance(r.full_reference, str) else r.citation).replace("|", "/")
            lines.append(f"| {r.ScreenID} | {ref[:220]} | [{'DOI' if 'doi.org' in r.link else 'search'}]({r.link}) |")
        lines.append("")
    (ROOT / "docs/SCREENING_LIST.md").write_text("\n".join(lines))
    print(f"{len(js)} studies; in scope {int(js.in_scope.sum())}; with full reference {int(js.full_reference.notna().sum())}; with DOI {int((js.doi.fillna('') != '').sum())}")
    print(js.state.value_counts().to_dict())


if __name__ == "__main__":
    main()
