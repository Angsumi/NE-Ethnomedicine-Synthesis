"""Build Supplementary Table S1 (source list with design metadata) and a .docx of the manuscript with figures.
Usage: .venv/bin/python analysis/23_supplementary_and_docx.py
Writes docs/manuscript/Table_S1_sources.csv, docs/manuscript/manuscript.docx
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs/manuscript"


def table_s1():
    d = pd.read_excel(ROOT / "output/NE_combined_v3.xlsx", "Data")
    meta = pd.read_csv(ROOT / "data/survey_metadata.csv")
    refs = d.groupby("SourceID").agg(reference=("Reference", "first"), records=("SourceID", "size")).reset_index()
    t = meta.merge(refs, left_on="source_id", right_on="SourceID", how="left").drop(columns=["SourceID"])
    t = t[["source_id", "reference", "state", "districts", "communities", "design", "attribution", "fieldwork_group",
           "is_primary", "non_st", "records", "citation_note"]]
    t.to_csv(M / "Table_S1_sources.csv", index=False)
    return t


def docx():
    from docx import Document
    from docx.shared import Pt, Inches
    md = (M / "manuscript.md").read_text()
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)

    def add_runs(par, text):
        # **bold**, *italic*, <sup>x</sup>
        for tok in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|<sup>[^<]+</sup>)", text):
            if not tok: continue
            if tok.startswith("**"): r = par.add_run(tok[2:-2]); r.bold = True
            elif tok.startswith("<sup>"): r = par.add_run(tok[5:-6]); r.font.superscript = True
            elif tok.startswith("*") and len(tok) > 2: r = par.add_run(tok[1:-1]); r.italic = True
            else: par.add_run(tok)
    lines = md.splitlines(); i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-\s|]+\|$", lines[i]): rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            tb = doc.add_table(rows=len(rows), cols=len(rows[0])); tb.style = "Table Grid"
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    add_runs(tb.cell(r, c).paragraphs[0], cell)
            continue
        if l.startswith("# "): doc.add_heading(l[2:], level=0)
        elif l.startswith("## "): doc.add_heading(l[3:], level=1)
        elif l.startswith("### "): doc.add_heading(l[4:], level=2)
        elif l.strip() == "---": pass
        elif l.strip(): add_runs(doc.add_paragraph(), l.replace("\\*", "*"))
        i += 1
    doc.add_page_break(); doc.add_heading("Figures", level=1)
    for f in sorted((ROOT / "output/figures/pub").glob("Fig*.png")):
        doc.add_paragraph(f.stem.replace("_", " ")); doc.add_picture(str(f), width=Inches(6.3))
    doc.save(M / "manuscript.docx")


if __name__ == "__main__":
    t = table_s1(); print("Table S1:", len(t), "sources")
    docx(); print("wrote", M / "manuscript.docx")
