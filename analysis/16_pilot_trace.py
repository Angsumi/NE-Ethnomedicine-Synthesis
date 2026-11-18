"""Pilot: trace 10 plant-use pairs back to the original source tables.

Selection rule (fixed in docs/PROTOCOL.md before inspecting the pilot output):
  - the 5 pairs with the most independent tier-A reports, and
  - 5 pairs drawn at random (seed 2026) from pairs with 3-5 tier-A reports.

For every supporting unit we export the original use wording from the record AND a verbatim snippet of the
source text around the species name, with blank columns for two independent readers (reader1_*, reader2_*)
to confirm: table row found, identification, plant part, community attribution, same specific use.

Usage: .venv/bin/python analysis/16_pilot_trace.py
Writes output/pilot_trace.xlsx, output/figures/fig_pilot_pairs.png
"""
import importlib.util, re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ev", ROOT / "analysis/13_evidence_units.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)


def main():
    pairs = pd.read_csv(ROOT / "output/recurrence_pairs.csv")
    u = pd.read_csv(ROOT / "output/evidence_units.csv")
    top = pairs.sort_values(["A", "C"], ascending=False).head(5)
    mid = pairs[pairs.A.between(3, 5)].sample(5, random_state=2026)
    pilot = pd.concat([top.assign(selection="top-5 by tier A"), mid.assign(selection="random, 3-5 reports")])

    texts = {}
    rows = []
    for p in pilot.itertuples():
        sub = u[(u.taxon == p.taxon) & (u.condition == p.condition) & (u.is_primary == 1)]
        for r in sub.itertuples():
            snips = []
            for sid in r.source_ids.split(";"):
                if sid not in texts:
                    t = ev.source_text(sid); texts[sid] = ev.Src(t) if t else None
                S = texts[sid]
                name = str(r.taxon).replace(" [unresolved]", "")
                # search by every name used for this taxon in the source
                names = set(u[(u.taxon == r.taxon)].taxon) | set(pd.read_csv(ROOT / "output/evidence_records.csv", usecols=["taxon", "name_in_data", "source_id"])
                                                              .query("taxon == @r.taxon and source_id == @sid").name_in_data)
                w = []
                if S:
                    for n in names:
                        w += S.windows(str(n).replace(" [unresolved]", ""), size=260)
                snips.append(f"[{sid}] " + (w[0] if w else "(species not located in source text)"))
            rows.append(dict(pair=f"{p.taxon} | {p.condition}", selection=p.selection, tier_A=p.A, tier_B=p.B, tier_C=p.C,
                             fieldwork_group=r.fieldwork_group, community=r.community, state=r.state, design=r.design,
                             attribution=r.attribution, parts=r.parts, use_found_in_source=r.use_found_in_source,
                             original_use_wording=r.original_use_wording, source_text_snippet=" || ".join(snips)[:900],
                             reader1_row_found="", reader1_same_use="", reader1_part_ok="", reader1_community_ok="", reader1_notes="",
                             reader2_row_found="", reader2_same_use="", reader2_part_ok="", reader2_community_ok="", reader2_notes=""))
    trace = pd.DataFrame(rows)
    summary = pilot[["selection", "taxon", "condition", "species_any_use", "A", "B", "C", "same_part", "A_leave_one_out_min", "states"]]
    out = ROOT / "output/pilot_trace.xlsx"
    if out.exists() and "Pilot_trace_author_checked" in pd.ExcelFile(out).sheet_names:
        print("pilot_trace.xlsx already holds the authors' check; not overwritten"); return
    with pd.ExcelWriter(out) as xw:
        summary.to_excel(xw, sheet_name="Pilot_pairs", index=False)
        trace.to_excel(xw, sheet_name="Trace_for_two_readers", index=False)
    print(summary.to_string(index=False))
    print(f"\n{len(trace)} supporting units exported for two-reader audit")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    s = summary.iloc[::-1]
    y = np.arange(len(s))
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for col, off, colr, lab in [("A", 0.27, "#34495e", "A: all primary reports"), ("B", 0.09, "#2980b9", "B: explicit community attribution"),
                                ("C", -0.09, "#27ae60", "C: + general survey, wording verified"), ("A_leave_one_out_min", -0.27, "#e67e22", "A, worst case leaving one survey out")]:
        ax.barh(y + off, s[col].fillna(0), height=0.17, color=colr, label=lab)
    ax.set_yticks(y); ax.set_yticklabels([f"{t} — {c}" for t, c in zip(s.taxon, s.condition)], fontsize=8)
    ax.set_xlabel("independent community reports"); ax.legend(frameon=False, fontsize=7, loc="lower right")
    fig.tight_layout(); fig.savefig(ROOT / "output/figures/fig_pilot_pairs.png", dpi=200)


if __name__ == "__main__":
    main()
