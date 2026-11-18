"""Merge gap-filling sources into the dataset -> output/NE_combined_v3.xlsx.

Records from sources/gap with no medical use in their text (food, fodder, timber only) go to Quarantine.
Usage: .venv/bin/python analysis/12_merge_v3.py
"""
import importlib.util, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
v2 = pd.read_excel(ROOT / "output/NE_combined_v2.xlsx", sheet_name=None)
gap = pd.read_excel(ROOT / "output/gap_sources_extracted.xlsx", sheet_name=None)
spec = importlib.util.spec_from_file_location("ex", ROOT / "analysis/08_extract_new.py")
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
g = gap["Records"].copy()
# single-ailment study: every plant in the table is a jaundice remedy (the parsed column is dosage)
g.loc[g.SourceID == "G13", "Disease"] = "Jaundice; " + g.loc[g.SourceID == "G13", "Disease"].fillna("")
g["ActedUpon"] = g["Disease"].map(ex.systems)
g["Dataset"], g["Row"], g["Tribe_original"], g["status"] = "GAP", range(2, len(g) + 2), g["Tribe"], "extracted_from_paper"
g["qc_flag"] = "auto-extracted (generic table parser) - review use text; ActedUpon auto-assigned"
g.loc[g.Tribe.str.contains("non-ST"), "qc_flag"] += "; non-ST community"
g.loc[g.SourceID == "G04", "qc_flag"] += "; single-theme study (maternity care)"
g.loc[g.SourceID == "G13", "qc_flag"] += "; single-ailment study (jaundice)"
g.loc[g.SourceID == "G16", "qc_flag"] += "; trees only (sacred groves)"
med = re.compile(r"medic|cure|treat|pain|disease|wound|fever|cough|ache|remed|heal|infect|stomach|dysent|diarr|"
                 r"jaundice|bite|boil|ulcer|pressure|diabet|tonic|antidot|poison|swell|burn|cut|skin|bleed", re.I)
# only two papers mix food and medicine; elsewhere every listed plant is medicinal
nonmed = g.SourceID.isin(["G10", "G14", "G19"]) & (g.ActedUpon == "GENERAL/UNSPECIFIED") & ~g.Disease.fillna("").str.contains(med)
# uses that are only non-medicinal (fish poison, fruit ripening, tool making)
nonmed |= g.ActedUpon.map(lambda a: "NON-MEDICINAL" in a and set(a.split(",")) <= {"NON-MEDICINAL", "GENERAL/UNSPECIFIED"})
g["qc_reason"] = ""
g.loc[nonmed, "qc_reason"] = "no medicinal use in extracted text (food/other use)"
# Moran records were mis-cited as the Rabha paper (S16); all 18 occur in Kalita & Phukan 2009 -> restore as G25
MORAN_REF = ("Kalita, D., & Phukan, B. (2009). Folk medicines used by the Moran of Brahmaputra valley, Tinsukia district, "
             "Assam, India. Natural Product Radiance, 8(1), 73-76.")
vq = v2["Quarantine"]
mor = vq.qc_reason.str.contains("Moran", na=False)
restored = vq[mor].copy()
restored["SourceID"], restored["Reference"], restored["qc_reason"] = "G25", MORAN_REF, ""
restored["qc_flag"] = "source corrected: was cited as S16 (Rabha paper); verified in Kalita & Phukan 2009"
restored["status"] = "verified_in_corrected_source"
v2["Quarantine"] = vq[~mor]
v2["Data"] = pd.concat([v2["Data"], restored[[c for c in v2["Data"].columns if c in restored.columns]]], ignore_index=True)
cols = list(v2["Data"].columns)
data = pd.concat([v2["Data"], g.loc[~nonmed, [c for c in cols if c in g.columns]]], ignore_index=True)
quar = pd.concat([v2["Quarantine"], g.loc[nonmed, [c for c in v2["Quarantine"].columns if c in g.columns]]], ignore_index=True)
log = pd.concat([v2["Changelog"], pd.DataFrame(
    [("restore", "18 Moran records -> G25 Kalita & Phukan 2009 (were mis-cited as S16)", int(mor.sum()))] +
    [("add source", f"{r.SourceID}: {r.reference[:90]}", int(((g.SourceID == r.SourceID) & ~nonmed).sum()))
     for r in gap["Sources"].itertuples()] + [("quarantine", "gap records with no medicinal use", int(nonmed.sum()))],
    columns=["action", "detail", "records"])], ignore_index=True)
not_added = pd.DataFrame([
    ("Reang (Tripura)", "Shil & Dutta Choudhury 2009, Ethnobotanical Leaflets", "https://opensiuc.lib.siu.edu/ebl/vol2009/iss6/11", "open access - site blocks scripts, download in browser"),
    ("Moran (Assam)", "Borah, reproductive health (Neliti)", "https://media.neliti.com/media/publications/263243-various-ethno-medicinal-plants-used-for-0a069108.pdf", "open access - download in browser"),
    ("Tea tribes (Assam)", "Journal of Threatened Taxa 6772", "https://threatenedtaxa.org/index.php/JoTT/article/view/6772", "open access - download in browser"),
    ("Tea tribes (Assam)", "Journal of Natural Remedies 23879", "https://informaticsjournals.co.in/index.php/jnr/article/download/23879/19231/38941", "open access - download in browser"),
    ("Chakhesang (Nagaland)", "Bharali et al. 2017, BEPLS (ICAR KRISHI)", "https://krishi.icar.gov.in/jspui/handle/123456789/41747", "open access - host unreachable from here"),
    ("Garo (Meghalaya)", "Marak & Lalnundanga 2019, Science Vision", "https://www.sciencevision.org/storage/journal-articles/January2019/Tu2KIEIaE1yTFs9qtWN3.pdf", "open access - site certificate error"),
    ("Mao Naga (Manipur)", "Lokho et al. 2023, Exploratory Animal and Medical Research", "https://doaj.org/article/3c05e13ebcd64199acd1db7efac64a0b", "open access - get PDF from journal"),
    ("Thadou, Hmar, Gangte, Simte, Vaiphei, Zo (Manipur)", "Kuki-Chin, Kaihlam WLS, Acta Ecologica Sinica 2023", "https://www.aminer.org/pub/64a79570d68f896efa07c359", "paywalled"),
    ("Halam (Tripura)", "Debnath & Das 2019, Indian J Ecology", "https://indianjournals.com/article/ije1-46-2-036", "paywalled (Halam partly covered by G13)"),
    ("Ao (Nagaland)", "Pegu et al. 2024 Supplementary Table 1", "https://horizonepublishing.com/journals/index.php/PST/article/view/2602", "supplement needed"),
    ("Several Naga tribes", "Rao & Jamir 1982, Economic Botany", "https://repository.ias.ac.in/52225", "paywalled"),
], columns=["fills_gap", "paper", "link", "status"])
data["State"] = data["State"].replace({"AP": "Arunachal Pradesh"})
out = ROOT / "output/NE_combined_v3.xlsx"
with pd.ExcelWriter(out) as xw:
    data.to_excel(xw, sheet_name="Data", index=False)
    quar.to_excel(xw, sheet_name="Quarantine", index=False)
    log.to_excel(xw, sheet_name="Changelog", index=False)
    pd.concat([v2["New_sources"], gap["Sources"]]).to_excel(xw, sheet_name="Added_sources", index=False)
    not_added.to_excel(xw, sheet_name="Not_yet_added", index=False)
print(f"v2+restored {len(v2['Data'])} + gap {int((~nonmed).sum())} = {len(data)} records; quarantined {int(nonmed.sum())}; wrote {out}")
