"""Recurrence of plant-use claims across independently documented communities, and how it depends on survey design.

Counting unit: an independent report = distinct (fieldwork_group, community) supporting a taxon x condition.

Evidence tiers (each is a subset of the previous):
  A  all primary field reports (reviews excluded)
  B  A, explicit community attribution only (pooled multi-community / unresolved records excluded)
  C  B, general medicinal surveys only (no single-ailment, plant-group, food+medicine, selected-ailment designs),
     and the use wording verified near the species name in the source text

Also computed:
  - agreement ladder: species -> species+condition -> species+condition+same plant part
  - leave-one-fieldwork-group-out minimum (does recurrence rest on one survey?)
  - permutation nulls, 999 draws each, counting how many taxon x condition pairs reach >= 3 reports by chance:
      shuffle    : the original null, conditions shuffled among a survey's own units, then duplicates dropped
                   (keeps each survey's species list but NOT the number of distinct uses per plant)
      curveball  : margin-preserving null. Within every report (community x campaign) the plant x condition
                   incidence matrix is randomised by curveball swaps, which keeps each plant's number of conditions
                   and each condition's number of plants in that report exactly (Strona et al. 2014)
  - replication units (revision): a pair's support counted as distinct community x campaign reports (main),
    distinct communities (repeat surveys of one community count once), and distinct fieldwork campaigns
    (a multi-community campaign counts once: the conservative definition)
  - design effect: how much single-ailment / plant-group surveys add to each condition

Usage: .venv/bin/python analysis/15_recurrence.py
Writes output/recurrence_pairs.csv, output/recurrence_summary.json, output/figures/*.png
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from nulls import BlockCurveball, perm_p

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "output/figures"; FIG.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(2026)
MIN_REC = 3          # "recurrent" = at least 3 independent reports (fixed before looking at results)
N_PERM = 999
# spelling variants of one community, merged for the distinct-community count
COMMUNITY_ALIAS = {"Mizo (Lushai)": "Mizo", "Mizo (various)": "Mizo", "Bru (Reang)": "Bru"}


def tiers(u):
    A = u[(u.is_primary == 1) & (u.condition != "unspecified/other")]
    B = A[A.attribution != "pooled"]
    C = B[(B.design == "general") & (B.use_found_in_source)]
    return {"A": A, "B": B, "C": C}


def count_reports(df, unit="report"):
    """Support per taxon x condition. unit: report (campaign x community), community, or campaign."""
    if unit == "report":
        key = df.fieldwork_group + "|" + df.community
    elif unit == "community":
        key = df.community.replace(COMMUNITY_ALIAS)
    else:
        key = df.fieldwork_group
    return df.assign(key=key).groupby(["taxon", "condition"]).key.nunique()


def null_curveball(units, n_perm=N_PERM, units_to_count=("report", "campaign")):
    """Margin-preserving null: curveball swaps within each report's plant x condition matrix."""
    base = units[["fieldwork_group", "community", "taxon", "condition"]].drop_duplicates()
    blocks = {}
    for (g, c, t), cond in base.groupby(["fieldwork_group", "community", "taxon"]).condition:
        blocks.setdefault((g, c), {})[t] = set(cond)
    chain = BlockCurveball(blocks, RNG)
    out = {k: [] for k in units_to_count}
    for _ in range(n_perm):
        sh = pd.DataFrame([(b[0], b[1], t, c) for b, t, c in chain.sample()],
                          columns=["fieldwork_group", "community", "taxon", "condition"])
        for k in units_to_count:
            out[k].append(int((count_reports(sh, k) >= MIN_REC).sum()))
    return {k: np.array(v) for k, v in out.items()}


def null_recurrent(units, n_perm=N_PERM):
    """Original null: shuffle condition labels among each fieldwork group's own units, then drop duplicates."""
    out = []
    base = units[["fieldwork_group", "community", "taxon", "condition"]].reset_index(drop=True)
    for _ in range(n_perm):
        sh = base.copy()
        sh["condition"] = sh.groupby("fieldwork_group").condition.transform(lambda s: RNG.permutation(s.values))
        sh = sh.drop_duplicates()
        out.append(int((count_reports(sh) >= MIN_REC).sum()))
    return np.array(out)


def main():
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    T = tiers(u)
    counts = {k: count_reports(v) for k, v in T.items()}
    pairs = pd.concat(counts, axis=1).fillna(0).astype(int).reset_index()
    # replication units for tier A (revision point 2)
    repl = pd.concat({"A_communities": count_reports(T["A"], "community"),
                      "A_campaigns": count_reports(T["A"], "campaign"),
                      "C_campaigns": count_reports(T["C"], "campaign")}, axis=1).fillna(0).astype(int).reset_index()
    pairs = pairs.merge(repl, on=["taxon", "condition"], how="left").fillna(0)

    # species-level recurrence (any medicinal use), for the agreement ladder
    A = T["A"].assign(report=lambda x: x.fieldwork_group + "|" + x.community)
    sp_level = A.groupby("taxon").report.nunique().rename("species_any_use")
    pairs = pairs.merge(sp_level, on="taxon", how="left")
    # same condition AND same plant part: largest number of reports that share one part
    ex = A.assign(part=A.parts.str.split(";")).explode("part")
    ex = ex[ex.part != "unknown"]
    part_top = ex.groupby(["taxon", "condition", "part"]).report.nunique().groupby(["taxon", "condition"]).max()
    pairs = pairs.merge(part_top.rename("same_part"), on=["taxon", "condition"], how="left").fillna({"same_part": 0})
    pairs["part_reported"] = pairs.apply(lambda r: ex[(ex.taxon == r.taxon) & (ex.condition == r.condition)].report.nunique()
                                         if r.A >= MIN_REC else np.nan, axis=1)

    # leave-one-fieldwork-group-out minimum for recurrent pairs
    def loo(r):
        sub = A[(A.taxon == r.taxon) & (A.condition == r.condition)]
        return min(sub[sub.fieldwork_group != g].report.nunique() for g in sub.fieldwork_group.unique())
    rec = pairs.A >= MIN_REC
    pairs.loc[rec, "A_leave_one_out_min"] = pairs[rec].apply(loo, axis=1)
    # states and communities behind each recurrent pair
    pairs.loc[rec, "states"] = pairs[rec].apply(lambda r: ";".join(sorted(set(A[(A.taxon == r.taxon) & (A.condition == r.condition)].state))), axis=1)
    pairs.loc[rec, "communities"] = pairs[rec].apply(lambda r: ";".join(sorted(set(A[(A.taxon == r.taxon) & (A.condition == r.condition)].community))), axis=1)
    pairs = pairs.sort_values(["A", "C"], ascending=False)
    pairs.to_csv(ROOT / "output/recurrence_pairs.csv", index=False)

    # permutation nulls (tier A and tier C)
    nullA, nullC = null_recurrent(T["A"]), null_recurrent(T["C"])
    cbA, cbC = null_curveball(T["A"]), null_curveball(T["C"])
    obsA, obsC = int((pairs.A >= MIN_REC).sum()), int((pairs.C >= MIN_REC).sum())
    obsA_camp, obsC_camp = int((pairs.A_campaigns >= MIN_REC).sum()), int((pairs.C_campaigns >= MIN_REC).sum())
    np.savez(ROOT / "output/recurrence_nulls.npz", shuffle_A=nullA, shuffle_C=nullC, curveball_A=cbA["report"],
             curveball_C=cbC["report"], curveball_A_campaign=cbA["campaign"], curveball_C_campaign=cbC["campaign"])
    recA = pairs[pairs.A >= MIN_REC]

    # design effect per condition: share of tier-A reports coming from non-general designs
    des = T["A"].assign(nongen=T["A"].design != "general").groupby("condition").nongen.mean().sort_values(ascending=False)

    summ = {
        "units_total": len(u), "units_tierA": len(T["A"]), "units_tierB": len(T["B"]), "units_tierC": len(T["C"]),
        "pairs_recurrent_A": obsA, "pairs_recurrent_B": int((pairs.B >= MIN_REC).sum()), "pairs_recurrent_C": obsC,
        "null_recurrent_A_mean": float(nullA.mean()), "null_recurrent_A_95pct": float(np.percentile(nullA, 95)),
        "perm_p_A": perm_p(nullA, obsA),
        "null_recurrent_C_mean": float(nullC.mean()), "null_recurrent_C_95pct": float(np.percentile(nullC, 95)),
        "perm_p_C": perm_p(nullC, obsC),
        "n_permutations": N_PERM,
        "curveball_null": {
            "A_report": {"observed": obsA, "null_mean": float(cbA["report"].mean()), "null_95pct": float(np.percentile(cbA["report"], 95)),
                         "null_max": int(cbA["report"].max()), "perm_p": perm_p(cbA["report"], obsA)},
            "C_report": {"observed": obsC, "null_mean": float(cbC["report"].mean()), "null_95pct": float(np.percentile(cbC["report"], 95)),
                         "null_max": int(cbC["report"].max()), "perm_p": perm_p(cbC["report"], obsC)},
            "A_campaign": {"observed": obsA_camp, "null_mean": float(cbA["campaign"].mean()), "null_95pct": float(np.percentile(cbA["campaign"], 95)),
                           "null_max": int(cbA["campaign"].max()), "perm_p": perm_p(cbA["campaign"], obsA_camp)},
            "C_campaign": {"observed": obsC_camp, "null_mean": float(cbC["campaign"].mean()), "null_95pct": float(np.percentile(cbC["campaign"], 95)),
                           "null_max": int(cbC["campaign"].max()), "perm_p": perm_p(cbC["campaign"], obsC_camp)},
        },
        "replication_units": {
            "recurrent_A_by_report": obsA,
            "recurrent_A_by_distinct_community": int((pairs.A_communities >= MIN_REC).sum()),
            "recurrent_A_by_distinct_campaign": obsA_camp,
            "recurrent_A_by_report_AND_campaign": int(((pairs.A >= MIN_REC) & (pairs.A_campaigns >= MIN_REC)).sum()),
            "recurrent_A_with_fewer_than_3_campaigns": int((recA.A_campaigns < MIN_REC).sum()),
            "recurrent_A_with_fewer_than_3_communities": int((recA.A_communities < MIN_REC).sum()),
            "recurrent_C_by_report": obsC, "recurrent_C_by_distinct_campaign": obsC_camp,
        },
        "recurrent_A_that_survive_C": int(((pairs.A >= MIN_REC) & (pairs.C >= MIN_REC)).sum()),
        "recurrent_A_that_survive_leave_one_out": int((pairs.A_leave_one_out_min >= MIN_REC).sum()),
        "species_recurrent_any_use": int((sp_level >= MIN_REC).sum()),
        "design_effect_top_conditions": des.head(8).round(3).to_dict(),
    }
    (ROOT / "output/recurrence_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))
    print(pairs.head(25)[["taxon", "condition", "species_any_use", "A", "B", "C", "same_part", "A_leave_one_out_min", "states"]].to_string(index=False))

    # ---- figures ----
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.hist(nullA, bins=25, color="#9aa5b1", label="null (conditions shuffled within surveys)")
    ax.axvline(obsA, color="#c0392b", lw=2, label=f"observed = {obsA}")
    ax.set_xlabel(f"taxon x condition pairs with >= {MIN_REC} independent reports (tier A)")
    ax.set_ylabel("permutations"); ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "fig_null_recurrence.png", dpi=200); plt.close(fig)

    ladder = pd.DataFrame({
        "species (any use)": [(sp_level >= k).sum() for k in range(2, 9)],
        "species + condition": [(pairs.A >= k).sum() for k in range(2, 9)],
        "+ same plant part": [(pairs.same_part >= k).sum() for k in range(2, 9)],
        "tier C (explicit, general, verified)": [(pairs.C >= k).sum() for k in range(2, 9)],
    }, index=range(2, 9))
    ax = ladder.plot(marker="o", figsize=(6.5, 3.8), logy=True)
    ax.set_xlabel("minimum number of independent community reports"); ax.set_ylabel("number of taxa / pairs (log)")
    ax.legend(frameon=False, fontsize=8); plt.tight_layout(); plt.savefig(FIG / "fig_agreement_ladder.png", dpi=200); plt.close()
    ladder.to_csv(ROOT / "output/agreement_ladder.csv")


if __name__ == "__main__":
    main()
