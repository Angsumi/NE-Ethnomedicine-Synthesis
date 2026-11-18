"""Tribe and geographic coverage of the combined dataset against a reference list of NE India communities.

Usage: .venv/bin/python analysis/10_coverage.py
Reads  output/NE_combined_v3.xlsx, analysis/ne_tribes_reference.csv
Writes output/coverage.xlsx (Tribes, By_state, Districts)
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STATE_FIX = {"AP": "Arunachal Pradesh"}
DISTRICTS_TOTAL = {"Arunachal Pradesh": 28, "Assam": 35, "Manipur": 16, "Meghalaya": 12, "Mizoram": 11,
                   "Nagaland": 17, "Tripura": 8}
# study districts, read from each paper (sources/text) and checked by hand
SOURCE_DISTRICTS = {
    "S01": ["Lower Subansiri"], "S02": ["Champhai"], "S03": ["Mon"], "S04": ["Kohima"], "S05": ["Biswanath"],
    "S06": ["Dibrugarh"], "S07": ["Lakhimpur"], "S08": ["Tinsukia", "Dibrugarh"], "S09": ["East Khasi Hills", "Ri Bhoi"],
    "S10": ["Imphal West", "Imphal East"], "S11": ["Morigaon"], "S12": ["Lohit", "Namsai"], "S14": ["Golaghat", "Nagaon"],
    "S15": ["West Jaintia Hills", "East Jaintia Hills"], "S16": ["Chirang"], "S17": ["West Tripura", "South Tripura"],
    "S18": ["East Siang"], "S19": ["Lohit"], "S21": ["West Siang"], "S22": ["Kamrup Metropolitan"], "S23": ["Papum Pare"],
    "S24": ["West Kameng"], "S25": ["Sivasagar"], "S26": ["Upper Subansiri"], "S27": ["Baksa"], "S28": ["Kamrup"],
    "S29": ["West Karbi Anglong"], "S30": ["Goalpara"], "S31": ["Dibrugarh"], "S33": ["Hailakandi"],
    "N03": ["West Tripura", "South Tripura"], "N05": ["West Garo Hills"],
    "N06": ["Aizawl", "Lunglei", "Lawngtlai", "Saiha", "Mamit"], "N07": ["Mamit"], "N08": ["Tawang"],
    "N09": ["Ukhrul"], "N10": ["Unakoti", "North Tripura", "Dhalai", "West Tripura"],
    "G02": ["Senapati"], "G03": ["Tamenglong"], "G04": ["Churachandpur"], "G09": ["Tirap"], "G10": ["Tirap"],
    "G13": ["West Tripura", "Khowai", "Gomati"], "G14": ["Charaideo"], "G16": ["Imphal West", "Imphal East"],
    "G17": ["Wokha"], "G19": ["Mokokchung"], "G20": ["Dima Hasao"], "G21": ["Bongaigaon"], "G22": ["South Salmara-Mankachar"], "G23": ["South West Garo Hills"], "G25": ["Tinsukia"], "G26": ["West Jaintia Hills"], "G27": ["Tuensang"], "G29": ["Longding"], "G33": ["Senapati"], "G18": ["Lower Subansiri", "Tawang", "Changlang", "East Siang", "Papum Pare", "Lower Dibang Valley"],
}
SOURCE_STATE = {}


def main():
    d = pd.read_excel(ROOT / "output/NE_combined_v3.xlsx", "Data")
    d["State"] = d["State"].replace(STATE_FIX)
    ref = pd.read_csv(ROOT / "analysis/ne_tribes_reference.csv")
    tribes = d.groupby(["State", "Tribe"]).agg(records=("SourceID", "size"), sources=("SourceID", "nunique"),
                                               species=("Botanical Name", "nunique")).reset_index()
    rows = []
    for r in ref.itertuples():
        hit = tribes[(tribes.State == r.state) & tribes.Tribe.str.lower().str.contains(r.aliases, regex=True)]
        # a community studied in a neighbouring state still counts as "studied elsewhere"
        other = tribes[(tribes.State != r.state) & tribes.Tribe.str.lower().str.contains(r.aliases, regex=True)]
        rows.append(dict(state=r.state, tribe=r.tribe, status=r.status, language_family=r.language_family,
                         size_tier=r.size_tier, zone=r.zone, covered=len(hit) > 0,
                         sources=int(hit.sources.sum()), records=int(hit.records.sum()), species=int(hit.species.sum()),
                         covered_in_other_state=", ".join(sorted(other.State.unique()))))
    cov = pd.DataFrame(rows)

    by_state = cov.groupby("state").agg(
        tribes_listed=("tribe", "size"), tribes_covered=("covered", "sum"),
        major_listed=("size_tier", lambda s: (s == "major").sum()),
        major_covered=("covered", lambda s: (s & (cov.loc[s.index, "size_tier"] == "major")).sum()))
    dist = (pd.Series({s: v for s, v in SOURCE_DISTRICTS.items()}).explode().rename("district").reset_index()
            .rename(columns={"index": "SourceID"}))
    st = d.groupby("SourceID")["State"].first()
    dist["state"] = dist.SourceID.map(st)
    dc = dist.groupby("state").district.nunique()
    by_state["districts_covered"] = dc
    by_state["districts_total"] = pd.Series(DISTRICTS_TOTAL)
    by_state["sources"] = d.groupby("State").SourceID.nunique()
    by_state["records"] = d.groupby("State").size()

    with pd.ExcelWriter(ROOT / "output/coverage.xlsx") as xw:
        cov.to_excel(xw, sheet_name="Tribes", index=False)
        by_state.to_excel(xw, sheet_name="By_state")
        dist.to_excel(xw, sheet_name="Districts", index=False)
    pd.set_option("display.width", 200)
    print(by_state.to_string())
    print("\nUNCOVERED major/medium communities:")
    u = cov[~cov.covered & cov.size_tier.isin(["major", "medium"])]
    print(u[["state", "tribe", "status", "size_tier", "covered_in_other_state"]].to_string(index=False))
    print("\nLanguage families covered:", cov[cov.covered].language_family.str.split(" \\(").str[0].value_counts().to_dict())
    print("Zones covered:", cov[cov.covered].zone.value_counts().to_dict())


if __name__ == "__main__":
    main()
