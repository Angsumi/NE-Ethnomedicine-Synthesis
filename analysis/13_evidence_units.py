"""Build the evidence-unit table: one row per (independent fieldwork survey x community x accepted species x condition).

Why: the same plant-use claim can appear many times in the workbook because one survey lists it for several
communities, because two papers reuse one fieldwork campaign, or because a pooled multi-community survey is
split into records. Recurrence must be counted on independent units, not rows.

Each unit keeps:
  - the original use wording (verbatim, from the record) next to the harmonised condition
  - the plant part
  - survey design (general / single_ailment / plant_group / food_and_medicine / selected_ailments / review)
  - attribution (single_community / multi_community_explicit / pooled)
  - an automatic source check: does the condition's wording occur near the species name in the source text?

Usage: .venv/bin/python analysis/13_evidence_units.py
Reads  output/NE_combined_v3.xlsx, data/survey_metadata.csv, data/taxonomy_gbif.csv, sources/*/text
Writes output/evidence_units.csv, output/condition_vocabulary.csv
"""
import importlib.util, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tax", ROOT / "analysis/14_taxonomy_gbif.py")
tx = importlib.util.module_from_spec(spec); spec.loader.exec_module(tx)
spec = importlib.util.spec_from_file_location("clean", ROOT / "analysis/01_clean.py")
clean = importlib.util.module_from_spec(spec); spec.loader.exec_module(clean)

# Specific conditions (finer than body systems). Order matters only for readability; a record can map to several.
CONDITIONS = [
    ("diarrhoea", r"diarr?h?o?ea|loose motion|\bdiarr"), ("dysentery", r"dysent"), ("jaundice", r"jaundice|hepatitis|bilirubin"),
    ("liver disorder", r"liver|hepat(?!itis)"), ("stomach ache", r"stomach ?(ache|pain|disorder|problem|trouble|complaint)|abdominal pain|colic|gastralgia"),
    ("indigestion", r"indigest|dyspeps|digest(ion|ive)|flatul|bloat|carminat|appetite"), ("gastritis/acidity", r"gastri|acidity|peptic|ulcer of stomach|stomach ulcer"),
    ("constipation", r"constipat|laxative|purgative"), ("intestinal worms", r"worm|helminth|anthelmint|vermifug|deworm"),
    ("piles", r"piles|haemorrhoid|hemorrhoid"), ("vomiting/nausea", r"vomit|nausea|emesis"), ("cholera", r"cholera"),
    ("toothache/oral", r"tooth|dental|gum|pyorrh|mouth (ulcer|sore)|stomatitis"),
    ("wounds/cuts", r"wound|\bcuts?\b|injur"), ("burns", r"\bburn"), ("boils/abscess", r"\bboil|abscess|carbuncle|furuncle"),
    ("skin disease", r"skin|eczema|dermat|rash|pimple|acne|leucoderm|wart"), ("scabies/itching", r"scabies|itch"),
    ("fungal infection/ringworm", r"ringworm|fung|tinea"), ("leprosy", r"leprosy"), ("hair/dandruff/lice", r"dandruff|hair|lice"),
    ("fever", r"fever|pyre|febri"), ("malaria", r"malaria"), ("typhoid", r"typhoid"), ("pox/measles", r"pox|measles"),
    ("cough", r"cough"), ("common cold", r"\bcold\b|catarrh|nasal|sinus"), ("asthma", r"asthma"), ("bronchitis", r"bronch"),
    ("sore throat/tonsillitis", r"throat|tonsil|pharyng"), ("tuberculosis", r"tubercul|\btb\b|phthisis"), ("pneumonia", r"pneumon"),
    ("headache", r"headache|head ache|migraine"), ("body ache/pain", r"body ?ache|body pain|pain relie|analgesic|backache|back pain"),
    ("rheumatism/arthritis", r"rheumat|arthrit|gout|joint pain"), ("bone fracture", r"fractur|bone"), ("sprain/dislocation", r"sprain|dislocat|swelling"),
    ("inflammation", r"inflam"), ("snakebite", r"snake"), ("insect/scorpion bite", r"insect|scorpion|bee sting|sting|leech"), ("dog bite/rabies", r"dog bite|rabies|hydrophob"),
    ("bleeding (haemostatic)", r"bleed|haemosta|hemosta|blood clot|stop blood"), ("anaemia", r"an(a)?emi"),
    ("hypertension", r"blood pressure|hypertens|\bbp\b"), ("heart disorder", r"heart|cardi"), ("blood purifier", r"blood purif|purify blood"),
    ("diabetes", r"diabet|blood sugar"), ("urinary disorder", r"urin|dysuria|diuret"), ("kidney stone", r"kidney stone|renal stone|calculi|\bstone"),
    ("menstrual disorder", r"menstru|dysmenor|period pain|menorrh"), ("childbirth/postpartum", r"delivery|child ?birth|labou?r pain|postpartum|after birth|placenta"),
    ("lactation", r"lactat|breast milk|milk secretion|galactag"), ("abortion/contraception", r"abort|contracept|antifertil"),
    ("leucorrhoea", r"leucorrh|leukorrh|white discharge"), ("infertility/sexual", r"infertil|steril|impoten|aphrodis|sexual|fertility"),
    ("gonorrhoea/STI", r"gonorr|syphil|venereal"), ("eye disorder", r"\beyes?\b|conjunctiv|ophthalm"), ("ear ache", r"\bears?\b|otitis|earache"),
    ("cancer/tumour", r"cancer|tumou?r"), ("epilepsy/convulsion", r"epilep|convuls|fits"), ("insomnia/mental", r"insomnia|sleep|mental|madness|insan"),
    ("poisoning/antidote", r"poison|antidote|intoxicat|hangover"), ("tonic/weakness", r"tonic|weakness|debility|vigour|energy"),
    ("goitre/thyroid", r"goit|thyroid"), ("obesity", r"obesity|weight loss"),
]
VOCAB = [(name, re.compile(pat, re.I)) for name, pat in CONDITIONS]
PART_RX = {"LEAF": r"lea[fv]", "ROOT": r"root", "BARK": r"bark", "FRUIT": r"fruit", "SEED": r"seed", "RHIZOME": r"rhizome",
           "WHOLEPLANT": r"whole|entire", "STEM": r"stem", "FLOWER": r"flower", "SHOOT": r"shoot|twig", "TUBER": r"tuber|bulb"}


def conditions(text):
    return [name for name, rx in VOCAB if rx.search(str(text))]


def letters(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def source_text(sid):
    for p in [ROOT / f"sources/text/{sid}.txt", *sorted((ROOT / "sources/new").glob(f"{sid}_*.txt")),
              *sorted((ROOT / "sources/gap").glob(f"{sid}_*.txt"))]:
        if p.exists():
            return p.read_text(errors="ignore")
    return None


class Src:
    def __init__(self, t):
        self.low = re.sub(r"\s+", " ", t.lower())
        self.flat = letters(t)

    def windows(self, species, size=700):
        g, *rest = species.lower().split()
        pat = re.escape(g) + r"\W{0,8}" + re.escape((rest or [""])[0][:4])
        ms = list(re.finditer(pat, self.low))[:15] or list(re.finditer(re.escape(g), self.low))[:8]
        return [self.low[m.start(): m.start() + size] for m in ms]


def main():
    d = pd.read_excel(ROOT / "output/NE_combined_v3.xlsx", "Data")
    meta = pd.read_csv(ROOT / "data/survey_metadata.csv").set_index("source_id")
    tax = pd.read_csv(ROOT / "data/taxonomy_gbif.csv").set_index("name_in_data")
    d["name_in_data"] = d["Botanical Name"].map(tx.norm_name)
    d["accepted_species"] = d.name_in_data.map(tax.accepted_species).where(d.name_in_data.map(tax.usable).fillna(False).astype(bool))
    d["accepted_family"] = d.name_in_data.map(tax.accepted_family)
    d["taxon"] = d.accepted_species.fillna(d.name_in_data + " [unresolved]")

    # community per record
    def community(r):
        m = meta.loc[r.SourceID]
        if m.attribution == "multi_community_explicit":
            t = str(r.Tribe)
            if r.SourceID == "S08":
                return [x.replace(" (non-tribal)", "") for x in t.split("; ")] if t != "UNRESOLVED" else ["UNRESOLVED"]
            return [t]
        return [m.communities]
    rows, texts = [], {}
    for r in d.itertuples():
        m = meta.loc[r.SourceID]
        if r.SourceID not in texts:
            t = source_text(r.SourceID); texts[r.SourceID] = Src(t) if t else None
        conds = conditions(r.Disease) or ["unspecified/other"]
        parts = [p for p, rx in PART_RX.items() if re.search(rx, str(r.Partsused), re.I)]
        S = texts[r.SourceID]
        wins = S.windows(r.name_in_data) if S else []
        for c in conds:
            rx = dict(VOCAB).get(c)
            verified = None if S is None or rx is None else any(rx.search(w) for w in wins)
            for com in community(r):
                rows.append(dict(
                    source_id=r.SourceID, fieldwork_group=m.fieldwork_group, community=com, state=str(r.State).replace("AP", "Arunachal Pradesh") if r.State == "AP" else r.State,
                    design=m.design, attribution=("pooled" if com == "UNRESOLVED" else m.attribution), is_primary=int(m.is_primary), non_st=int(m.non_st),
                    name_in_data=r.name_in_data, accepted_species=r.accepted_species, taxon=r.taxon, family=r.accepted_family,
                    condition=c, parts=";".join(parts) or "unknown", original_use_wording=str(r.Disease)[:300],
                    use_found_in_source=verified, parser_flag=int("generic table parser" in str(r.qc_flag)),
                    record_dataset=r.Dataset, record_row=r.Row))
    u = pd.DataFrame(rows)
    u.to_csv(ROOT / "output/evidence_records.csv", index=False)   # record x condition x community (before de-duplication)

    # collapse to independent units: one per fieldwork_group x community x taxon x condition
    key = ["fieldwork_group", "community", "taxon", "condition"]
    agg = u.groupby(key).agg(
        accepted_species=("accepted_species", "first"), family=("family", "first"), state=("state", "first"),
        source_ids=("source_id", lambda s: ";".join(sorted(set(s)))), n_records=("source_id", "size"),
        design=("design", lambda s: ";".join(sorted(set(s)))), attribution=("attribution", "first"),
        is_primary=("is_primary", "max"), non_st=("non_st", "max"),
        parts=("parts", lambda s: ";".join(sorted({p for x in s for p in x.split(";")}))),
        use_found_in_source=("use_found_in_source", lambda s: bool(s.fillna(False).any())),
        parser_flag=("parser_flag", "min"),
        original_use_wording=("original_use_wording", lambda s: " || ".join(dict.fromkeys(s))[:600]),
    ).reset_index()
    agg.to_csv(ROOT / "output/evidence_units.csv", index=False)
    pd.DataFrame(CONDITIONS, columns=["condition", "regex"]).to_csv(ROOT / "output/condition_vocabulary.csv", index=False)

    print(f"records {len(d)} -> record x condition x community {len(u)} -> independent units {len(agg)}")
    print("units by attribution:", agg.attribution.value_counts().to_dict())
    print("units by design:", agg.design.value_counts().to_dict())
    print("share of units whose use wording is found near the species in the source text:",
          round(agg.use_found_in_source.mean(), 3))
    print("unspecified condition share:", round((agg.condition == "unspecified/other").mean(), 3))
    print("distinct taxa:", agg.taxon.nunique(), "| communities:", agg.community.nunique(), "| fieldwork groups:", agg.fieldwork_group.nunique())


if __name__ == "__main__":
    main()
