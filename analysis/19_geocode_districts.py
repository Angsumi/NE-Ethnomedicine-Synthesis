"""Geocode study districts (OpenStreetMap Nominatim, 1 request/s) -> data/district_coords.csv.
Only district and state names are sent. Cached; re-running queries only new districts.
Usage: .venv/bin/python analysis/19_geocode_districts.py
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/district_coords.csv"
ALIAS = {"Kamrup Metropolitan": "Kamrup Metropolitan district", "South Salmara-Mankachar": "South Salmara Mankachar",
         "Saiha": "Siaha", "Lower Dibang Valley": "Lower Dibang Valley district", "several": None}


def geocode(district, state):
    q = urllib.parse.urlencode({"q": f"{ALIAS.get(district, district)}, {state}, India", "format": "json", "limit": 1})
    req = urllib.request.Request(f"https://nominatim.openstreetmap.org/search?{q}", headers={"User-Agent": "ne-ethnomed-synthesis/0.1"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception:
        r = []
    time.sleep(1.1)
    return (float(r[0]["lat"]), float(r[0]["lon"]), r[0].get("display_name", "")[:80]) if r else (None, None, "")


def main():
    m = pd.read_csv(ROOT / "data/survey_metadata.csv")
    pairs = sorted({(d.strip(), r.state) for r in m.itertuples() for d in str(r.districts).split(";") if ALIAS.get(d.strip(), 1) is not None})
    cache = pd.read_csv(CACHE) if CACHE.exists() else pd.DataFrame(columns=["district", "state", "lat", "lon", "match"])
    have = set(zip(cache.district, cache.state))
    new = []
    for d, s in pairs:
        if (d, s) in have: continue
        lat, lon, name = geocode(d, s)
        new.append(dict(district=d, state=s, lat=lat, lon=lon, match=name)); print(d, s, lat, lon, name[:50])
    cache = pd.concat([cache, pd.DataFrame(new)], ignore_index=True)
    cache.to_csv(CACHE, index=False)
    print("missing:", cache[cache.lat.isna()][["district", "state"]].values.tolist())


if __name__ == "__main__":
    main()
