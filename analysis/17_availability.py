"""Does local availability explain which plants are shared, and which uses are specific beyond popularity?

1. Availability proxy: GBIF occurrence records of the accepted taxon (GBIF backbone key) with country = India inside
   the box 21.9-29.5 N, 89.7-97.5 E (the seven states plus a sliver of north Bengal). GBIF's GADM state tags are
   missing for most Indian records, so a state filter returns near-zero counts. This is a coarse proxy:
   it mixes collecting effort with abundance and under-records cultivated plants; it is used for ranking only.
2. Species level: independent community reports (tier A, any use) ~ log(occurrences) - Spearman + negative binomial GLM.
   Species far above the fit are shared more widely than their recorded presence predicts.
3. Use specificity: for each taxon x condition, binomial tail P(X >= reports | n = reports of that taxon for any use,
   p = share of that condition among all tier-A units), Benjamini-Hochberg corrected. A significant pair is a use that
   communities converge on more than the plant's general popularity and the condition's general frequency imply.

Usage: .venv/bin/python analysis/17_availability.py
Writes data/gbif_ne_occurrences.csv (cache), output/availability_species.csv, output/use_specificity.csv, figures
"""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
GADM = ["IND.3_1", "IND.4_1", "IND.21_1", "IND.22_1", "IND.23_1", "IND.24_1", "IND.33_1"]
CACHE = ROOT / "data/gbif_ne_box_occurrences.csv"
UA = {"User-Agent": "ne-ethnomed-synthesis/0.1"}


def occ(key):
    q = "country=IN&decimalLatitude=21.9,29.5&decimalLongitude=89.7,97.5"
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(
                f"https://api.gbif.org/v1/occurrence/search?taxonKey={int(key)}&{q}&limit=0", headers=UA), timeout=40))
            return int(key), r["count"]
        except Exception:
            time.sleep(2 * (a + 1))
    return int(key), np.nan


def main():
    tax = pd.read_csv(ROOT / "data/taxonomy_gbif.csv")
    tax = tax[tax.usable]
    keys = sorted(set(tax.accepted_key.dropna().astype(int)))
    cache = pd.read_csv(CACHE) if CACHE.exists() else pd.DataFrame(columns=["accepted_key", "ne_occurrences"])
    todo = [k for k in keys if k not in set(cache.accepted_key)]
    print(f"{len(keys)} accepted taxa, {len(todo)} to query")
    with ThreadPoolExecutor(8) as ex:
        new = pd.DataFrame(list(ex.map(occ, todo)), columns=["accepted_key", "ne_occurrences"])
    cache = pd.concat([cache, new]).drop_duplicates("accepted_key", keep="last"); cache.to_csv(CACHE, index=False)
    key_of = tax.groupby("accepted_species").accepted_key.first()
    occ_of = cache.set_index("accepted_key").ne_occurrences

    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    A = u[(u.is_primary == 1) & (u.condition != "unspecified/other") & u.accepted_species.notna()]
    A = A.assign(report=A.fieldwork_group + "|" + A.community)
    sp = A.groupby("accepted_species").agg(reports=("report", "nunique"), states=("state", "nunique"), family=("family", "first"))
    sp["ne_occurrences"] = sp.index.map(key_of).map(occ_of)
    sp = sp.dropna(subset=["ne_occurrences"])
    sp["log_occ"] = np.log10(sp.ne_occurrences + 1)
    rho, p = stats.spearmanr(sp.log_occ, sp.reports)
    import statsmodels.api as sm
    X = sm.add_constant(sp[["log_occ"]])
    nb = sm.GLM(sp.reports, X, family=sm.families.NegativeBinomial(alpha=0.5)).fit()
    sp["expected_reports"] = nb.predict(X)
    sp["pearson_resid"] = (sp.reports - sp.expected_reports) / np.sqrt(sp.expected_reports + 0.5 * sp.expected_reports ** 2)
    sp = sp.sort_values("pearson_resid", ascending=False)
    sp.to_csv(ROOT / "output/availability_species.csv")

    # use specificity beyond popularity
    base = A.groupby("condition").report.size() / len(A)
    pairs = A.groupby(["accepted_species", "condition"]).report.nunique().rename("pair_reports").reset_index()
    pairs["species_reports"] = pairs.accepted_species.map(sp.reports)
    pairs["p_condition"] = pairs.condition.map(base)
    pairs = pairs.dropna()
    pairs["p_binom"] = stats.binom.sf(pairs.pair_reports - 1, pairs.species_reports.astype(int), pairs.p_condition)
    from statsmodels.stats.multitest import multipletests
    pairs["q_bh"] = multipletests(pairs.p_binom, method="fdr_bh")[1]
    pairs["specificity_ratio"] = (pairs.pair_reports / pairs.species_reports) / pairs.p_condition
    pairs = pairs.sort_values("q_bh")
    pairs.to_csv(ROOT / "output/use_specificity.csv", index=False)
    sig = pairs[(pairs.q_bh < 0.05) & (pairs.pair_reports >= 3)]

    out = {"species_tested": len(sp), "spearman_rho_reports_vs_log_occurrences": round(float(rho), 3), "spearman_p": float(p),
           "nb_coef_log_occ": round(float(nb.params["log_occ"]), 3), "nb_p_log_occ": float(nb.pvalues["log_occ"]),
           "species_with_zero_ne_gbif_records": int((sp.ne_occurrences == 0).sum()),
           "use_specific_pairs_q05_min3": len(sig)}
    print(json.dumps(out, indent=2))
    (ROOT / "output/availability_summary.json").write_text(json.dumps(out, indent=2))
    print("\nShared more widely than recorded presence predicts:")
    print(sp.head(12)[["reports", "states", "ne_occurrences", "expected_reports", "pearson_resid"]].round(2).to_string())
    print("\nUse-specific convergence (q<0.05, >=3 reports):")
    print(sig.head(20)[["accepted_species", "condition", "pair_reports", "species_reports", "specificity_ratio", "q_bh"]].round(4).to_string(index=False))

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(sp.log_occ, sp.reports + np.random.default_rng(1).uniform(-0.15, 0.15, len(sp)), s=8, alpha=0.45, color="#34495e")
    xs = np.linspace(sp.log_occ.min(), sp.log_occ.max(), 50)
    ax.plot(xs, nb.predict(sm.add_constant(pd.DataFrame({"log_occ": xs}))), color="#c0392b")
    for name, r in sp.head(6).iterrows():
        ax.annotate(name, (r.log_occ, r.reports), fontsize=6.5)
    ax.set_xlabel("log10(GBIF occurrences in the 7 states + 1)"); ax.set_ylabel("independent community reports")
    ax.set_title(f"Spearman rho = {rho:.2f}", fontsize=9); fig.tight_layout()
    fig.savefig(ROOT / "output/figures/fig_availability.png", dpi=200)


if __name__ == "__main__":
    main()
