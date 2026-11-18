"""Resolve every species name in the combined dataset against the GBIF Backbone Taxonomy.

Synonyms are mapped to the accepted name, so e.g. Emblica officinalis and Phyllanthus emblica count as one species.
Results are cached in data/taxonomy_gbif.csv (re-running only queries new names).

Usage: .venv/bin/python analysis/14_taxonomy_gbif.py [output/NE_combined_v3.xlsx]
"""
import json, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import importlib.util
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/taxonomy_gbif.csv"
spec = importlib.util.spec_from_file_location("clean", ROOT / "analysis/01_clean.py")
clean = importlib.util.module_from_spec(spec); spec.loader.exec_module(clean)
UA = {"User-Agent": "ne-ethnomed-synthesis/0.1"}


def norm_name(s):
    s = str(s).upper().strip()
    s = " ".join(s.split())
    return clean.NAME_FIX.get(s, s).capitalize()


def match(name):
    q = urllib.parse.urlencode({"name": name, "kingdom": "Plantae", "verbose": "false"})
    for attempt in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.gbif.org/v1/species/match?{q}", headers=UA), timeout=30))
            break
        except Exception:
            time.sleep(2 * (attempt + 1)); r = {}
    acc_key = r.get("acceptedUsageKey") or r.get("usageKey")
    return dict(name_in_data=name, match_type=r.get("matchType"), confidence=r.get("confidence"), status=r.get("status"),
                gbif_usage_key=r.get("usageKey"), accepted_key=acc_key, rank=r.get("rank"),
                accepted_species=r.get("species") if r.get("rank") in ("SPECIES", "VARIETY", "SUBSPECIES", "FORM") else None,
                accepted_genus=r.get("genus"), accepted_family=r.get("family"), gbif_scientific_name=r.get("scientificName"))


def main(src):
    d = pd.read_excel(src, "Data")
    names = sorted({norm_name(x) for x in d["Botanical Name"].dropna()})
    cache = pd.read_csv(CACHE) if CACHE.exists() else pd.DataFrame(columns=["name_in_data"])
    todo = [n for n in names if n not in set(cache.name_in_data)]
    print(f"{len(names)} names, {len(todo)} to query")
    with ThreadPoolExecutor(6) as ex:
        new = list(ex.map(match, todo))
    tax = pd.concat([cache, pd.DataFrame(new)], ignore_index=True).drop_duplicates("name_in_data", keep="last")
    # a usable accepted species needs a species-level match with reasonable confidence
    tax["usable"] = tax.accepted_species.notna() & tax.match_type.isin(["EXACT", "FUZZY"]) & (tax.confidence.fillna(0) >= 80)
    CACHE.parent.mkdir(exist_ok=True)
    tax.sort_values("name_in_data").to_csv(CACHE, index=False)
    t = tax[tax.name_in_data.isin(names)]
    print(t.match_type.value_counts(dropna=False).to_dict())
    print("usable species-level matches:", int(t.usable.sum()), "/", len(t))
    print("distinct accepted species:", t.loc[t.usable, "accepted_species"].nunique(), "(names in data:", len(t), ")")
    syn = t[t.usable & (t.name_in_data != t.accepted_species)]
    print("names changed to an accepted name:", len(syn)); print(syn[["name_in_data", "accepted_species"]].head(12).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "output/NE_combined_v3.xlsx")
