"""Look up each source reference in Crossref; write output/sources_crossref.csv."""
import json, sys, time, urllib.parse, urllib.request
import pandas as pd
d = pd.read_excel(sys.argv[1], "Records_clean")
refs = d.groupby("Reference").size().sort_values(ascending=False)
rows = []
for ref, n in refs.items():
    q = urllib.parse.quote(ref[:300])
    url = f"https://api.crossref.org/works?query.bibliographic={q}&rows=2&select=DOI,title,container-title,issued,author,score"
    req = urllib.request.Request(url, headers={"User-Agent": "ne-ethno-meta/0.1"})
    try:
        items = json.load(urllib.request.urlopen(req, timeout=30))["message"]["items"]
    except Exception as e:
        items = []; print("ERR", e, file=sys.stderr)
    top = items[0] if items else {}
    rows.append(dict(records=n, reference=ref,
        cr_title=(top.get("title") or [""])[0], cr_journal=(top.get("container-title") or [""])[0],
        cr_year=(top.get("issued", {}).get("date-parts") or [[None]])[0][0],
        cr_first_author=(top.get("author") or [{}])[0].get("family", ""),
        doi=top.get("DOI", ""), score=round(top.get("score", 0), 1)))
    time.sleep(1)
out = pd.DataFrame(rows)
out.to_csv(sys.argv[2], index=False)
for r in out.itertuples():
    print(f"{r.score:6} | {r.reference[:70]}\n       -> {r.cr_first_author} {r.cr_year} {r.cr_title[:80]} [{r.cr_journal[:40]}] {r.doi}")
