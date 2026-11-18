"""Publication figures (PNG 300 dpi + PDF) in output/figures/pub/.

Fig 1  Study map: assemblages over the seven states, coloured by language family, sized by species documented
Fig 2  Evidence funnel + agreement ladder: how many claims survive each evidence rule
Fig 3  Agreement beyond chance: recurrent pairs and use congruence vs permutation nulls
Fig 4  'Popular is not agreed': species reach vs share agreeing on one use
Fig 5  Consensus network of tier-C recurrent plant-use pairs (modules)
Fig 6  Survey design and robustness: design effect by condition; pilot pairs under tiers
Fig 7  Completeness: accumulation curves and Chao2 by state
Fig S1 Geography and language do not explain use congruence (pairwise plots)
Fig S2 Availability proxy (GBIF) vs reach

Map boundaries: Natural Earth 1:10m admin-1, schematic only. Replace with Survey of India boundaries for publication in India.
Usage: .venv/bin/python analysis/22_figures.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "output"; F = O / "figures/pub"; F.mkdir(parents=True, exist_ok=True)
OKABE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
FAM_COL = {"Tibeto-Burman": "#0072B2", "Austroasiatic": "#009E73", "Tai-Kadai": "#E69F00", "Indo-Aryan": "#CC79A7"}
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7, "axes.spines.top": False,
                     "axes.spines.right": False, "font.family": "DejaVu Sans", "savefig.bbox": "tight"})


def save(fig, name):
    fig.savefig(F / f"{name}.png", dpi=300); fig.savefig(F / f"{name}.pdf"); plt.close(fig)


def panel(ax, letter):
    ax.text(-0.12, 1.04, letter, transform=ax.transAxes, fontweight="bold", fontsize=10, va="bottom")


def fig1_map():
    import geopandas as gpd
    st = gpd.read_file(ROOT / "data/ne_states.geojson"); ctx = gpd.read_file(ROOT / "data/ne_context.geojson")
    asm = pd.read_csv(O / "output_placeholder.csv") if False else pd.read_csv(O / "assemblages.csv")
    u = pd.read_csv(O / "evidence_units.csv")
    fig, ax = plt.subplots(figsize=(7, 6))
    ctx.plot(ax=ax, color="#f2f2f2", edgecolor="#d9d9d9", lw=0.3)
    st.plot(ax=ax, color="#fbf7ef", edgecolor="#7f7f7f", lw=0.7)
    for r in st.itertuples():
        c = r.geometry.representative_point(); ax.text(c.x, c.y, r.name, fontsize=6.5, color="#7f7f7f", ha="center", style="italic")
    jit = np.random.default_rng(3)
    for fam, col in FAM_COL.items():
        s = asm[asm.family == fam]
        ax.scatter(s.lon + jit.normal(0, 0.06, len(s)), s.lat + jit.normal(0, 0.06, len(s)), s=s.n_species * 1.6,
                   color=col, alpha=0.75, edgecolor="white", lw=0.6, label=f"{fam} ({len(s)})", zorder=3)
    for r in asm.itertuples():
        ax.text(r.lon + 0.08, r.lat + 0.05, r.community.replace(" Naga", ""), fontsize=5, zorder=4)
    ax.set_xlim(89.5, 97.5); ax.set_ylim(21.8, 29.6); ax.set_aspect("equal")
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
    l1 = ax.legend(title="Language family (assemblages)", loc="lower right", frameon=True, framealpha=0.9)
    ax.add_artist(l1)
    hs = [plt.scatter([], [], s=n * 1.6, color="#999999", alpha=0.6) for n in (20, 60, 120)]
    ax.legend(hs, ["20", "60", "120"], title="Species documented", loc="upper left", frameon=True, framealpha=0.9, labelspacing=1.2)
    ax.set_title("Independent community-surveys included in the synthesis (general medicinal surveys)")
    ax.text(0.01, 0.005, "Boundaries schematic (Natural Earth); not authenticated by the Survey of India.", transform=ax.transAxes, fontsize=5, color="#7f7f7f")
    save(fig, "Fig1_study_map")


def fig2_funnel_ladder():
    s = json.loads((O / "recurrence_summary.json").read_text())
    d = pd.read_excel(O / "NE_combined_v3.xlsx", "Data")
    lad = pd.read_csv(O / "agreement_ladder.csv", index_col=0)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    steps = [("Published records", len(d)), ("Independent evidence units", s["units_total"]), ("Tier A: primary reports", s["units_tierA"]),
             ("Tier B: explicit attribution", s["units_tierB"]), ("Tier C: general survey, wording verified", s["units_tierC"])]
    for i, (lab, v) in enumerate(steps):
        w = v / steps[0][1]
        ax.barh(-i, w, left=(1 - w) / 2, color=OKABE[0], alpha=0.25 + 0.15 * i, height=0.75)
        ax.text(0.5, -i, f"{lab}\n{v:,}", ha="center", va="center", fontsize=6.8)
    rec = [("Recurrent pairs (≥3 reports), tier A", s["pairs_recurrent_A"]), ("… tier C", s["pairs_recurrent_C"]),
           ("… robust to dropping any one survey", s["recurrent_A_that_survive_leave_one_out"]), ("Expected by chance (tier A)", round(s["null_recurrent_A_mean"]))]
    for k, (lab, v) in enumerate(rec):
        ax.text(0.5, -5.2 - 0.55 * k, f"{lab}: {v}", ha="center", fontsize=6.8, color=OKABE[5] if "chance" in lab else "black")
    ax.set_xlim(0, 1); ax.set_ylim(-7.4, 0.6); ax.axis("off"); panel(ax, "a")
    ax = axes[1]
    marks = ["o", "s", "^", "D"]
    for (col, m, c) in zip(lad.columns, marks, [OKABE[7], OKABE[0], OKABE[2], OKABE[5]]):
        ax.plot(lad.index, lad[col], marker=m, ms=3.5, color=c, label=col)
    ax.set_yscale("log"); ax.set_xlabel("Minimum independent community reports"); ax.set_ylabel("Species or plant–use pairs")
    ax.legend(frameon=False); ax.set_title("Agreement ladder"); panel(ax, "b")
    save(fig, "Fig2_evidence_funnel_ladder")


def fig3_null():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rc", ROOT / "analysis/15_recurrence.py"); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
    u = pd.read_csv(O / "evidence_units.csv"); T = rc.tiers(u)
    nA = rc.null_recurrent(T["A"], 300); nC = rc.null_recurrent(T["C"], 300)
    s = json.loads((O / "recurrence_summary.json").read_text())
    cn = np.load(O / "congruence_null.npy"); sim = json.loads((O / "similarity_mrm.json").read_text())["congruence_null"]
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.5))
    for ax, null, obs, lab, L in [(axes[0], nA, s["pairs_recurrent_A"], "Recurrent plant–use pairs\n(tier A)", "a"),
                                   (axes[1], nC, s["pairs_recurrent_C"], "Recurrent plant–use pairs\n(tier C)", "b"),
                                   (axes[2], cn, sim["mean_congruence_observed"], "Use congruence on shared plants", "c")]:
        null = np.asarray(null, dtype=float); null = null[~np.isnan(null)]
        bins = np.arange(null.min() - 0.5, null.max() + 1.5, 1) if L != "c" else 20
        ax.hist(null, bins=bins, color="#9e9e9e", edgecolor="white", lw=0.3)
        ax.axvline(obs, color=OKABE[5], lw=2)
        ax.text(obs, ax.get_ylim()[1] * 0.92, " observed", color=OKABE[5], fontsize=7, va="top")
        ax.set_xlabel(lab); ax.set_ylabel("Permutations" if L == "a" else ""); panel(ax, L)
        ax.set_xlim(min(null.min(), obs) * 0.9, max(null.max(), obs) * 1.08)
    fig.suptitle("Agreement exceeds what each survey's own ailment profile produces by chance", y=1.04, fontsize=9)
    save(fig, "Fig3_agreement_vs_null")


def fig4_popular_vs_agreed():
    from adjustText import adjust_text
    u = pd.read_csv(O / "evidence_units.csv")
    A = u[(u.is_primary == 1) & (u.condition != "unspecified/other") & u.accepted_species.notna()].assign(rep=lambda x: x.fieldwork_group + "|" + x.community)
    reach = A.groupby("accepted_species").rep.nunique()
    pair = A.groupby(["accepted_species", "condition"]).rep.nunique()
    best = pair.groupby("accepted_species").max(); bestc = pair.groupby("accepted_species").idxmax().map(lambda t: t[1])
    ncond = A.groupby("accepted_species").condition.nunique()
    df = pd.DataFrame({"reach": reach, "best": best, "share": best / reach, "ncond": ncond, "bestc": bestc})
    df = df[df.reach >= 5]
    sig = pd.read_csv(O / "use_specificity.csv"); sig = sig[(sig.q_bh < 0.05) & (sig.pair_reports >= 3)]
    df["specific"] = df.index.isin(sig.accepted_species)
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    ax.axhspan(0.5, 1.02, color=OKABE[2], alpha=0.06); ax.axhspan(0, 0.3, color=OKABE[5], alpha=0.05)
    sc = ax.scatter(df.reach, df.share, s=df.ncond * 6, c=np.where(df.specific, OKABE[0], "#9e9e9e"), alpha=0.7, edgecolor="white", lw=0.5)
    texts = []
    lab = pd.concat([df.nlargest(10, "reach"), df[(df.share >= 0.6) & (df.reach >= 8)]]).drop_duplicates()
    for n, r in lab.iterrows():
        texts.append(ax.text(r.reach, r.share, f"{n}\n({r.bestc})", fontsize=5.5, style="italic"))
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="#9e9e9e", lw=0.4))
    ax.set_xlabel("Reach: independent community reports (any medicinal use)")
    ax.set_ylabel("Share of reports agreeing on the single most-cited use")
    ax.text(0.99, 0.97, "convergent: communities agree on a use", transform=ax.transAxes, ha="right", fontsize=6.5, color=OKABE[2])
    ax.text(0.99, 0.03, "versatile: popular plant, many different uses", transform=ax.transAxes, ha="right", fontsize=6.5, color=OKABE[5])
    leg = [Line2D([], [], marker="o", ls="", color=OKABE[0], label="has a use converging beyond popularity (q < 0.05)"),
           Line2D([], [], marker="o", ls="", color="#9e9e9e", label="no significant convergent use")]
    l1 = ax.legend(handles=leg, loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False); ax.add_artist(l1)
    hs = [plt.scatter([], [], s=k * 6, color="#cccccc") for k in (5, 15, 30)]
    ax.legend(hs, ["5", "15", "30"], title="distinct conditions", loc="upper left", bbox_to_anchor=(1.01, 0.75), frameon=False, labelspacing=1.4)
    ax.set_ylim(0, 1.02)
    save(fig, "Fig4_popular_vs_agreed")


def fig5_network():
    e = pd.read_csv(O / "consensus_network_edges.csv"); nodes = pd.read_csv(O / "consensus_network_nodes.csv").set_index("node")
    pal = plt.get_cmap("tab10")
    # order modules by size; within a module conditions by degree, plants by strength
    order = nodes.groupby("module").size().sort_values(ascending=False).index.tolist()
    conds, plants = [], []
    for m in order:
        sub = nodes[nodes.module == m]
        conds += sub[sub.kind == "condition"].sort_values("degree", ascending=False).index.tolist()
        plants += sub[sub.kind == "taxon"].sort_values("strength", ascending=False).index.tolist()
    def ring(names, r, gap=0.0):
        th = np.linspace(0, 2 * np.pi, len(names), endpoint=False) + np.pi / 2
        return {n: (r * np.cos(t), r * np.sin(t), t) for n, t in zip(names, th)}
    pc, pp = ring(conds, 0.62), ring(plants, 1.0)
    fig, ax = plt.subplots(figsize=(7.4, 7.4))
    for r in e.itertuples():
        x0, y0, _ = pc[r.condition]; x1, y1, _ = pp[r.taxon]
        col = pal(nodes.loc[r.taxon].module % 10)
        # quadratic curve bending toward the centre
        t = np.linspace(0, 1, 30); cx, cy = (x0 + x1) * 0.35, (y0 + y1) * 0.35
        ax.plot((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1,
                color=col, alpha=0.35 + 0.05 * min(r.C, 8), lw=0.4 + 0.22 * r.C, zorder=1)
    for n, (x, y, t) in pc.items():
        k = nodes.loc[n]
        ax.scatter(x, y, s=30 + 22 * k.degree, marker="s", color="white", edgecolor=pal(k.module % 10), lw=1.8, zorder=3)
        deg = np.degrees(t); flip = 90 < (deg % 360) < 270
        ax.text(x * 0.93, y * 0.93, n, fontsize=6.0, fontweight="bold", rotation=deg + (180 if flip else 0),
                ha="left" if flip else "right", va="center", rotation_mode="anchor", zorder=4)
    for n, (x, y, t) in pp.items():
        k = nodes.loc[n]
        ax.scatter(x, y, s=8 + 7 * k.strength, color=pal(k.module % 10), alpha=0.9, edgecolor="white", lw=0.4, zorder=3)
        deg = np.degrees(t); flip = 90 < (deg % 360) < 270
        ax.text(x * 1.04, y * 1.04, n, fontsize=5.4, style="italic", rotation=deg + (180 if flip else 0),
                ha="right" if flip else "left", va="center", rotation_mode="anchor")
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.55, 1.55); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Consensus network: plant–use pairs with ≥3 independent community reports (strictest tier)\n"
                 "inner ring = conditions, outer ring = plants; colour = network module; line width = reports", fontsize=8)
    save(fig, "Fig5_consensus_network")


def fig6_design_pilot():
    u = pd.read_csv(O / "evidence_units.csv")
    A = u[(u.is_primary == 1) & (u.condition != "unspecified/other")]
    des = A.assign(single=A.design.isin(["single_ailment", "selected_ailments"]), group=A.design.isin(["plant_group", "food_and_medicine"]))
    t = des.groupby("condition").agg(n=("design", "size"), single=("single", "mean"), group=("group", "mean"))
    t = t[t.n >= 40].sort_values("single", ascending=True).tail(16)
    pilot = pd.read_excel(O / "pilot_trace.xlsx", "Pilot_pairs").iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.8), gridspec_kw={"width_ratios": [1, 1.1], "wspace": 1.05})
    ax = axes[0]
    ax.barh(t.index, t.single, color=OKABE[5], label="single/selected-ailment surveys")
    ax.barh(t.index, t.group, left=t.single, color=OKABE[1], label="plant-group / food+medicine surveys")
    ax.set_xlabel("Share of reports from theme-restricted surveys"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.16), fontsize=6.5); panel(ax, "a")
    ax.tick_params(axis="y", labelsize=6.5)
    ax = axes[1]; y = np.arange(len(pilot))
    for col, off, c, lab in [("A", 0.3, OKABE[7], "A all primary"), ("B", 0.1, OKABE[0], "B explicit attribution"),
                             ("C", -0.1, OKABE[2], "C + general, verified"), ("A_leave_one_out_min", -0.3, OKABE[1], "A, worst leave-one-out")]:
        ax.barh(y + off, pilot[col].fillna(0), height=0.19, color=c, label=lab)
    ax.set_yticks(y); ax.set_yticklabels([f"{t.replace(' [unresolved]', '*')} – {c}" for t, c in zip(pilot.taxon, pilot.condition)], fontsize=6)
    ax.set_xlabel("Independent community reports"); ax.legend(frameon=False, fontsize=6, loc="lower right"); panel(ax, "b")
    ax.set_title("Pilot pairs (selected by a rule fixed in advance)", fontsize=8)
    save(fig, "Fig6_design_effect_pilot")


def fig7_completeness():
    cur = pd.read_csv(O / "accumulation_curves.csv"); c = json.loads((O / "completeness.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3), gridspec_kw={"wspace": 0.55})
    ax = axes[0]
    for what, col, lab in [("taxa", OKABE[0], "taxa"), ("taxon_condition_pairs", OKABE[5], "plant–use pairs")]:
        s = cur[cur.what == what]
        ax.plot(s.units, s["mean"], color=col, label=f"{lab}: Chao2 ≈ {c[what]['chao2']:,.0f} ({c[what]['completeness']:.0%} documented)")
        ax.fill_between(s.units, s.lo, s.hi, color=col, alpha=0.2)
    ax.set_xlabel("Independent community-surveys (random order)"); ax.set_ylabel("Cumulative count"); ax.legend(frameon=False, fontsize=6.2, loc="upper left"); panel(ax, "a")
    ax = axes[1]
    st = pd.DataFrame(c["taxa_by_state"]).T.sort_values("chao2")
    y = np.arange(len(st))
    ax.hlines(y, st.ci_low, st.ci_high, color="#9e9e9e"); ax.scatter(st.chao2, y, color=OKABE[0], zorder=3, label="Chao2 estimate (95% CI)")
    ax.scatter(st.observed, y, color=OKABE[5], marker="|", s=80, zorder=3, label="documented")
    for i, r in enumerate(st.itertuples()): ax.text(r.ci_high, i, f"  {r.completeness:.0%}  (n={int(r.units)})", va="center", fontsize=6)
    ax.set_yticks(y); ax.set_yticklabels(st.index); ax.set_xlabel("Medicinal taxa"); ax.legend(frameon=False, fontsize=6, loc="lower right"); panel(ax, "b")
    save(fig, "Fig7_completeness")


def figS1_geo():
    pw = pd.read_csv(O / "pairwise_similarity.csv"); r = json.loads((O / "similarity_mrm.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for ax, col, lab, L in [(axes[0], "jaccard", "Plant overlap (Jaccard)", "a"), (axes[1], "use_congruence", "Use congruence on shared plants", "b")]:
        s = pw.dropna(subset=[col])
        c = np.where(s.same_family == 1, OKABE[0], OKABE[1])
        ax.scatter(s.km, s[col], s=6, c=c, alpha=0.45, edgecolor="none")
        bins = pd.cut(s.km, [0, 100, 200, 300, 400, 500, 700, 1000])
        m = s.groupby(bins, observed=True)[col].median()
        ax.plot([b.mid for b in m.index], m.values, color="black", lw=1.2, marker="o", ms=3)
        st = r[col]; ax.set_title(f"MRM R² = {st['R2']:.3f}; distance p = {st['p_log_km']:.2f}; same family p = {st['p_same_family']:.2f}", fontsize=7)
        ax.set_xlabel("Distance between surveys (km)"); ax.set_ylabel(lab); panel(ax, L)
    axes[1].legend(handles=[Line2D([], [], marker="o", ls="", color=OKABE[0], label="same language family"),
                            Line2D([], [], marker="o", ls="", color=OKABE[1], label="different family")], frameon=False)
    save(fig, "FigS1_geography_language")


def figS2_avail():
    sp = pd.read_csv(O / "availability_species.csv"); a = json.loads((O / "availability_summary.json").read_text())
    fig, ax = plt.subplots(figsize=(4.2, 3))
    ax.scatter(sp.log_occ, sp.reports, s=6, alpha=0.4, color=OKABE[0])
    ax.set_xlabel("log10(GBIF georeferenced records in region + 1)"); ax.set_ylabel("Independent community reports")
    ax.set_title(f"Spearman ρ = {a['spearman_rho_reports_vs_log_occurrences']:.2f}; {a['species_with_zero_ne_gbif_records']} of {a['species_tested']} taxa have no record", fontsize=7)
    save(fig, "FigS2_availability_gbif")


if __name__ == "__main__":
    for f in [fig1_map, fig2_funnel_ladder, fig3_null, fig4_popular_vs_agreed, fig5_network, fig6_design_pilot, fig7_completeness, figS1_geo, figS2_avail]:
        f(); print("done", f.__name__)
