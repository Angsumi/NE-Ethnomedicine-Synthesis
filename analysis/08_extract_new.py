"""Extract plant-use records from newly added papers (sources/new) into the NE5 schema.

Usage: .venv/bin/python analysis/08_extract_new.py
Writes output/new_sources_extracted.xlsx (sheets: Records, Sources)
"""
import html, re
from pathlib import Path
import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "sources/new"

SOURCES = {
    "N03": dict(file="N03_Tripura_Tripuri_Majumdar", state="Tripura", tribe="Tripuri",
                ref="Majumdar, K., & Datta, B. K. (2007). A study on ethnomedicinal usage of plants among the folklore herbalists and Tripuri medical practitioners: Part-II. Natural Product Radiance, 6(1), 66-73."),
    "N05": dict(file="N05_Garo_bonefracture", state="Meghalaya", tribe="Garo",
                ref="Marak, A. D., & Mathew, B. (2020). Traditional healing methods for bone fracture practiced by the Garo tribe of Meghalaya. Plant Archives, 20(1), 754-758."),
    "N06": dict(file="N06_Mizoram_Ralte2024", state="Mizoram", tribe=None,
                ref="Ralte, L., Sailo, H., & Singh, Y. T. (2024). Ethnobotanical survey of medicinal plants used by various ethnic tribes of Mizoram, India. PLoS ONE, 19(5), e0302792. https://doi.org/10.1371/journal.pone.0302792"),
    "N07": dict(file="N07_Mizoram_West2024", state="Mizoram", tribe="Mizo",
                ref="Ralte, L., Sailo, H., & Singh, Y. T. (2024). Ethnobotanical study of medicinal plants used by the indigenous community of the western region of Mizoram, India. Journal of Ethnobiology and Ethnomedicine, 20, 2. https://doi.org/10.1186/s13002-023-00642-z"),
    "N08": dict(file="N08_Monpa_Zemithang", state="Arunachal Pradesh", tribe="Monpa",
                ref="Tsering, J., Gogoi, B. J., Hui, P. K., Tam, N., & Tag, H. (2017). Ethnobotanical appraisal on wild edible plants used by the Monpa community of Arunachal Pradesh / First report on the ethnopharmacological uses of medicinal plants by Monpa tribe from the Zemithang region. (PMC5371772)"),
    "N09": dict(file="N09_Tangkhul_ERA", state="Manipur", tribe="Tangkhul Naga",
                ref="Shimrah, T., Leisan, J., & Lungleng, P. Cultural consensus in medicinal plant use among the Tangkhul Naga of Northeast India. Ethnobotany Research and Applications."),
    "N10": dict(file="N10_Bishnupriya_ERA", state="Tripura", tribe="Bishnupriya Manipuri (non-ST)",
                ref="Dhar, C., Bhagawati, M., et al. (2025). Documentation of ethnomedicinal knowledge of native flora utilized by Bishnupriya Manipuri people of Tripura, India. Ethnobotany Research and Applications, 31, 59. http://dx.doi.org/10.32859/era.31.59.1-29"),
}

SYS = [
    ("DIGESTIVE", r"stomach|dysenter|diarr|constipat|indigest|dyspeps|gastr|jaundice|liver|hepat|piles|haemorrhoid|hemorrhoid|worm|helminth|vomit|nausea|colic|tooth|dental|gum|mouth|acidity|flatul|appetite|cholera|abdomin|intestin|carminat|digest|peptic|ulcer|stomachic|purgative|laxative|bowel|cleft|tongue"),
    ("INTEGUMENTARY", r"skin|wound|\bcut|burn|boil|eczema|itch|scabies|ringworm|leprosy|dandruff|hair|acne|sore|fung|lice|leucoderm|abscess|blister|allerg|dermat|pimple|wart|swelling"),
    ("CIRCULATORY", r"haemosta|hemosta|blood clot|blood pressure|hypertens|\bbp\b|heart|cardi|an(a)?emi|blood purif|haemorrh|hemorrh|bleed|cholesterol|circulat"),
    ("RESPIRATORY", r"cough|cold|asthma|bronch|pneumon|tubercul|throat|tonsil|sinus|nasal|chest|respirat|breath|lung"),
    ("NERVOUS", r"intoxicat|headache|epilep|insomni|mental|nerv|paralys|migraine|sedative|madness|convuls|dizz|memory"),
    ("MUSCULOSKELETAL", r"fractur|bone|joint|rheumat|arthrit|sprain|body pain|back pain|muscle|gout|dislocat"),
    ("URINARY", r"urin|kidney|renal|stone|dysuria|diuret"),
    ("REPRODUCTIVE", r"fertil|conception|morning sickness|menstru|abortion|delivery|child ?birth|lactat|leucorr|steril|infertil|gonorr|syphil|sex|impoten|uter|postpartum|labou?r|pregnan"),
    ("ENDOCRINE", r"diabet|thyroid|goit|blood sugar"),
    ("IMMUNE", r"fever|malaria|typhoid|measles|chicken ?pox|small ?pox|infection|antisept|antibacter"),
    ("SENSORY", r"\beye|\bear\b|ear ?ache|conjunctiv|vision"),
    ("NEOPLASMS", r"cancer|tumou?r"),
    ("VETERINARY", r"\bcows?\b|cattle|livestock|goat|\bpigs?\b|poultry|animal"),
    ("NON-MEDICINAL", r"poison fish|fish poison|poisoning \(killing\) fish|ripening|machete|anok"),
    ("GENERAL/UNSPECIFIED", r"tonic|inflam|pain|poison|snake|scorpion|bite|sting|weakness|fatigue|antidote"),
]
PART_WORDS = [("WHOLEPLANT", r"whole|entire"), ("ROOT", r"root"), ("RHIZOME", r"rhizome"), ("BARK", r"bark"),
              ("LEAF", r"lea[fv]"), ("FRUIT", r"fruit|pulp|rind|peel"), ("SEED", r"seed|grain|nut"),
              ("FLOWER", r"flower|inflores|bud"), ("STEM", r"stem|wood|vine|petiole"), ("SHOOT", r"shoot|twig|tender"),
              ("TUBER", r"tuber|bulb|corm"), ("LATEX", r"latex|sap|gum|resin|exudate|oil"), ("AERIALPART", r"aerial")]


def systems(dis):
    t = str(dis).lower()
    out = [name for name, pat in SYS if re.search(pat, t)]
    return ",".join(out) or "GENERAL/UNSPECIFIED"


def parts(txt):
    t = str(txt).lower()
    return ",".join(p for p, pat in PART_WORDS if re.search(pat, t)) or "NOTSPECIFIED"


def binomial(s):
    s = re.sub(r"^\s*([A-Z][a-z]+) ([a-z]{1,3}) ([a-z]{3,})", r"\1\2 \3", str(s))   # "Agerati na adenophora"
    m = re.search(r"([A-Z][a-z]+)\s*(?:x\s+)?([a-z][a-z\-]+)", str(s))
    return f"{m.group(1)} {m.group(2)}".upper() if m else None


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def rec(sid, sp, fam, local, part_txt, disease, way, tribe=None):
    S = SOURCES[sid]
    return {"SourceID": sid, "Botanical Name": sp, "Family Name": clean(fam).upper(), "Common Name": clean(local),
            "Partsused": parts(part_txt), "Disease": clean(disease), "ActedUpon": systems(disease),
            "Way to Use": clean(way), "Tribe": tribe or S["tribe"], "State": S["state"], "Reference": S["ref"],
            "parts_as_in_paper": clean(part_txt)}


# ---------- XML (Europe PMC JATS) ----------
def xml_tables(name):
    t = (NEW / f"{name}.xml").read_text()
    out = []
    for tw in re.findall(r"<table-wrap.*?</table-wrap>", t, re.S):
        rows = []
        for r in re.findall(r"<tr.*?</tr>", tw, re.S):
            rows.append([html.unescape(clean(re.sub(r"<[^>]+>", " ", c))) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)])
        out.append(rows)
    return out


TRIBE_MAP = {"lushai": "Mizo (Lushai)", "mizo": "Mizo (Lushai)", "chakma": "Chakma", "bru": "Bru (Reang)",
             "lai": "Lai", "mara": "Mara", "hmar": "Hmar", "paite": "Paite", "ralte": "Mizo (Lushai)"}


def n06():
    rows = xml_tables(SOURCES["N06"]["file"])[1]
    out = []
    for r in rows[1:]:
        if len(r) < 9: continue
        sp = binomial(r[1])
        tribes = sorted({TRIBE_MAP.get(t.lower().strip(), t.strip()) for t in re.findall(r"\(([A-Za-z ]+)\)", r[2])}) or ["Mizo (various)"]
        local = re.sub(r"\s*\([^)]*\)", "", r[2])
        for tr in tribes:
            out.append(rec("N06", sp, r[3], local, r[6], r[7], r[8], tribe=tr))
    return out


def n07():
    rows = xml_tables(SOURCES["N07"]["file"])[1]
    return [rec("N07", binomial(r[1]), r[2], r[3], r[5], r[7], r[6]) for r in rows[1:] if len(r) >= 8 and binomial(r[1])]


def n08():
    tabs = xml_tables(SOURCES["N08"]["file"])
    fam = {binomial(r[1]): r[2] for r in tabs[1][1:] if len(r) >= 3 and binomial(r[1])}
    out = []
    for r in tabs[0][1:]:
        if len(r) < 7: continue
        for m in re.finditer(r"([A-Z][a-z]+) ([a-z][a-z\-]+)", r[3]):
            sp = f"{m.group(1)} {m.group(2)}".upper()
            if sp not in fam: continue
            out.append(rec("N08", sp, fam.get(sp, ""), r[1], r[4], r[6], f"{r[2]}: {r[5]}"))
    return out


# ---------- PDF tables ----------
def n09():
    out, cur = [], None
    with pdfplumber.open(NEW / f"{SOURCES['N09']['file']}.pdf") as pdf:
        for p in pdf.pages:
            for t in p.extract_tables():
                for r in t:
                    if len(r) < 7 or (r[0] or "").startswith("Botanical"):
                        continue
                    if r[0] and binomial(r[0]):
                        if cur: out.append(cur)
                        cur = [clean(x) for x in r[:7]]
                    elif cur:
                        cur = [clean(f"{a} {b or ''}") for a, b in zip(cur, r[:7])]
    if cur: out.append(cur)
    join = lambda x: re.sub(r"^([A-Z][a-z]+) ([a-z]{1,3}) ([a-z]{3,})", r"\1\2 \3", x)
    return [rec("N09", binomial(join(r[0])), r[1], r[2], r[3], r[5], r[4]) for r in out]


SKIP = re.compile(r"Natural Product Radiance|Ethnobotany Research and Applications|^\s*\d{1,3}\s*$|Vol 6\(1\)|"
                  r"Explorer: Research|Species name\s+Family|S\. No\.|Bengali \(B\)|Kokborok \(K\)|& Habit|ility status|^\s*Table \d")


def layout_rows(lines, start_re, n_right):
    """Group lines into table rows. Column starts for the right-hand columns come from each row's first line."""
    rows, cur = [], None
    for ln in lines:
        if not ln.strip() or SKIP.search(ln):
            continue
        if re.match(start_re, ln):
            if cur: rows.append(cur)
            fields = [(m.start(), m.group()) for m in re.finditer(r"\S+(?: \S+)*", ln)]
            starts = [s for s, _ in fields][-n_right:]
            cur = {"starts": starts, "left": [], "right": [[] for _ in range(n_right)]}
        if cur is None:
            continue
        st = cur["starts"]
        cur["left"].append(ln[: st[0]])
        for i, s in enumerate(st):
            e = st[i + 1] if i + 1 < len(st) else None
            # snap to whitespace so words cut by the boundary stay whole
            a = s
            while 0 < a < len(ln) and ln[a - 1] != " ": a -= 1
            b = e
            if b is not None:
                while b < len(ln) and ln[b - 1] != " ": b += 1
            cur["right"][i].append(ln[a:b] if a < len(ln) else "")
    if cur: rows.append(cur)
    return [(clean(" ".join(r["left"])), [clean(" ".join(c)) for c in r["right"]]) for r in rows]


def n03():
    lines = (NEW / f"{SOURCES['N03']['file']}.txt").read_text().splitlines()
    a = next(i for i, l in enumerate(lines) if "Table 1: Ethnomedicinal plants used by the Tripuri" in l)
    b = next(i for i, l in enumerate(lines) if i > a and re.match(r"^\s*(Discussion|Acknowledg|References)", l))
    out = []
    for left, (status, part, uses) in layout_rows(lines[a:b], r"^ {0,3}\\?\d{1,2} {2,}[A-Z][a-z]+ ", 3):
        body = re.sub(r"^\\?\d{1,2}\s+", "", left)
        part = " ".join(w for w in part.split() if re.search(r"(?i)leaf|leave|root|bark|seed|fruit|flower|stem|shoot|twig|whole|plant|rhizome|bulb|tuber|latex|petiole|young|tender|under|ground|and|aerial", w))
        sp = binomial(body)
        fam = (re.search(r"([A-Z][a-z]+aceae)", body) or [None, ""])[1]
        local = "; ".join(re.findall(r"([A-Z][\w\- ,]+?)\s*\((?:B|K)\)", body))
        out.append(rec("N03", sp, fam, local, part, uses, uses))
    return out


def fix_glyphs(t):
    """ERA PDF font maps ligatures to odd characters: sa5vum->sativum, HouAuynia->Houttuynia, PreparaJon->Preparation."""
    t = t.replace("\ufb00", "ff").replace("\ufb03", "ffi").replace("\ufb01", "fi").replace("\ufb02", "fl")
    t = re.sub(r"(?<=[a-z])[5JK](?=[a-z])", "ti", t)
    t = re.sub(r"(?<=[a-z])A(?=[a-z])", "tt", t)
    for a, b in [("Ensre", "Entire"), ("intessn", "intestin"), ("urinason", "urination"), ("mensoned", "mentioned"),
                 ("sason", "sation"), ("carminasve", "carminative"), ("Myrisscaceae", "Myristicaceae")]:
        t = t.replace(a, b)
    return t


def n10():
    lines = fix_glyphs((NEW / f"{SOURCES['N10']['file']}.txt").read_text()).splitlines()
    a = next(i for i, l in enumerate(lines) if l.startswith("Table 2. List of plants"))
    b = next(i for i, l in enumerate(lines) if l.startswith("Table 3."))
    out = []
    for left, (part, prep, route, appl) in layout_rows(lines[a + 1:b], r"^ {0,3}[A-Z][a-z]+\b(?=.*aceae)", 4):
        left = re.sub(r"\s*[×x]\s+", " ", left)
        sp = binomial(re.sub(r"PN/.*?;\s*\S+", " ", left))
        fam = (re.search(r"([A-Z][a-z]+aceae)", left) or [None, ""])[1]
        local = clean(re.sub(r".*aceae,?\s*(Herb|Shrub|Tree|Climber|Creeper|Fern|Grass|Palm)?", "", left).split("PN/")[0])
        out.append(rec("N10", sp, fam, local, part, appl, f"{prep}; {route}"))
    return out


GARO = [  # transcribed from Tables 1-4 of Marak & Mathew 2020 (all for bone fracture)
    ("CISSUS QUADRANGULARIS", "Vitaceae", "Char shira", "Stem"), ("CISSUS TRIANGULARIS", "Vitaceae", "Tin shira", "Stem"),
    ("COLOCASIA ESCULENTA", "Araceae", "Matchitagong", "Leaf"), ("STYRAX SERRULATUM", "Styracaceae", "Bolnarang", "Bark"),
    ("ORNITHOGALUM UMBELLATUM", "Asparagaceae", "Bethlehem", "Whole plant"), ("CRINUM DEFIXUM", "Amaryllidaceae", "Rajamuri", "Leaf"),
    ("JUSTICIA GENDARUSSA", "Acanthaceae", "Dojagipe", "Leaf"), ("BALIOSPERMUM MONTANUM", "Euphorbiaceae", "Boldokakki", "Bark"),
    ("BRACHYGLOTTIS REPANDA", "Asteraceae", "Rangjora", "Leaf"), ("ZINGIBER OFFICINALE", "Zingiberaceae", "Eching", "Rhizome"),
    ("ADIANTUM LUNULATUM", "Pteridaceae", "Dokongsibijak", "Whole plant"), ("CAREYA ARBOREA", "Lecythidaceae", "Gimbil", "Leaf"),
    ("TINOSPORA CORDIFOLIA", "Menispermaceae", "Amtrutrubudu", "Vine"), ("TERMINALIA ARJUNA", "Combretaceae", "Arjun", "Bark"),
]


def n05():
    return [rec("N05", sp, f, l, p, "Bone fracture", "Paste/poultice applied by traditional bone-setters") for sp, f, l, p in GARO]


def main():
    recs = []
    for fn in (n03, n05, n06, n07, n08, n09, n10):
        r = fn()
        print(f"{fn.__name__}: {len(r)} records, {len({x['Botanical Name'] for x in r})} species")
        recs += r
    d = pd.DataFrame(recs)
    d = d[d["Botanical Name"].notna()]
    d["Botanical Name"] = d["Botanical Name"].replace({"TRIDA PROCUMBENS": "TRIDAX PROCUMBENS"})
    d["ActedUpon_source"] = "auto-assigned from Disease text"
    src = pd.DataFrame([dict(SourceID=k, state=v["state"], tribe=v["tribe"] or "per record", reference=v["ref"])
                        for k, v in SOURCES.items()])
    out = ROOT / "output/new_sources_extracted.xlsx"
    with pd.ExcelWriter(out) as xw:
        d.to_excel(xw, sheet_name="Records", index=False)
        src.to_excel(xw, sheet_name="Sources", index=False)
    print(d.groupby(["SourceID", "Tribe"]).size().to_string())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
