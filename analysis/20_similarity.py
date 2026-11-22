"""Does medicinal knowledge follow geography, language, or neither?

Assemblage = one community in one independent fieldwork group (primary, explicit attribution, general-design surveys).
For every pair of assemblages:
  - species Jaccard: overlap of the plants used (reflects shared flora AND shared knowledge)
  - use congruence: among plants BOTH use, the share used for at least one common condition.
    Conditioning on shared plants removes availability from the comparison.
Predictors: great-circle distance (log km), same language family, same linguistic subgroup, same state.
Inference: multiple regression on distance matrices (MRM) with 9,999 assemblage-label permutations (QAP),
which respects the non-independence of pairwise data.

Missing use congruence (revision point 1): congruence is defined only when two assemblages share >= 3 plants.
Pairs below that threshold are NOT imputed. The congruence MRM is fitted on observed pairs only; in each permutation
the observed/missing pattern travels with the permuted labels and the model is refitted on the pairs that are
observed after permutation. Sensitivity: (a) the same model weighted by the number of shared plants,
(b) thresholds of >= 5 and >= 10 shared plants, (c) a model of missingness itself (is congruence defined?) on the
same predictors, so that any geographic structure in what can be compared is reported, (d) the old mean-filled fit
for comparison only.

Usage: .venv/bin/python analysis/20_similarity.py
Writes output/assemblages.csv, output/pairwise_similarity.csv, output/similarity_mrm.json
"""
import itertools, json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nulls import BlockCurveball, perm_p

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


N_PERM_MRM = 9999
PRED = ["intercept", "log_km", "same_family", "same_subgroup", "same_state"]


def _wls(X, Y, w):
    sw = np.sqrt(w)
    beta = np.linalg.lstsq(X * sw[:, None], Y * sw, rcond=None)[0]
    ybar = np.sum(w * Y) / np.sum(w)
    r2 = 1 - np.sum(w * (Y - X @ beta) ** 2) / np.sum(w * (Y - ybar) ** 2)
    return beta, r2


def mrm(Y, Xs, n, idx_i, idx_j, nperm=N_PERM_MRM, W=None):
    """(Weighted) OLS on pairwise vectors; p-values by permuting object labels (rows/cols jointly).

    Y may contain NaN (pair not comparable). Missing pairs are dropped, never imputed: in every permutation the
    response matrix (with its NaN pattern) is permuted and the model is refitted on the pairs observed after
    permutation, so the test conditions on the same missingness mechanism as the observed fit.
    W: optional pair weights, permuted together with Y.
    """
    X = np.column_stack([np.ones(len(Y))] + Xs)
    W = np.ones(len(Y)) if W is None else np.asarray(W, float)
    ok = ~np.isnan(Y)
    beta, r2 = _wls(X[ok], Y[ok], W[ok])
    M = np.full((n, n), np.nan); M[idx_i, idx_j] = Y; M[idx_j, idx_i] = Y
    MW = np.zeros((n, n)); MW[idx_i, idx_j] = W; MW[idx_j, idx_i] = W
    ge = np.zeros(len(beta)); ge_r2 = 0
    for _ in range(nperm):
        p = RNG.permutation(n)
        Yp = M[p][:, p][idx_i, idx_j]; Wp = MW[p][:, p][idx_i, idx_j]
        okp = ~np.isnan(Yp)
        bp, r2p = _wls(X[okp], Yp[okp], Wp[okp])
        ge += np.abs(bp) >= np.abs(beta)
        ge_r2 += r2p >= r2
    return beta, (ge + 1) / (nperm + 1), r2, (ge_r2 + 1) / (nperm + 1), int(ok.sum())


def mrm_result(Y, sub, n, W=None, nperm=N_PERM_MRM):
    Xs = [sub.log_km.values, sub.same_family.values, sub.same_subgroup.values, sub.same_state.values]
    beta, p, r2, pr2, n_obs = mrm(Y, Xs, n, sub.i.values, sub.j.values, nperm=nperm, W=W)
    return {"pairs_used": n_obs, "R2": round(r2, 3), "p_R2": round(pr2, 4),
            **{f"b_{k}": round(b, 4) for k, b in zip(PRED, beta)},
            **{f"p_{k}": round(q, 4) for k, q in zip(PRED, p)}}


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
        cong = (np.mean([len(uses[(A.assemblage, s)] & uses[(B.assemblage, s)]) > 0 for s in shared]) if len(shared) >= 1 else np.nan)
        rows.append(dict(i=i, j=j, a=A.assemblage, b=B.assemblage, jaccard=len(shared) / len(sa | sb), n_shared=len(shared),
                         use_congruence=cong, km=haversine((A.lat, A.lon), (B.lat, B.lon)),
                         same_family=int(A.family == B.family), same_subgroup=int(A.subgroup == B.subgroup),
                         same_state=int(A.state == B.state), same_community=int(A.community == B.community)))
    pw = pd.DataFrame(rows)
    pw["congruence_any"] = pw.use_congruence                       # defined with >= 1 shared plant (sensitivity only)
    pw.loc[pw.n_shared < 3, "use_congruence"] = np.nan              # main definition: >= 3 shared plants
    pw["log_km"] = np.log10(pw.km + 10)
    pw.to_csv(ROOT / "output/pairwise_similarity.csv", index=False)

    res = {"assemblages": n, "pairs": len(pw), "median_jaccard": round(pw.jaccard.median(), 3),
           "pairs_with_congruence": int(pw.use_congruence.notna().sum()), "median_use_congruence": round(pw.use_congruence.median(), 3)}
    res["jaccard"] = mrm_result(pw.jaccard.values, pw, n)
    # main congruence model: observed pairs only (>= 3 shared plants), no imputation
    res["use_congruence"] = mrm_result(pw.use_congruence.values, pw, n)
    sens = {}
    sens["weighted_by_n_shared"] = mrm_result(pw.use_congruence.values, pw, n, W=pw.n_shared.values)
    for k in (5, 10):
        sens[f"min_shared_{k}"] = mrm_result(np.where(pw.n_shared >= k, pw.use_congruence, np.nan), pw, n)
    # missingness: is congruence defined (>= 3 shared plants)? linear probability MRM with QAP
    sens["missingness_defined_ge3"] = mrm_result((pw.n_shared >= 3).astype(float).values, pw, n)
    sens["missingness_defined_ge3"]["share_defined"] = round(float((pw.n_shared >= 3).mean()), 3)
    # the original mean-filled fit, reported only to show what changed
    sens["original_mean_filled"] = mrm_result(pw.use_congruence.fillna(pw.use_congruence.mean()).values, pw, n, nperm=999)
    res["use_congruence_sensitivity"] = sens
    # same community name studied twice (independent surveys of one community): how similar?
    res["jaccard_same_community_vs_other"] = [round(pw[pw.same_community == 1].jaccard.mean(), 3), round(pw[pw.same_community == 0].jaccard.mean(), 3)]
    res["congruence_same_community_vs_other"] = [round(pw[pw.same_community == 1].use_congruence.mean(), 3), round(pw[pw.same_community == 0].use_congruence.mean(), 3)]
    (ROOT / "output/similarity_mrm.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()


def congruence_null(nperm=999):
    """Is use congruence above chance?

    shuffle   (original): conditions shuffled among each assemblage's own plant x condition rows, duplicates dropped.
              Keeps the ailment profile but not each plant's number of distinct uses.
    curveball (revision): within each assemblage the plant x condition incidence matrix is randomised by curveball
              swaps, keeping each plant's number of conditions and each condition's number of plants exactly.
    Species lists, and therefore which plants each pair shares, are fixed under both nulls.
    """
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    asm = pd.read_csv(ROOT / "output/assemblages.csv")
    pw = pd.read_csv(ROOT / "output/pairwise_similarity.csv")
    a = u[(u.is_primary == 1) & (u.attribution != "pooled") & (u.design == "general") & u.accepted_species.notna()
          & (u.condition != "unspecified/other")].copy()
    a["community"] = a.community.replace(N06_ALIAS)
    a["assemblage"] = a.fieldwork_group + "|" + a.community
    a = a[a.assemblage.isin(set(asm.assemblage))][["assemblage", "accepted_species", "condition"]].drop_duplicates()
    sp = a.groupby("assemblage").accepted_species.apply(set)
    comp = [(r.a, r.b, sorted(sp[r.a] & sp[r.b])) for r in pw.itertuples()]
    comp = [c for c in comp if len(c[2]) >= 3]

    def mean_cong(uses):
        return float(np.mean([np.mean([len(uses[(x, s)] & uses[(y, s)]) > 0 for s in sh]) for x, y, sh in comp]))

    obs_uses = a.groupby(["assemblage", "accepted_species"]).condition.apply(set).to_dict()
    obs = mean_cong(obs_uses)
    null_shuffle = []
    for _ in range(nperm):
        b = a.copy()
        b["condition"] = b.groupby("assemblage").condition.transform(lambda s: RNG.permutation(s.values))
        null_shuffle.append(mean_cong(b.drop_duplicates().groupby(["assemblage", "accepted_species"]).condition.apply(set).to_dict()))
    blocks = {}
    for (g, t), s in obs_uses.items():
        blocks.setdefault(g, {})[t] = s
    chain = BlockCurveball(blocks, RNG)
    null_cb = []
    for _ in range(nperm):
        d = {}
        for g, t, c in chain.sample():
            d.setdefault((g, t), set()).add(c)
        null_cb.append(mean_cong(d))
    null_shuffle, null_cb = np.array(null_shuffle), np.array(null_cb)
    same = pw[pw.same_community == 1].use_congruence.dropna()
    other = pw[pw.same_community == 0].use_congruence.dropna()
    from scipy import stats
    out = {"mean_congruence_observed": round(obs, 3), "n_permutations": nperm,
           "null_mean": round(float(null_shuffle.mean()), 3), "null_95pct": round(float(np.percentile(null_shuffle, 95)), 3),
           "perm_p": perm_p(null_shuffle, obs),
           "curveball_null_mean": round(float(null_cb.mean()), 3), "curveball_null_95pct": round(float(np.percentile(null_cb, 95)), 3),
           "curveball_null_max": round(float(null_cb.max()), 3), "curveball_perm_p": perm_p(null_cb, obs),
           "ratio_observed_to_curveball_null": round(obs / float(null_cb.mean()), 2),
           "same_community_pairs": int(len(same)), "same_vs_other_mannwhitney_p": float(stats.mannwhitneyu(same, other).pvalue),
           "same_community_pairs_list": pw[pw.same_community == 1][["a", "b", "jaccard", "use_congruence"]].round(3).values.tolist()}
    res = json.loads((ROOT / "output/similarity_mrm.json").read_text()); res["congruence_null"] = out
    (ROOT / "output/similarity_mrm.json").write_text(json.dumps(res, indent=2))
    np.save(ROOT / "output/congruence_null.npy", null_shuffle)
    np.save(ROOT / "output/congruence_null_curveball.npy", null_cb)
    print(json.dumps({k: v for k, v in out.items() if k != "same_community_pairs_list"}, indent=2))


if __name__ == "__main__" and True:
    congruence_null()
