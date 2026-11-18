"""Merge references from NE5 + Assam V6, look each up in OpenAlex for DOI / open-access PDF links.
Writes output/source_master.csv. No download here.

Usage: .venv/bin/python analysis/04_find_pdfs.py NE-Ethnomedicine/NE5.xlsx Assam_Ethnomedicine/V6.xlsx output/source_master.csv
"""
import json, re, sys, time, urllib.parse, urllib.request
import pandas as pd

UA = {"User-Agent": "ne-ethno-meta/0.1"}


def norm(s):
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


def title_of(ref):
    # text after "(year)." up to next period; fall back to whole ref
    m = re.search(r"\(\d{4}\)\.?\s*(.+?)(?:\.\s|$)", ref)
    t = m.group(1) if m else ref
    t = re.sub(r"^\d+\.\s*", "", t)            # "12. THE INDIGENOUS ..."
    t = t.split(" By ")[0]
    return t[:200]


def openalex(title):
    q = urllib.parse.quote(title)
    url = f"https://api.openalex.org/works?search={q}&per-page=3"
    try:
        res = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))["results"]
    except Exception as e:
        return [], str(e)
    return res, ""


def sim(a, b):
    wa, wb = set(re.findall(r"[a-z]{3,}", a.lower())), set(re.findall(r"[a-z]{3,}", b.lower()))
    return len(wa & wb) / max(1, len(wa | wb))


def main(ne5, v6, dst):
    a = pd.read_excel(ne5); b = pd.read_excel(v6)
    a["Reference"] = a["Reference"].map(norm); b["Reference"] = b["Reference"].map(norm)
    ra = a.groupby("Reference").size().rename("records_NE5")
    rb = b.groupby("Reference").size().rename("records_V6")
    refs = pd.concat([ra, rb], axis=1).fillna(0).astype(int).reset_index(names="reference")
    rows = []
    for r in refs.itertuples():
        t = title_of(r.reference)
        res, err = openalex(t)
        best = max(res, key=lambda w: sim(t, w.get("title") or ""), default={})
        s = sim(t, best.get("title") or "")
        oa = best.get("open_access") or {}
        locs = [l.get("pdf_url") for l in (best.get("locations") or []) if l.get("pdf_url")]
        rows.append(dict(reference=r.reference, records_NE5=r.records_NE5, records_V6=r.records_V6,
                         query_title=t, oa_title=best.get("title"), match=round(s, 2),
                         year=best.get("publication_year"), doi=(best.get("doi") or "").replace("https://doi.org/", ""),
                         is_oa=oa.get("is_oa"), oa_url=oa.get("oa_url"), pdf_urls=" | ".join(dict.fromkeys(locs)),
                         openalex_id=best.get("id"), err=err))
        time.sleep(0.3)
    out = pd.DataFrame(rows)
    out.loc[out.match < 0.5, ["doi", "oa_url", "pdf_urls"]] = ""   # weak match -> don't trust
    out = out.sort_values(["records_NE5", "records_V6"], ascending=False)
    out.insert(0, "SourceID", [f"S{i:02d}" for i in range(1, len(out) + 1)])
    out.to_csv(dst, index=False)
    for x in out.itertuples():
        print(f"{x.SourceID} m={x.match:.2f} oa={x.is_oa} doi={x.doi or '-'}\n    {x.query_title[:90]}\n    pdf: {x.pdf_urls[:150] or x.oa_url or '-'}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
