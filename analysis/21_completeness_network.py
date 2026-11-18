"""How complete is the documented pharmacopoeia, and how are recurrent uses structured?

1. Completeness: incidence-based accumulation over independent assemblages (fieldwork group x community, tier A),
   Chao2 estimator with bias correction and 95% log-normal CI (Chao 1987; Chao et al. 2009), for taxa and for
   taxon x condition pairs. Per state as well.
2. Consensus network: bipartite graph of taxa and conditions for tier-C recurrent pairs (>= 3 independent reports),
   with modules (greedy modularity) to show which plants form shared therapeutic clusters.

Usage: .venv/bin/python analysis/21_completeness_network.py
Writes output/completeness.json, output/accumulation_curves.csv, output/consensus_network_edges.csv,
       output/consensus_network_nodes.csv
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(2026)


def chao2(inc):
    """inc: boolean matrix sampling units x items."""
    m = inc.shape[0]
    q = inc.sum(axis=0)
    s_obs = int((q > 0).sum()); q1 = int((q == 1).sum()); q2 = int((q == 2).sum())
    k = (m - 1) / m
    est = s_obs + k * q1 * (q1 - 1) / (2 * (q2 + 1))            # bias-corrected
    var_f = max(est - s_obs, 1e-9)
    var = k * q1 * (q1 - 1) / (2 * (q2 + 1)) + k ** 2 * q1 * (2 * q1 - 1) ** 2 / (4 * (q2 + 1) ** 2) + k ** 2 * q1 ** 2 * q2 * (q1 - 1) ** 2 / (4 * (q2 + 1) ** 4)
    c = np.exp(1.96 * np.sqrt(np.log(1 + var / var_f ** 2)))
    return dict(units=m, observed=s_obs, uniques=q1, duplicates=q2, chao2=round(est, 1),
                ci_low=round(s_obs + var_f / c, 1), ci_high=round(s_obs + var_f * c, 1),
                completeness=round(s_obs / est, 3))


def accumulation(inc, nperm=200):
    m = inc.shape[0]; curves = np.zeros((nperm, m))
    for p in range(nperm):
        order = RNG.permutation(m)
        curves[p] = (np.cumsum(inc[order], axis=0) > 0).sum(axis=1)
    return curves.mean(0), np.percentile(curves, 2.5, 0), np.percentile(curves, 97.5, 0)


def main():
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    A = u[(u.is_primary == 1) & (u.condition != "unspecified/other")].assign(unit=lambda x: x.fieldwork_group + "|" + x.community)
    out, curves = {}, []
    for label, col in [("taxa", "taxon"), ("taxon_condition_pairs", None)]:
        df = A.assign(item=A.taxon if col else A.taxon + " | " + A.condition)
        inc = pd.crosstab(df.unit, df.item).values > 0
        out[label] = chao2(inc)
        mean, lo, hi = accumulation(inc)
        curves.append(pd.DataFrame({"what": label, "units": np.arange(1, len(mean) + 1), "mean": mean, "lo": lo, "hi": hi}))
    out["taxa_by_state"] = {}
    for st, df in A.groupby("state"):
        inc = pd.crosstab(df.unit, df.taxon).values > 0
        if inc.shape[0] >= 3:
            out["taxa_by_state"][st] = chao2(inc)
    pd.concat(curves).to_csv(ROOT / "output/accumulation_curves.csv", index=False)

    pairs = pd.read_csv(ROOT / "output/recurrence_pairs.csv")
    rec = pairs[(pairs.C >= 3) & ~pairs.taxon.str.contains("unresolved")]
    G = nx.Graph()
    for r in rec.itertuples():
        G.add_node(r.taxon, kind="taxon"); G.add_node(r.condition, kind="condition")
        G.add_edge(r.taxon, r.condition, weight=int(r.C))
    comms = nx.algorithms.community.greedy_modularity_communities(G, weight="weight")
    mod = {n: i for i, c in enumerate(comms) for n in c}
    nodes = pd.DataFrame([dict(node=n, kind=d["kind"], degree=G.degree(n), strength=G.degree(n, weight="weight"), module=mod[n])
                          for n, d in G.nodes(data=True)])
    nodes.to_csv(ROOT / "output/consensus_network_nodes.csv", index=False)
    rec[["taxon", "condition", "C", "A"]].to_csv(ROOT / "output/consensus_network_edges.csv", index=False)
    out["network"] = {"taxa": int((nodes.kind == "taxon").sum()), "conditions": int((nodes.kind == "condition").sum()),
                      "edges": G.number_of_edges(), "modules": len(comms),
                      "modularity": round(nx.algorithms.community.modularity(G, comms, weight="weight"), 3),
                      "multi_use_taxa": nodes[(nodes.kind == "taxon") & (nodes.degree >= 2)].sort_values("degree", ascending=False).node.tolist()[:12],
                      "conditions_by_number_of_taxa": nodes[nodes.kind == "condition"].sort_values("degree", ascending=False)[["node", "degree"]].head(12).values.tolist()}
    (ROOT / "output/completeness.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
