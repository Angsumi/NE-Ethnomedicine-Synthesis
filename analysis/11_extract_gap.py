"""Extract records from the gap-filling papers in sources/gap with a generic table-row detector.

A row starts on a line where a binomial (known genus, or followed by an author abbreviation) begins in the
left part of the line. The row block runs until the next row start. Uses come from the "uses" column
(found from the header line) where possible; parts and family are read from the whole block.

Usage: .venv/bin/python analysis/11_extract_gap.py
Writes output/gap_sources_extracted.xlsx
"""
import importlib.util, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "sources/gap"
spec = importlib.util.spec_from_file_location("ex", ROOT / "analysis/08_extract_new.py")
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)

AUTH = r"(?:L\.|Linn|Roxb|Wall|DC\.?|Benth|Hook|Willd|Lam\b|Lamk|Retz|Burm|Blume|Sm\.|Jacq|Mill|Merr|Kurz|Buch|Ham|Gaertn|Schott|Nees|Pers|Spreng|Thunb|Lour|Hassk|Kunth|Engl|Desv|Schum|Sw\.|Wight|Arn|Gamble|Kuntze|Royle|D\.\s?Don|Vahl|Clarke|Griff|Koenig|Rosc|Miq|Mart|Planch|Decne|Prain|Medik|Stapf|Moench|Correa|Juss|Raf|Steud|Craib|Ridl|Haw|Salisb|Br\.|Poir|Cav|Dunal|Urb|Endl|Wedd|Kostel|Forssk|Spach|Bl\.|Dalz|Vent|Michx|Wendl|Nutt|Gaudich|Cham|Ker|Sims|Ait|Delile|Rchb|Hochst|Hassk|Muell|Arg|Chev)"
NOT = {"The", "This", "Table", "Plant", "Leaves", "Leaf", "Root", "Fruit", "Bark", "Seeds", "Stem", "Whole", "Young",
       "Paste", "Juice", "Decoction", "Used", "Mode", "Local", "Family", "Scientific", "Botanical", "Indian", "Journal"}

PAPERS = {
    "G02": dict(file="G02_Poumai_IJEP", state="Manipur", tribe="Poumai Naga", start=r"Table 1: List of medicinal plants", end=r"^\s*(4\.|Discussion|Conclusion)", uses=r"Uses|Ailment|Disease",
                ref="Documentation of medicinal plants traditionally used in health care by Poumai tribe of Manipur, India. International Journal of Economic Plants (2022), 9(2), 130-138. https://doi.org/10.23910/2/2022.0442b"),
    "G03": dict(file="G03_Rongmei_AJTCAM", state="Manipur", tribe="Rongmei Naga", start=r"^S\.\s+Name of the Plant", end=r"^\s*Discussion", uses=r"\bUses\b", width=130,
                ref="Prakash, N., et al. (2014). Indigenous traditional knowledge and usage of folk bio-medicines among Rongmei tribe of Tamenglong district of Manipur, India. Afr J Tradit Complement Altern Med, 11(3), 239-247. https://doi.org/10.4314/ajtcam.v11i3.34"),
    "G04": dict(file="G04_Paite_maternity", state="Manipur", tribe="Paite", start=r"Table 1:-Valuable", end=r"^\s*(Discussion|Conclusion)", uses=r"Purpose",
                ref="Devi, & Das (2018). Valuable medicinal plants used for maternity care by the Paite tribe of Manipur. International Journal of Advanced Research, 6(2), 825-828. https://doi.org/10.21474/IJAR01/6456"),
    "G09": dict(file="G09_Nocte_IJTK2025", state="Arunachal Pradesh", tribe="Nocte", start=r"Table 3 — Phytomedicine", end=r"Table 4 — Zootherapy", uses=r"Ethnomedicinal",
                ref="Cultural roots of healing: exploring ethnomedicine of the Nocte tribe. Indian Journal of Traditional Knowledge, 24(7), 665-676 (2025). https://doi.org/10.56042/ijtk.v24i7.18003"),
    "G10": dict(file="G10_Nocte_JBR2019", state="Arunachal Pradesh", tribe="Nocte", start=r"Table 1\. Ethnobotanically important", end=r"^\s*(Discussion|Conclusion|Acknowledg)", uses=r"Mode of Use",
                ref="Ethnobotanically important plants used by the Nocte tribe of Tirap district, Arunachal Pradesh. Journal of Bioresources, 6(1), 36-45 (2019)."),
    "G13": dict(file="G13_Tripura_jaundice", state="Tripura", tribe="Tripuri; Jamatia; Halam", start=r"Table 1: Enumeration", end=r"Table 2: Enumeration", uses=r"Dosage|Mode",
                ref="Deb, D., et al. (2016). Ethnomedicinal plants used for jaundice by tribes of Tripura. Biodiversitas, 17(1), 256-269. https://doi.org/10.13057/biodiv/d170137"),
    "G14": dict(file="G14_Ahom_antrocom", state="Assam", tribe="Ahom (non-ST)", start=r"Local Name\s+Scientific name", end=r"^\s*(Discussion|Conclusion|References)", uses=r"Mode of use",
                ref="Dutta (2023). Some traditional plants used by the Ahoms in health management and medicine in upper Assam, India. Antrocom Online Journal of Anthropology, 19(2), 197-200."),
    "G16": dict(file="G16_Meitei_sacredgrove", state="Manipur", tribe="Meitei", start=r"Table 3 — Ethnomedicinal association", end=r"^\s*(Discussion|Conclusion)\b", uses=r"Ethnomedicinal application",
                ref="Ethnobotany of medicinal trees of sacred groves of the Imphal valley (Meitei). Indian Journal of Traditional Knowledge, 24(10), 918-929 (2025). https://doi.org/10.56042/ijtk.v24i10.22353"),
    "G17": dict(file="G17_Lotha_IJTK2010", state="Nagaland", tribe="Lotha Naga", start=r"Table 1\W+Medicinal plants used by Lotha", end=r"^\s*(Acknowledg|References)", uses=r"Uses|Ailment",
                ref="Jamir, N. S., Takatemjen, & Limasemba (2010). Traditional knowledge of Lotha-Naga tribes in Wokha district, Nagaland. Indian Journal of Traditional Knowledge, 9(1), 45-48."),
    "G18": dict(file="G18_Arunachal_tribes_IJTK", state="Arunachal Pradesh", tribe=None, start=r"Table 1—Medicinal plants used by Apatani", end=r"^\s*(Acknowledg|References)", uses=r"\bUses\b|Mode of utilization",
                ref="Khongsai, M., Saikia, S. P., & Kayang, H. (2011). Ethnomedicinal plants used by different tribes of Arunachal Pradesh. Indian Journal of Traditional Knowledge, 10(3), 541-546."),
    "G19": dict(file="G19_Ao_Chungtia", state="Nagaland", tribe="Ao Naga", start=r"Plants documented from Chungtia village", end=r"^Table 2", uses=r"Recorded uses",
                ref="Kichu, M., Malewska, T., Akter, K., Imchen, I., Harrington, D., Kohen, J., Vemulpad, S. R., & Jamie, J. F. (2015). An ethnobotanical study of medicinal plants of Chungtia village, Nagaland, India. Journal of Ethnopharmacology, 166, 5-17. https://doi.org/10.1016/j.jep.2015.02.053"),
    "G21": dict(file="G21_KochRajbangshi_Bongaigaon", state="Assam", tribe="Koch-Rajbongshi (non-ST)", start=r"Table 1\. Medicinal plants used by Koch Rajbangshi", end=r"^\s*(Discussion|DISCUSSION|Conclusion)", uses=r"Disorders",
                ref="Das, A. K., Choudhury, M., & Sharma, G. C. (2013). Medicinal plants used by Koch Rajbangshi of North Salmara subdivision, Bongaigaon, Assam, India. Our Nature, 11(1), 45-53. https://doi.org/10.3126/on.v11i1.8243"),
    "G22": dict(file="G22_Koch_SSalmara", state="Assam", tribe="Koch", start=r"Table 1 :List of plants showing", end=r"^\s*(Discussion|DISCUSSION|Conclusion|CONCLUSION)", uses=r"Name of disease",
                ref="Majumdar, Roy, & Koch (2019). Studies on traditional phytotherapy of Koch community of South Salmara-Mankachar district, Assam. Plant Archives, 19(1), 83-91."),
    "G23": dict(file="G23_Koch_Meghalaya", state="Meghalaya", tribe="Koch (Meghalaya)", start=r"Table 1 — List of plants showing", end=r"^\s*(Discussion|Conclusion)", uses=r"Mode of administration", prefix="Liver disorder / jaundice (hepatoprotective); ",
                ref="Traditional hepatoprotective herbal medicine of Koch tribe in the South-West Garo hills district, Meghalaya. Indian Journal of Traditional Knowledge, 18(2), 312-317 (2019)."),
    "G26": dict(file="G26_PnarWar_WJaintia", state="Meghalaya", tribe="Jaintia (Pnar; War)", start=r"Table 6 — Mode of preparation", end=r"Table 7 — Informant", uses=r"Diseases",
                ref="Langshiang, E. S., et al. (2020). Traditional healing practices of Pnar and War communities in West Jaintia Hills district of Meghalaya, Northeast India. Indian Journal of Traditional Knowledge, 19(4), 776-787."),
    "G27": dict(file="G27_Sangtam_Tuensang", state="Nagaland", tribe="Sangtam Naga", start=r"Table 1: Medicinal plants and their uses", end=r"Table 2: Animals", uses=r"Preparation and Uses",
                ref="Ethnomedical practices among the Sangtam Naga of Tuensang town, Nagaland. Antrocom Online Journal of Anthropology, 21(2), 499-506 (2025)."),
    "G33": dict(file="G33_Senapati_IJTK2025", state="Manipur", tribe="Senapati healers (mixed, incl. Mao)", start=r"Table 2 — List of medicinal plants used by the traditional healers", end=r"^\s*(Discussion|Table 3)", uses=r"Traditional Uses",
                ref="Thokchom, B., et al. (2025). Ethnobotany of traditional medicinal plants used in Senapati district of Manipur, Northeastern India. Indian Journal of Traditional Knowledge, 24(2), 112-123. https://doi.org/10.56042/ijtk.v24i2.8847"),
}
G18_CODES = {"Ap": "Apatani", "M": "Monpa", "S": "Singpho", "T": "Tangsa", "P": "Adi (Padam)", "N": "Nyishi", "I": "Idu Mishmi"}
SKIP = re.compile(r"Indian Journal of Traditional|Journal of Bioresources|Afr J Tradit|Int\. J\. Adv\. Res|Biodiversitas|BIODIVERSITAS|"
                  r"Antrocom|International Journal of Economic|^\s*\d{1,3}\s*$|Contd|Continue\.\.\.|\(Contd\.\)")


def known_genera():
    d = pd.read_excel(ROOT / "output/NE_combined_v2.xlsx", "Data")
    return {str(s).split()[0].lower() for s in d["Botanical Name"].dropna()}


def row_start(line, genera, width=70, nxt="", scol=None):
    # genus alone at line start with the epithet on the next line ("Achyranthes" / "aspera L.")
    m0 = re.match(r"^\s{0,3}([A-Z][a-z]{3,})(?:\s{2,}|$)", line)
    m1 = re.match(r"^\s{0,3}([a-z][a-z\-]{2,})\b", nxt)
    if m0 and m1 and m0.group(1).lower() in genera:
        class M:  # minimal match-like object
            def __init__(s, g, e): s._g = (g, e)
            def group(s, i): return s._g[i - 1]
            def end(s): return len(line)
        return M(m0.group(1), m1.group(1))
    for m in re.finditer(r"([A-Z][a-z]{2,})\s{1,9}([a-z][a-z\-]{2,})", line[:width]):
        g = m.group(1)
        if g in NOT or g.endswith("aceae"):
            continue
        in_col = (scol is not None and abs(m.start() - scol) <= 4) or (m.start() <= 3 and re.search(r"\S\s{3,}\S", line[m.end():]))
        if in_col and m.group(2) not in {"plant", "name", "used", "local", "tribe", "and", "the"}:
            return m
        if g.lower() in genera or re.match(r"\s*\(?[A-Z]?[a-z]*\.?\)?\s*" + AUTH, line[m.end(): m.end() + 30]):
            return m
    return None


def extract(sid, P, genera):
    lines = ex.fix_glyphs((GAP / f"{P['file']}.txt").read_text(errors="ignore")).splitlines()
    out, i = [], 0
    while i < len(lines):
        if not re.search(P["start"], lines[i]):
            i += 1; continue
        # header line holds the 'uses' column
        ucol = scol = None
        for h in lines[i: i + 6]:
            m = re.search(P["uses"], h)
            if m and ucol is None: ucol = m.start()
            m = re.search(r"Scientific [Nn]ame|Botanical [Nn]ame|Plant name|Name of the\s*$", h)
            if m and scol is None: scol = m.start()
        j = i + 1
        block = None
        while j < len(lines) and not re.search(P["end"], lines[j]) and not (j > i + 1 and re.search(P["start"], lines[j])):
            ln = lines[j]
            if SKIP.search(ln) or not ln.strip():
                j += 1; continue
            m = row_start(ln, genera, P.get("width", 70), lines[j + 1] if j + 1 < len(lines) else "", scol)
            if m:
                if block: out.append(block)
                block = {"sp": f"{m.group(1)} {m.group(2)}", "lines": [], "uses": []}
            if block:
                block["lines"].append(ln)
                if ucol is not None and len(ln) > ucol - 3:
                    a = ucol - 3
                    while a > 0 and ln[a - 1] != " ": a -= 1
                    block["uses"].append(ln[a:])
            j += 1
        if block: out.append(block)
        i = j
    recs = []
    for b in out:
        text = ex.clean(" ".join(b["lines"]))
        uses = P.get("prefix", "") + (ex.clean(" ".join(b["uses"])) or text)
        fam = (re.search(r"([A-Z][a-z]+aceae)", text) or [None, ""])[1]
        if not fam:   # family printed in another table of the same paper
            g0 = b["sp"].split()[0]
            fam = next((m.group(1) for ln in lines if g0 in ln for m in [re.search(r"([A-Z][a-z]+aceae)", ln)] if m), "")
        tribes = [P["tribe"]]
        if sid == "G18":
            codes = re.findall(r"\b(Ap|M|S|T|P|N|I)\b(?=[,\s)]|$)", text)
            tribes = sorted({G18_CODES[c] for c in codes}) or ["Arunachal tribes (unspecified)"]
        for t in tribes:
            r = ex.rec("N03", b["sp"].upper(), fam, "", text, uses, uses, tribe=t)   # rec() needs a known key
            r.update(SourceID=sid, State=P["state"], Reference=P["ref"], parts_as_in_paper="")
            r["Partsused"] = ex.parts(text)
            recs.append(r)
    return recs


WANCHO = [  # Wangjen et al. 2011, Table 1 (scanned; transcribed from OCR)
    ("ACORUS CALAMUS", "Acoraceae", "Wok-kak hing", "Leaves", "Stomach ache"),
    ("ALSTONIA SCHOLARIS", "Apocynaceae", "Tsam tson pan", "Leaves", "Wound healing"),
    ("CASSIA ALATA", "Fabaceae", "Khatri pan", "Leaves", "Skin disease"),
    ("CENTELLA ASIATICA", "Apiaceae", "Lum-loh", "Whole plant", "Stomach ache and dysentery"),
    ("CHRYSANTHEMUM INDICUM", "Asteraceae", "Hahkak rangkak", "Leaves", "Pain relief"),
    ("ERYTHRINA STRICTA", "Fabaceae", "Shit pan", "Flower", "Scorpion sting"),
    ("EUPHORBIA LIGULARIS", "Euphorbiaceae", "Thamran-hingnu", "Stem", "Bone fracture"),
    ("LITSEA POLYANTHA", "Lauraceae", "Ngop", "Stem", "Bleeding stopper"),
    ("OROXYLUM INDICUM", "Bignoniaceae", "Pan okui", "Root", "Stomach problems"),
    ("PHLOGACANTHUS CURVIFLORUS", "Acanthaceae", "Thamran hingsa", "Leaves", "Cut wounds"),
    ("PHLOGACANTHUS THYRSIFLORUS", "Acanthaceae", "Ran hing", "Leaves", "Stomach ache and dysentery"),
    ("SCOPARIA DULCIS", "Plantaginaceae", "Lumpu panchong", "Leaves", "Jaundice"),
    ("TETRASTIGMA SERRULATUM", "Vitaceae", "Van-huak hing", "Leaves", "Fire wound"),
]
WANCHO_REF = "Wangjen, K., Chaudhry, S., Arya, S. C., & Samal, P. K. (2011). A preliminary investigation on ethnomedicinal plants used by Wancho tribes of Arunachal Pradesh, India. (G.B. Pant Institute; ICIMOD library record kfn2a-z0668)."
JAINTIA_REF = "Sajem, A. L., & Gosai, K. (2006). Traditional use of medicinal plants by the Jaintia tribes in North Cachar Hills district of Assam, northeast India. Journal of Ethnobiology and Ethnomedicine, 2, 33. https://doi.org/10.1186/1746-4269-2-33"


def manual_and_xml():
    out = []
    for sp, f, l, p, u in WANCHO:
        r = ex.rec("N03", sp, f, l, p, u, u, tribe="Wancho")
        r.update(SourceID="G29", State="Arunachal Pradesh", Reference=WANCHO_REF, parts_as_in_paper=p)
        out.append(r)
    import html as _h
    t = (GAP / "G20_Jaintia_NCHills_JEE.xml").read_text()
    tw = re.findall(r"<table-wrap.*?</table-wrap>", t, re.S)[0]
    for row in re.findall(r"<tr.*?</tr>", tw, re.S)[1:]:
        c = [_h.unescape(ex.clean(re.sub(r"<[^>]+>", " ", x))) for x in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        if len(c) < 4 or not ex.binomial(c[0]): continue
        fam = (re.search(r"([A-Z][a-z]+aceae)", c[0]) or [None, ""])[1]
        r = ex.rec("N03", ex.binomial(c[0]), fam, c[1], c[2], c[3], c[3], tribe="Jaintia (Assam)")
        r.update(SourceID="G20", State="Assam", Reference=JAINTIA_REF, parts_as_in_paper=c[2])
        out.append(r)
    return out


def main():
    genera = known_genera()
    allr = manual_and_xml()
    print(f"G29 Wancho (manual): 13 | G20 Jaintia NC Hills (XML): {sum(r['SourceID']=='G20' for r in allr)}")
    for sid, P in PAPERS.items():
        r = extract(sid, P, genera)
        print(f"{sid} {P['tribe'] or 'per-plant tribes'}: {len(r)} records, {len({x['Botanical Name'] for x in r})} species")
        allr += r
    d = pd.DataFrame(allr)
    # drop text fragments caught as names, and truncated duplicates ("Saccharum sponta" vs "Saccharum spontaneum")
    junk_g = {"Drug", "Maximum", "Medicine", "Informant", "Meitei", "Duron", "Herb", "Famine", "Food"}
    junk_e = {"and", "species", "preparation", "usage", "consensus", "society", "bon", "sp", "spp"}
    g_e = d["Botanical Name"].str.capitalize().str.split(n=1, expand=True)
    d = d[~g_e[0].isin(junk_g) & ~g_e[1].isin(junk_e)]
    names = set(d["Botanical Name"])
    trunc = {n for n in names for m in names if n != m and m.startswith(n) and len(m) - len(n) >= 2}
    d = d[~d["Botanical Name"].isin(trunc)]
    # one record per source x species x tribe; a species re-detected inside another row's text is merged
    agg = {c: "first" for c in d.columns if c not in ("SourceID", "Botanical Name", "Tribe")}
    agg["Disease"] = lambda s: " | ".join(dict.fromkeys(x for x in s if x))
    agg["Partsused"] = lambda s: ",".join(sorted({p for x in s for p in str(x).split(",") if p}))
    d = d.groupby(["SourceID", "Botanical Name", "Tribe"], as_index=False, sort=False).agg(agg)
    d["ActedUpon"] = d["Disease"].map(ex.systems)
    print("after merge:", d.groupby("SourceID")["Botanical Name"].nunique().to_dict())
    d["ActedUpon_source"] = "auto-assigned from Disease text"
    src = pd.DataFrame([dict(SourceID=k, state=v["state"], tribe=v["tribe"] or "per record (codes)", reference=v["ref"])
                        for k, v in PAPERS.items()] + [
        dict(SourceID="G29", state="Arunachal Pradesh", tribe="Wancho", reference=WANCHO_REF),
        dict(SourceID="G20", state="Assam", tribe="Jaintia (Assam)", reference=JAINTIA_REF)])
    with pd.ExcelWriter(ROOT / "output/gap_sources_extracted.xlsx") as xw:
        d.to_excel(xw, sheet_name="Records", index=False)
        src.to_excel(xw, sheet_name="Sources", index=False)
    if "G18" in set(d.SourceID):
        print(d[d.SourceID == "G18"].Tribe.value_counts().to_dict())


if __name__ == "__main__":
    main()
