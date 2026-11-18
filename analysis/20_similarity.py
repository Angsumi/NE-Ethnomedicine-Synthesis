"""Does medicinal knowledge follow geography, language, or neither?

Assemblage = one community in one independent fieldwork group (primary, explicit attribution, general-design surveys).
For every pair of assemblages:
  - species Jaccard: overlap of the plants used (reflects shared flora AND shared knowledge)
  - use congruence: among plants BOTH use, the share used for at least one common condition.
    Conditioning on shared plants removes availability from the comparison.
Predictors: great-circle distance (log km), same language family, same linguistic subgroup, same state.
Inference: multiple regression on distance matrices (MRM) with 999 assemblage-label permutations (QAP),
which respects the non-independence of pairwise data.

Usage: .venv/bin/python analysis/20_similarity.py
Writes output/assemblages.csv, output/pairwise_similarity.csv, output/similarity_mrm.json
"""
import itertools, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(2026)

# community -> (language family, subgroup); current language of daily use
LANG = {
    "Apatani": ("Tibeto-Burman", "Tani"), "Adi (Minyong)": ("Tibeto-Burman", "Tani"), "Adi (Padam)": ("Tibeto-Burman", "Tani"),
    "Galo": ("Tibeto-Burman", "Tani"), "Nyishi": ("Tibeto-Burman", "Tani"), "Tagin": ("Tibeto-Burman", "Tani"), "Mishing": ("Tibeto-Burman", "Tani"),
    "Mishmi": ("Tibeto-Burman", "Mishmic"), "Idu Mishmi": ("Tibeto-Burman", "Mishmic"), "Monpa": ("Tibeto-Burman", "Bodish"),
    "Aka (Hrusso)": ("Tibeto-Burman", "Hrusish"), "Singpho": ("Tibeto-Burman", "Jingpho"),
    "Konyak Naga": ("Tibeto-Burman", "Konyak"), "Nocte": ("Tibeto-Burman", "Konyak"), "Wancho": ("Tibeto-Burman", "Konyak"), "Tangsa": ("Tibeto-Burman", "Konyak"),
    "Angami Naga": ("Tibeto-Burman", "Naga"), "Ao Naga": ("Tibeto-Burman", "Naga"), "Lotha Naga": ("Tibeto-Burman", "Naga"), "Sangtam Naga": ("Tibeto-Burman", "Naga"),
    "Tangkhul Naga": ("Tibeto-Burman", "Naga"), "Poumai Naga": ("Tibeto-Burman", "Naga"), "Rongmei Naga": ("Tibeto-Burman", "Naga"),
    "Mizo": ("Tibeto-Burman", "Kuki-Chin"), "Lai": ("Tibeto-Burman", "Kuki-Chin"), "Mara": ("Tibeto-Burman", "Kuki-Chin"), "Hmar": ("Tibeto-Burman", "Kuki-Chin"),
    "Bawm": ("Tibeto-Burman", "Kuki-Chin"), "Paite": ("Tibeto-Burman", "Kuki-Chin"), "Karbi": ("Tibeto-Burman", "Karbi"),
    "Bodo": ("Tibeto-Burman", "Bodo-Garo"), "Rabha": ("Tibeto-Burman", "Bodo-Garo"), "Sonowal Kachari": ("Tibeto-Burman", "Bodo-Garo"),
    "Tiwa": ("Tibeto-Burman", "Bodo-Garo"), "Deori": ("Tibeto-Burman", "Bodo-Garo"), "Barman (Dimasa)": ("Tibeto-Burman", "Bodo-Garo"),
    "Garo": ("Tibeto-Burman", "Bodo-Garo"), "Koch": ("Tibeto-Burman", "Bodo-Garo"), "Tripuri": ("Tibeto-Burman", "Bodo-Garo"),
    "Bru": ("Tibeto-Burman", "Bodo-Garo"), "Meitei": ("Tibeto-Burman", "Meitei"),
    "Tai Khamti": ("Tai-Kadai", "Tai"), "Ahom": ("Tai-Kadai", "Tai"),
    "Khasi": ("Austroasiatic", "Khasian"), "Jaintia": ("Austroasiatic", "Khasian"),
    "Chakma": ("Indo-Aryan", "Bengali-Assamese"), "Bishnupriya Manipuri": ("Indo-Aryan", "Bengali-Assamese"),
    "Assamese": ("Indo-Aryan", "Bengali-Assamese"), "Bengali": ("Indo-Aryan", "Bengali-Assamese"),
    "Koch-Rajbongshi": ("Indo-Aryan", "Bengali-Assamese"), "Moran": ("Indo-Aryan", "Bengali-Assamese"),
}
# G18 lists several communities from different districts
G18_COORD = {"Apatani": (27.61, 93.87), "Monpa": (27.59, 91.86), "Singpho": (27.13, 95.73), "Tangsa": (27.13, 95.73),
             "Adi (Padam)": (28.30, 95.15), "Nyishi": (27.29, 93.62), "Idu Mishmi": (28.10, 95.80)}
N06_ALIAS = {"Mizo (Lushai)": "Mizo", "Mizo (various)": "Mizo", "Bru (Reang)": "Bru"}


def haversine(a, b):
    la1, lo1, la2, lo2 = map(np.radians, [a[0], a[1], b[0], b[1]])
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(h))


def mrm(Y, Xs, n, idx_i, idx_j, nperm=999):
    """OLS on pairwise vectors; p-values by permuting object labels (rows/cols jointly)."""
    X = np.column_stack([np.ones(len(Y))] + Xs)
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    r2 = 1 - np.sum((Y - X @ beta) ** 2) / np.sum((Y - Y.mean()) ** 2)
    # rebuild Y as matrix to permute
    M = np.full((n, n), np.nan); M[idx_i, idx_j] = Y; M[idx_j, idx_i] = Y
    ge = np.zeros(len(beta)); ge_r2 = 0
    for _ in range(nperm):
        p = RNG.permutation(n)
        Yp = M[p][:, p][idx_i, idx_j]
        bp = np.linalg.lstsq(X, Yp, rcond=None)[0]
        ge += np.abs(bp) >= np.abs(beta)
        ge_r2 += (1 - np.sum((Yp - X @ bp) ** 2) / np.sum((Yp - Yp.mean()) ** 2)) >= r2
    return beta, (ge + 1) / (nperm + 1), r2, (ge_r2 + 1) / (nperm + 1)


def main():
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    meta = pd.read_csv(ROOT / "data/survey_metadata.csv").set_index("source_id")
    coords = pd.read_csv(ROOT / "data/district_coords.csv")
    dc = {(r.district, r.state): (r.lat, r.lon) for r in coords.itertuples()}
    fg_coord = {}
    for sid, m in meta.iterrows():
        pts = [dc[(d.strip(), m.state)] for d in str(m.districts).split(";") if (d.strip(), m.state) in dc]
        if pts: fg_coord.setdefault(m.fieldwork_group, []).extend(pts)
    fg_coord = {k: tuple(np.mean(v, axis=0)) for k, v in fg_coord.items()}

    a = u[(u.is_primary == 1) & (u.attribution != "pooled") & (u.design == "general") & u.accepted_species.notna()
          & (u.condition != "unspecified/other")].copy()
    a["community"] = a.community.replace(N06_ALIAS)
    a["assemblage"] = a.fieldwork_group + "|" + a.community
    a = a[a.community.isin(LANG)]
    sizes = a.groupby("assemblage").accepted_species.nunique()
    keep = sizes[sizes >= 10].index            # too-small assemblages give unstable Jaccard
    a = a[a.assemblage.isin(keep)]
    sp = a.groupby("assemblage").accepted_species.apply(set)
    uses = a.groupby(["assemblage", "accepted_species"]).condition.apply(set)

    asm = pd.DataFrame({"assemblage": sp.index})
    asm["fieldwork_group"] = asm.assemblage.str.split("|").str[0]
    asm["community"] = asm.assemblage.str.split("|").str[1]
    asm["state"] = asm.fieldwork_group.map(lambda g: a[a.fieldwork_group == g].state.mode().iat[0])
    asm["lat"] = asm.apply(lambda r: G18_COORD[r.community][0] if r.fieldwork_group == "G18" else fg_coord.get(r.fieldwork_group, (np.nan,))[0], axis=1)
    asm["lon"] = asm.apply(lambda r: G18_COORD[r.community][1] if r.fieldwork_group == "G18" else fg_coord.get(r.fieldwork_group, (np.nan, np.nan))[1], axis=1)
    asm["family"] = asm.community.map(lambda c: LANG[c][0]); asm["subgroup"] = asm.community.map(lambda c: LANG[c][1])
    asm["n_species"] = asm.assemblage.map(sizes)
    asm = asm.dropna(subset=["lat"]).reset_index(drop=True)
    asm.to_csv(ROOT / "output/assemblages.csv", index=False)

    rows = []
    n = len(asm)
    for i, j in itertools.combinations(range(n), 2):
        A, B = asm.iloc[i], asm.iloc[j]
        sa, sb = sp[A.assemblage], sp[B.assemblage]
        shared = sa & sb
        cong = (np.mean([len(uses[(A.assemblage, s)] & uses[(B.assemblage, s)]) > 0 for s in shared]) if len(shared) >= 3 else np.nan)
        rows.append(dict(i=i, j=j, a=A.assemblage, b=B.assemblage, jaccard=len(shared) / len(sa | sb), n_shared=len(shared),
                         use_congruence=cong, km=haversine((A.lat, A.lon), (B.lat, B.lon)),
                         same_family=int(A.family == B.family), same_subgroup=int(A.subgroup == B.subgroup),
                         same_state=int(A.state == B.state), same_community=int(A.community == B.community)))
    pw = pd.DataFrame(rows)
    pw["log_km"] = np.log10(pw.km + 10)
    pw.to_csv(ROOT / "output/pairwise_similarity.csv", index=False)

    res = {"assemblages": n, "pairs": len(pw), "median_jaccard": round(pw.jaccard.median(), 3),
           "pairs_with_congruence": int(pw.use_congruence.notna().sum()), "median_use_congruence": round(pw.use_congruence.median(), 3)}
    for outcome in ["jaccard", "use_congruence"]:
        sub = pw.dropna(subset=[outcome])
        if outcome == "use_congruence":
            # permutation needs a full matrix; fill missing pairs with the mean so they carry no signal
            Y = pw[outcome].fillna(pw[outcome].mean()).values; sub = pw
        else:
            Y = sub[outcome].values
        Xs = [sub.log_km.values, sub.same_family.values, sub.same_subgroup.values, sub.same_state.values]
        beta, p, r2, pr2 = mrm(Y, Xs, n, sub.i.values, sub.j.values)
        res[outcome] = {"R2": round(r2, 3), "p_R2": round(pr2, 4),
                        **{f"b_{k}": round(b, 4) for k, b in zip(["intercept", "log_km", "same_family", "same_subgroup", "same_state"], beta)},
                        **{f"p_{k}": round(q, 4) for k, q in zip(["intercept", "log_km", "same_family", "same_subgroup", "same_state"], p)}}
    # same community name studied twice (independent surveys of one community): how similar?
    res["jaccard_same_community_vs_other"] = [round(pw[pw.same_community == 1].jaccard.mean(), 3), round(pw[pw.same_community == 0].jaccard.mean(), 3)]
    res["congruence_same_community_vs_other"] = [round(pw[pw.same_community == 1].use_congruence.mean(), 3), round(pw[pw.same_community == 0].use_congruence.mean(), 3)]
    (ROOT / "output/similarity_mrm.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()


def congruence_null(nperm=200):
    """Is use congruence above chance? Shuffle conditions among each assemblage's own plants (keeps its ailment profile)."""
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    asm = pd.read_csv(ROOT / "output/assemblages.csv")
    pw = pd.read_csv(ROOT / "output/pairwise_similarity.csv")
    a = u[(u.is_primary == 1) & (u.attribution != "pooled") & (u.design == "general") & u.accepted_species.notna()
          & (u.condition != "unspecified/other")].copy()
    a["community"] = a.community.replace(N06_ALIAS)
    a["assemblage"] = a.fieldwork_group + "|" + a.community
    a = a[a.assemblage.isin(set(asm.assemblage))][["assemblage", "accepted_species", "condition"]].drop_duplicates()

    def mean_cong(df):
        uses = df.groupby(["assemblage", "accepted_species"]).condition.apply(set)
        sp = df.groupby("assemblage").accepted_species.apply(set)
        vals = []
        for r in pw.itertuples():
            sh = sp[r.a] & sp[r.b]
            if len(sh) >= 3:
                vals.append(np.mean([len(uses[(r.a, s)] & uses[(r.b, s)]) > 0 for s in sh]))
        return np.mean(vals)
    obs = mean_cong(a)
    null = []
    for _ in range(nperm):
        b = a.copy()
        b["condition"] = b.groupby("assemblage").condition.transform(lambda s: RNG.permutation(s.values))
        null.append(mean_cong(b.drop_duplicates()))
    null = np.array(null)
    same = pw[pw.same_community == 1].use_congruence.dropna()
    other = pw[pw.same_community == 0].use_congruence.dropna()
    from scipy import stats
    out = {"mean_congruence_observed": round(float(obs), 3), "null_mean": round(float(null.mean()), 3),
           "null_95pct": round(float(np.percentile(null, 95)), 3), "perm_p": float((np.sum(null >= obs) + 1) / (nperm + 1)),
           "same_community_pairs": int(len(same)), "same_vs_other_mannwhitney_p": float(stats.mannwhitneyu(same, other).pvalue),
           "same_community_pairs_list": pw[pw.same_community == 1][["a", "b", "jaccard", "use_congruence"]].round(3).values.tolist()}
    res = json.loads((ROOT / "output/similarity_mrm.json").read_text()); res["congruence_null"] = out
    (ROOT / "output/similarity_mrm.json").write_text(json.dumps(res, indent=2))
    np.save(ROOT / "output/congruence_null.npy", null)
    print(json.dumps(out, indent=2))


if __name__ == "__main__" and True:
    congruence_null()
