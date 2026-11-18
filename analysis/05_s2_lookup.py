"""Semantic Scholar title lookup for sources still missing a PDF. Prints candidate OA links."""
import json, sys, time, urllib.parse, urllib.request, re
import pandas as pd
m = pd.read_csv(sys.argv[1]); have = set(sys.argv[2].split(","))
for r in m.itertuples():
    if r.SourceID in have: continue
    q = urllib.parse.quote(r.query_title[:150])
    url = f"https://api.semanticscholar.org/graph/v1/paper/search/match?query={q}&fields=title,year,venue,externalIds,openAccessPdf,url"
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ne-ethno-meta/0.1"}), timeout=30))["data"][0]; break
        except urllib.error.HTTPError as e:
            if e.code == 404: d = {}; break
            time.sleep(5 * (attempt + 1)); d = {}
        except Exception: d = {}; break
    print(f"{r.SourceID} | {r.query_title[:60]}\n   -> {d.get('title','-')[:70]} ({d.get('year')}, {d.get('venue','')[:30]}) oa={ (d.get('openAccessPdf') or {}).get('url') } ids={d.get('externalIds')}")
    time.sleep(1.5)
