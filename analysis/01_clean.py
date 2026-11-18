"""Step 1 of the NE India ethnomedicine meta-analysis: clean NE5.xlsx.

Mirrors the West Bengal meta-analysis (Vineeta et al. 2022, Phytomedicine Plus 2:100158):
species list -> families/genera -> plant parts -> ailment categories (Cook 1995) -> communities.

Usage:  .venv/bin/python analysis/01_clean.py NE-Ethnomedicine/NE5.xlsx output/NE_clean.xlsx
The input file is never modified.
"""
import re
import sys
from pathlib import Path

import pandas as pd

# --- 1. Species spelling fixes (typos/truncations found by fuzzy matching). -----------------
# Synonyms are NOT resolved here; that needs a WFO/POWO backbone (step 2).
NAME_FIX = {
    "ADHATOLA VASICA": "ADHATODA VASICA",
    "AGERATUM CONIZOIDES": "AGERATUM CONYZOIDES",
    "ALPINIA ALUGHAS": "ALPINIA ALLUGHAS",
    "ASPARAGUS RACEMOSA": "ASPARAGUS RACEMOSUS",
    "AZADIRACTA INDICA": "AZADIRACHTA INDICA",
    "CALICARPA ARBOREA": "CALLICARPA ARBOREA",
    "CAMELLIA SINEN": "CAMELLIA SINENSIS",
    "CARTHARANTHUS ROSEUS": "CATHARANTHUS ROSEUS",
    "CITRUS AURANTIFOLIA": "CITRUS AURANTIIFOLIA",
    "CLERODENDRON COLEBROOKIANUM": "CLERODENDRUM COLEBROOKIANUM",
    "CLERODENDRUM CLEOBROOKIANUM": "CLERODENDRUM COLEBROOKIANUM",
    "CRASSOCEPHALUM CREPIDIODES": "CRASSOCEPHALUM CREPIDIOIDES",
    "CURUMA ANGUSTIFOLIA": "CURCUMA ANGUSTIFOLIA",
    "DENDROCNIDE SINUTA": "DENDROCNIDE SINUATA",
    "DRYMERIA CORDATA": "DRYMARIA CORDATA",
    "DYMARIA CORDATA": "DRYMARIA CORDATA",
    "ELSHOLZIA BLANDA": "ELSHOLTZIA BLANDA",
    "FICUS BENGALENSIS": "FICUS BENGHALENSIS",
    "GYNURA BISCOLOR": "GYNURA BICOLOR",
    "HAUTTUYNIA CORDATA": "HOUTTUYNIA CORDATA",
    "HYDROCOTYL ROTUNDIFOLIA": "HYDROCOTYLE ROTUNDIFOLIA",
    "HYDROCOTYLE SIBTHORPHIOIDES": "HYDROCOTYLE SIBTHORPIOIDES",
    "LAGINARIA SICERARIA": "LAGENARIA SICERARIA",
    "MEASA INDICA": "MAESA INDICA",
    "MIKANIA MICRAN": "MIKANIA MICRANTHA",
    "MUSA ACUMINATE": "MUSA ACUMINATA",
    "MUSA BULBISIANA": "MUSA BALBISIANA",
    "MUSA PARADISSICA": "MUSA PARADISIACA",
    "PAEDARIA FOETIDA": "PAEDERIA FOETIDA",
    "PHLOGOCANTHUS THYRSIFORMIS": "PHLOGACANTHUS THYRSIFLORUS",
    "SPILANTHUS PANICULATA": "SPILANTHES PANICULATA",
    "SWERTIA CHIRATA": "SWERTIA CHIRAYITA",
    "ZINGIBER OFFICI": "ZINGIBER OFFICINALE",
    "CAESALPINIA BONDUCELLA": "CAESALPINIA BONDUC",
}

# --- 2. Families: spelling fixes + old (Cronquist) families -> APG IV. --------------------
FAMILY_FIX = {
    "CONVOVULACEAE": "CONVOLVULACEAE",
    "DISCOREACEAE": "DIOSCOREACEAE",
    "ELAEGNACEAE": "ELAEAGNACEAE",
    "MIMOSACEAE": "FABACEAE",
    "PAPILIONACEAE": "FABACEAE",
    "ASCLEPIADACEAE": "APOCYNACEAE",
    "BOMBACACEAE": "MALVACEAE",
    "STERCULIACEAE": "MALVACEAE",
    "CANNABINACEAE": "CANNABACEAE",
    "CHENOPODIACEAE": "AMARANTHACEAE",
    "AVERRHOACEAE": "OXALIDACEAE",
    "PUNICACEAE": "LYTHRACEAE",
    "MYRSINACEAE": "PRIMULACEAE",
    "VALERIANACEAE": "CAPRIFOLIACEAE",
    "STIXIDACEAE": "RESEDACEAE",
    "COMPOSITAE": "ASTERACEAE", "LEGUMINOSAE": "FABACEAE", "LABIATAE": "LAMIACEAE", "UMBELLIFERAE": "APIACEAE",
    "GRAMINEAE": "POACEAE", "CRUCIFERAE": "BRASSICACEAE", "GUTTIFERAE": "CLUSIACEAE", "PALMAE": "ARECACEAE",
    "CAESALPINIACEAE": "FABACEAE", "CAESALPINICEAE": "FABACEAE", "ACERACEAE": "SAPINDACEAE",
    "GESNERACEAE": "GESNERIACEAE", "LILIACCEAE": "LILIACEAE", "ZINGIBERCEAE": "ZINGIBERACEAE",
    "MELASTOMACEAE": "MELASTOMATACEAE", "APOCYANACEAE": "APOCYNACEAE", "MURACEAE": "MUSACEAE",
    "BIGONIACEAE": "BIGNONIACEAE", "TILIACEAE": "MALVACEAE", "CUSCUTACEAE": "CONVOLVULACEAE", "LEMIACEAE": "LAMIACEAE", "MENISPERMIACEAE": "MENISPERMACEAE", "THYMELACEAE": "THYMELAEACEAE", "PORTULACCACEAE": "PORTULACACEAE", "VISCACEAE": "SANTALACEAE",
    "FLACOURTIACEAE": "SALICACEAE", "XANTHORRHOEACEAE": "ASPHODELACEAE",
}

# Genus -> APG IV family, for genera whose family changed or was mis-entered in sources.
GENUS_FAMILY = {
    "ALLIUM": "AMARYLLIDACEAE", "ALOE": "ASPHODELACEAE", "ASPARAGUS": "ASPARAGACEAE", "ACORUS": "ACORACEAE",
    "COSTUS": "COSTACEAE", "HELLENIA": "COSTACEAE", "CLERODENDRUM": "LAMIACEAE", "CALLICARPA": "LAMIACEAE",
    "DRYMARIA": "CARYOPHYLLACEAE", "MAESA": "PRIMULACEAE", "PHYLLANTHUS": "PHYLLANTHACEAE",
    "ANTIDESMA": "PHYLLANTHACEAE", "APOROSA": "PHYLLANTHACEAE", "BACCAUREA": "PHYLLANTHACEAE",
    "FLUEGGEA": "PHYLLANTHACEAE", "BREYNIA": "PHYLLANTHACEAE", "BRIDELIA": "PHYLLANTHACEAE", "EMBLICA": "PHYLLANTHACEAE",
    "SCOPARIA": "PLANTAGINACEAE", "PICRORHIZA": "PLANTAGINACEAE", "BACOPA": "PLANTAGINACEAE",
    "LEPIONURUS": "OPILIACEAE", "VISCUM": "SANTALACEAE", "SENNA": "FABACEAE", "CASSIA": "FABACEAE",
    "LANTANA": "VERBENACEAE", "CURANGA": "PLANTAGINACEAE", "CYCLOSORUS": "THELYPTERIDACEAE", "EURYA": "PENTAPHYLACACEAE",
    "GYNOCARDIA": "ACHARIACEAE", "STIXIS": "RESEDACEAE",
    "AVERRHOA": "OXALIDACEAE", "BEGONIA": "BEGONIACEAE", "CHEILOCOSTUS": "COSTACEAE", "CORCHORUS": "MALVACEAE",
    "CUSCUTA": "CONVOLVULACEAE", "HYPTIS": "LAMIACEAE", "MELIA": "MELIACEAE", "ZINGIBER": "ZINGIBERACEAE", "CENTELLA": "APIACEAE", "HODGSONIA": "CUCURBITACEAE", "VITEX": "LAMIACEAE", "GMELINA": "LAMIACEAE", "TECTONA": "LAMIACEAE",
}

# --- 3. Plant parts -> standard categories (applied per comma-separated token). ------------
PART_RULES = [  # first regex that matches wins
    (r"ROOTBARK|STEMBARK|BARK", "Bark"),
    (r"WHOLEPLANT|ENTIREPART|^PLANT$", "Whole plant"),
    (r"AERIAL|APICAL", "Aerial part"),
    (r"LATEX|SAP|GUM|OIL|EXUDATE|WHITEFLUID|MILKY", "Latex/exudate"),
    (r"RHIZOME", "Rhizome"),
    (r"TUBER|BULB|BEET", "Tuber/bulb"),
    (r"ROOT", "Root"),
    (r"LEAF|PETIOLE|SHEATH", "Leaf"),
    (r"SEED|GRAIN|NUT", "Seed"),
    (r"FRUIT|FURIT|PERICARP|PULP|RIND|PEEL|POD|RASPBERRY", "Fruit"),
    (r"FLOWER|INFL|ESCENCE|BUD|SPIKE|BRACT|CARPEL", "Flower/inflorescence"),
    (r"SHOOT|TWIG|CULM", "Shoot/twig"),
    (r"STEM|WOOD", "Stem"),
    (r"PITCHER", "Other"),
]
PART_DROP = {"", "C", "N", "NOTSPECIFIED", "JUN.TOOCT.", "APPLIEDTOPICALLY", "BOILEDEXTRACT", "SOIL", "PASTE", "CURRY"}

# --- 4. Body systems (ActedUpon) -> Cook (1995)-style categories. --------------------------
SYSTEM_FIX = {
    "MUSCULOSSKELETAL": "MUSCULOSKELETAL", "INTEGUMENT": "INTEGUMENTARY", "MUSCULAR": "MUSCULOSKELETAL",
    "SKELETAL": "MUSCULOSKELETAL", "SSKELETAL": "MUSCULOSKELETAL",
    "ENSORY": "SENSORY", "OCULAR": "SENSORY", "OPHTHALMIC": "SENSORY", "OTIC": "SENSORY",
    "RENAL": "URINARY", "PULMONARY": "RESPIRATORY",
    "CARDIOVASCULAR": "CIRCULATORY", "BLOOD": "CIRCULATORY", "HEMATOLOGIC": "CIRCULATORY",
    "HEPATIC": "DIGESTIVE", "INTESTINAL": "DIGESTIVE", "DENTAL": "DIGESTIVE",
    "NEUROLOGICAL": "NERVOUS", "LYMPHATIC": "IMMUNE", "ONCOLOGICAL": "NEOPLASMS",
    "GENERAL": "GENERAL/UNSPECIFIED", "GENERALHEALTH": "GENERAL/UNSPECIFIED",
    "VARIOUS": "GENERAL/UNSPECIFIED", "PREVENTIVE": "GENERAL/UNSPECIFIED",
    "EMERGENCY": "GENERAL/UNSPECIFIED", "NUTRITIONAL": "NUTRITIONAL",
    "VARIOUS/DEPENDSONPECIFICTYPE": "GENERAL/UNSPECIFIED",
    # non-medicinal uses: kept but flagged
    "CULINARY": "NON-MEDICINAL", "AGRICULTURAL": "NON-MEDICINAL", "ARTISANAL": "NON-MEDICINAL",
}

STATE_FIX = {"AP": "Arunachal Pradesh"}


def map_parts(raw):
    out = []
    for tok in str(raw).upper().replace(" ", "").split(","):
        if tok in PART_DROP or tok in ("NAN", "<NA>"):
            continue
        cat = next((c for pat, c in PART_RULES if re.search(pat, tok)), None)
        out.append(cat or f"UNMAPPED:{tok}")
    return sorted(set(out)) or ["Not specified"]


def map_systems(raw):
    toks = [t.strip().replace(" ", "") for t in str(raw).upper().split(",") if t.strip()]
    toks = [re.sub(r"SYSTEMS?(\(.*\))?$", "", t) or t for t in toks]
    return sorted({SYSTEM_FIX.get(t, t) for t in toks}) or ["GENERAL/UNSPECIFIED"]


def main(src, dst):
    raw = pd.read_excel(src)
    d = raw.copy()
    d.insert(0, "RecordID", range(1, len(d) + 1))
    for c in d.select_dtypes(include=["object", "string"]):
        d[c] = d[c].astype("string").str.replace("\xa0", " ").str.strip()

    d["Species"] = d["Botanical Name"].str.upper().str.replace(r"\s+", " ", regex=True)
    d["Species"] = d["Species"].replace(NAME_FIX).str.capitalize()
    d["Genus"] = d["Species"].str.split().str[0]
    fam = d["Family Name"].str.upper().str.strip().replace(FAMILY_FIX)
    d["Family"] = d["Genus"].str.upper().map(GENUS_FAMILY).fillna(fam).str.capitalize()
    d["Family"] = d["Family"].fillna(d.groupby("Genus")["Family"].transform(lambda s: s.mode().iat[0] if s.notna().any() else pd.NA))
    d["State"] = d["State"].replace(STATE_FIX)
    d["PartCats"] = d["Partsused"].map(map_parts)
    d["SystemCats"] = d["ActedUpon"].map(map_systems)
    d["Year"] = d["Reference"].str.extract(r"\((\d{4})\)")[0].astype("Int64")
    d["Medicinal"] = ~d["SystemCats"].map(lambda s: s == ["NON-MEDICINAL"])

    # Species with conflicting family assignments after cleaning -> needs manual check
    fam_conf = d.groupby("Species")["Family"].nunique()
    fam_conf = d[d["Species"].isin(fam_conf[fam_conf > 1].index)][["Species", "Family"]].drop_duplicates()

    # ---- species-level table (unit of analysis in the paper) ----
    sp = d.groupby("Species").agg(
        Family=("Family", lambda s: s.mode().iat[0] if s.notna().any() else pd.NA),
        Genus=("Genus", "first"),
        n_records=("RecordID", "size"),
        n_sources=("Reference", "nunique"),
        n_tribes=("Tribe", "nunique"),
        n_states=("State", "nunique"),
        States=("State", lambda s: "; ".join(sorted(s.unique()))),
        Tribes=("Tribe", lambda s: "; ".join(sorted(s.unique()))),
        Parts=("PartCats", lambda s: "; ".join(sorted({p for l in s for p in l}))),
        Systems=("SystemCats", lambda s: "; ".join(sorted({p for l in s for p in l}))),
        LocalNames=("Common Name", lambda s: "; ".join(sorted(s.dropna().unique()))),
    ).reset_index()
    sp["LifeForm"] = pd.NA      # to fill: Herb/Shrub/Tree/Climber/Fern/Grass/Orchid (step 2)
    sp["IUCN"] = pd.NA          # to fill from IUCN Red List (step 2)
    sp["AcceptedName_WFO"] = pd.NA
    sp = sp.sort_values(["n_sources", "n_tribes"], ascending=False)

    # ---- paper-style summary tables (counted by species, not records) ----
    explode = lambda col: d[["Species", col]].explode(col).drop_duplicates()
    fam = sp.groupby("Family").agg(species=("Species", "size"), genera=("Genus", "nunique"))
    fam = fam.sort_values("species", ascending=False)
    parts = explode("PartCats").groupby("PartCats")["Species"].nunique().sort_values(ascending=False)
    parts = parts.to_frame("species").assign(pct=lambda x: (100 * x.species / sp.shape[0]).round(1))
    systems = explode("SystemCats").groupby("SystemCats")["Species"].nunique().sort_values(ascending=False)
    tribe = d.groupby(["State", "Tribe"]).agg(records=("RecordID", "size"), species=("Species", "nunique"),
                                              families=("Family", "nunique"), sources=("Reference", "nunique"))
    state = d.groupby("State").agg(records=("RecordID", "size"), species=("Species", "nunique"),
                                   families=("Family", "nunique"), tribes=("Tribe", "nunique"),
                                   sources=("Reference", "nunique"))
    sources = d.groupby("Reference").agg(Year=("Year", "first"), State=("State", lambda s: "; ".join(s.unique())),
                                         Tribe=("Tribe", lambda s: "; ".join(s.unique())),
                                         records=("RecordID", "size")).sort_values("Year")
    overview = pd.Series({
        "records": len(d), "sources": d["Reference"].nunique(), "species": sp.shape[0],
        "genera": sp["Genus"].nunique(), "families": sp["Family"].nunique(),
        "tribes": d["Tribe"].nunique(), "states": d["State"].nunique(),
        "spelling fixes applied": int((d["Botanical Name"].str.upper().str.strip() .isin(NAME_FIX.keys())).sum()),
        "species with >1 family": fam_conf["Species"].nunique(),
    }, name="value")

    unmapped = explode("PartCats")
    unmapped = unmapped[unmapped["PartCats"].astype(str).str.startswith("UNMAPPED")]

    rec = d.copy()
    for c in ("PartCats", "SystemCats"):
        rec[c] = rec[c].map("; ".join)

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(dst) as xw:
        overview.to_frame().to_excel(xw, sheet_name="Overview")
        rec.to_excel(xw, sheet_name="Records_clean", index=False)
        sp.to_excel(xw, sheet_name="Species", index=False)
        fam.to_excel(xw, sheet_name="Families")
        parts.to_excel(xw, sheet_name="Parts")
        systems.to_frame("species").to_excel(xw, sheet_name="Systems")
        tribe.to_excel(xw, sheet_name="Tribes")
        state.to_excel(xw, sheet_name="States")
        sources.to_excel(xw, sheet_name="Sources")
        fam_conf.to_excel(xw, sheet_name="QC_family_conflicts", index=False)
        unmapped.to_excel(xw, sheet_name="QC_unmapped_parts", index=False)

    print(overview.to_string())
    print("\nTop families:\n", fam.head(8).to_string())
    print("\nParts:\n", parts.to_string())
    print("\nSystems:\n", systems.to_string())
    print("\nStates:\n", state.to_string())
    print(f"\nWrote {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
