#!/usr/bin/env python3
"""Figures 1 and 2 of Paper B (sigma_max,GB perspective).

Reproducible: reads ONLY the three JSON files next to this script and writes
paper/figures/fig1_all_values.{pdf,png} and paper/figures/fig2_lineage_100MPa.{pdf,png}.
    python3 paper/data/make_fig1_fig2.py
Fig. 1: every measured pristine-NMC811 strength and every model-assumed GB strength
        on one log axis (the two kinds of quantity are kept in separate, labelled rows).
Fig. 2: citation lineage of the most common model input (100 MPa) - at least two roots.
No DATA value is typed into this file: values, counts, ratios and names come from
review_b01.json, fig1_measurements.json and lineage_100MPa.json. Only layout constants
(positions, sizes, colours, axis limits) are hard-coded.
Audit history: flow audit 2026-09-23 (fresh-context auditor) -> fixes in the same step.
"""
import json, os, math
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)
J = lambda f: json.load(open(os.path.join(HERE, f), encoding="utf-8"))
REV, MEAS, LIN = J("review_b01.json"), J("fig1_measurements.json"), J("lineage_100MPa.json")
INC = REV["included"]
MODE_V, MODE_N = Counter(r["value_MPa"] for r in INC).most_common(1)[0]   # most common model input
MT = MEAS["micro_tensile"]; SCH = MT["weibull"]["sigma_ch_MPa"]
RATIO = SCH / MODE_V

# palette: dataviz reference slots 1-3, validated all-pairs, light mode (2026-09-23).
# aqua is < 3:1 on the surface -> relief: distinct marker shapes / written category + legend.
INK, INK2, MUTED, GRID, SURF, FILL = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#ffffff", "#f3f2ee"
CAT = {"b": ("#2a78d6", "o", "cites another model / blanket citation", "cites a model"),
       "d": ("#eb6834", "s", "value set by the authors themselves", "authors' choice"),
       "e": ("#1baf7a", "^", "no source given", "no source"),
       "c": ("#4a3aa7", "D", "inverse calibration", "calibrated"),
       "a": ("#e34948", "P", "cites a measurement", "cites a measurement")}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                     "axes.linewidth": 0.6, "xtick.color": INK2, "ytick.color": INK2,
                     "savefig.dpi": 600, "pdf.fonttype": 42})

def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", facecolor=SURF)
    plt.close(fig)

# ------------------------------------------------------------------ Fig. 1
def fig1():
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.set_xscale("log"); ax.set_xlim(10, 1000)
    ax.grid(axis="x", which="both", color=GRID, lw=0.5); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    rows = []
    # (1) model inputs - stacked; neighbouring values closer than 10 % continue the stack
    y0 = 0.0; STEP = 0.3
    vals = sorted({r["value_MPa"] for r in INC}); level = {}; prev = None; base = 0
    for v in vals:
        base = base if (prev and v / prev < 1.1) else 0
        grp = sorted([r for r in INC if r["value_MPa"] == v], key=lambda r: r["category"])
        for k, r in enumerate(grp):
            c, m = CAT[r["category"]][:2]
            ax.scatter(v, y0 + STEP * (base + k), s=34, marker=m, facecolors="none", edgecolors=c,
                       linewidths=1.4, zorder=3)
        level[v] = base + len(grp) - 1; base += len(grp); prev = v
    ytop = y0 + STEP * level[MODE_V]
    ax.annotate(f"{MODE_N} of {len(INC)} models\nuse {MODE_V:g} MPa", xy=(MODE_V * 0.93, ytop),
                xytext=(MODE_V * 0.45, ytop), fontsize=7, color=INK, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    rows.append((y0 + 0.45, f"Model input:\nGB strength used\n(n = {len(INC)} models)"))
    # ratio arrow, on the model row, from the mode to the micro-tensile value
    # (ratio arrow removed 2026-09-28 after Reviewer 1: nominal and model quantities are not equivalent)
    # (2) micro-tensile across GBs
    y_mt = ytop + 1.55
    m, n = MT["weibull"]["m"], MT["weibull"]["n"]
    q = lambda p: SCH * (-math.log(1 - p)) ** (1 / m)          # Weibull quantile (Sedlatschek eq. 2)
    lo, hi = q(0.05), q(0.95)
    ax.fill_betweenx([y_mt - 0.22, y_mt + 0.22], lo, hi, color=INK, alpha=0.06, lw=0, zorder=1)
    for v in MT["individual_MPa"]:
        ax.scatter(v, y_mt, s=26, marker="x", color=INK, linewidths=1.2, zorder=3)
    ax.plot([SCH, SCH], [y_mt - 0.26, y_mt + 0.26], color=INK, lw=1.0, ls=(0, (2, 1.5)), zorder=3)
    ax.text(SCH, y_mt + 0.34, f"$\\sigma_{{ch}}$ = {SCH:g} MPa (Weibull m = {m:g}, n = {n};\nfit is indicative only; lithiated, exact $x_{{Li}}$ not reported)",
            ha="center", va="bottom", fontsize=6.4, color=INK2, linespacing=1.2)
    ax.text(lo, y_mt - 0.3, "5–95 % of fitted Weibull (indicative, n = 3)", ha="left", va="top", fontsize=6, color=MUTED)
    ax.text(62, y_mt, MT["short"], ha="right", va="center", fontsize=6.8, color=INK2)
    rows.append((y_mt, "Measured: FIB micro-tensile,\nfew GBs (authors: avg. GB strength)"))
    # (3) whole-particle measurements: flat platen / flat punch, then cono-spherical tip
    y_pc = y_mt + 1.3
    studies = []
    for r in MEAS["particle_compression"]:
        if not studies or studies[-1][0] != r["short"]: studies.append([r["short"], []])
        studies[-1][1].append(r)
    tip = MEAS["particle_tip_indentation"]
    for i, (name, rs) in enumerate(studies):
        yy = y_pc + 0.5 * i
        pts = []
        for r in rs:
            if "means_MPa" in r: pts += [(v, None, None) for v in r["means_MPa"]]
            else: pts.append((r["mean_MPa"], r["sd_MPa"], r.get("point_tag")))
        for j, (v, sd, tg) in enumerate(pts):
            dy = (j - (len(pts) - 1) / 2) * 0.15
            if sd: ax.errorbar(v, yy + dy, xerr=sd, fmt="o", ms=4.2, color=INK, ecolor=INK2, elinewidth=0.9, capsize=2, zorder=3)
            else: ax.scatter(v, yy + dy, s=20, marker="o", color=INK, zorder=3)
            if tg: ax.text(v + sd + 6, yy + dy, tg, ha="left", va="center", fontsize=5.6, color=INK2)
        ax.text(62, yy, name + (" (means only)" if "means_MPa" in rs[0] else ""), ha="right", va="center", fontsize=6.8, color=INK2)
    rows.append((y_pc + 0.5, "Measured: whole-particle\nstrength, flat platen\n/ flat punch"))
    y_tip = y_pc + 0.5 * len(studies) + 0.55
    for r in tip:
        ax.errorbar(r["mean_MPa"], y_tip, xerr=r["sd_MPa"], fmt="o", ms=4.2, mfc=SURF, mec=INK, color=INK,
                    ecolor=INK2, elinewidth=0.9, capsize=2, zorder=3)
        ax.text(r["mean_MPa"] + r["sd_MPa"] + 8, y_tip, "also depends on $K_{IC}$ (authors)", ha="left", va="center", fontsize=6, color=INK2)
        ax.text(62 if r["mean_MPa"] - r["sd_MPa"] > 62 else (r["mean_MPa"] - r["sd_MPa"]) * 0.92, y_tip, r["short"],
                ha="right", va="center", fontsize=6.8, color=INK2)
    rows.append((y_tip, "Measured: whole-particle,\ncono-spherical tip"))
    ax.set_yticks([r[0] for r in rows]); ax.set_yticklabels([r[1] for r in rows], fontsize=7, color=INK)
    ax.set_ylim(y0 - 0.5, y_tip + 0.5)
    ax.set_xlabel("Strength  [MPa]   (log scale; measured: pristine particles, micro-tensile lithiated (exact $x_{Li}$ not reported); models: as assumed)", color=INK)
    ax.set_xticks([10, 20, 50, 100, 200, 500, 1000]); ax.set_xticklabels(["10", "20", "50", "100", "200", "500", "1000"])
    used = sorted({r["category"] for r in INC})
    h = [plt.Line2D([], [], ls="", marker=CAT[k][1], mfc="none", mec=CAT[k][0], mew=1.4, ms=6, label=f"model input: {CAT[k][2]}") for k in used]
    h += [plt.Line2D([], [], ls="", marker="o", color=INK, ms=4.5, label="measured mean ± scatter as reported"),
          plt.Line2D([], [], ls="", marker="x", color=INK, ms=5, label="measured single test")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.45, -0.14), ncol=2, frameon=False, fontsize=6.8,
              handletextpad=0.4, columnspacing=1.5)
    save(fig, "fig1_all_values")

# ------------------------------------------------------------------ Fig. 2
def fig2():
    N = {n["id"]: n for n in LIN["nodes"]}
    col = {y: 1.5 * i for i, y in enumerate((2012, 2018, 2019, 2020, 2021, 2023, 2025, 2026))}
    X = lambda k: col[N[k]["year"] if N[k]["year"] else 2012]
    lane = {"TiO2": 6.1, "ZHU12": 4.8, "ZG18": 3.1, "M05": 4.8, "M12": 1.5, "ZHUX20": 3.2,
            "M11": 2.0, "M02": 0.2, "M03": -1.2, "M10": 0.0, "M09": -1.5, "M13": 4.8}
    pos = {k: (X(k), lane[k]) for k in N}
    fig, ax = plt.subplots(figsize=(7.9, 5.0)); ax.axis("off")
    STY = {"external": dict(fc=FILL, ec=MUTED, ls=(0, (3, 2))), "unopened": dict(fc=SURF, ec=MUTED, ls=(0, (1, 1.5))),
           "lineage_only": dict(fc=FILL, ec=INK2, ls="-")}
    TXT = {}
    for k, n in N.items():
        x, y = pos[k]
        st = STY.get(n["kind"]) or dict(fc=SURF, ec=CAT[n["category"]][0] if n.get("category") else INK2, ls="-")
        label = n["label"] + (f"\n[{CAT[n['category']][3]}]" if n.get("category") else "")
        TXT[k] = ax.text(x, y, label, ha="center", va="center", fontsize=5.9, color=INK, zorder=3, linespacing=1.3,
                         weight="bold" if n["kind"] == "root" else "normal",
                         bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.5", fc=st["fc"], ec=st["ec"],
                                   lw=2.0 if n["kind"] == "root" else 1.1, ls=st["ls"]))
    fig.canvas.draw()
    for e in LIN["edges"]:
        (x0, y0), (x1, y1) = pos[e["from"]], pos[e["to"]]
        ls = {"cites": "-", "shared_author": (0, (4, 3)), "estimate": (0, (2, 2))}[e["kind"]]
        ce = INK2 if e["kind"] == "cites" else MUTED
        rad = 0.0 if abs(y1 - y0) < 0.05 or abs(x1 - x0) < 1e-6 else (-0.2 if y1 > y0 else 0.2)
        if (e["from"], e["to"]) == ("M12", "M03"): rad = 0.55          # route left/below the M02 box
        if (e["from"], e["to"]) == ("ZHU12", "ZG18"): rad = -0.35     # bend right, clear of the ZHU12 note
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=4,
                    arrowprops=dict(arrowstyle="-|>", mutation_scale=8, lw=0.9, color=ce, linestyle=ls,
                                    connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=4,
                                    patchA=TXT[e["from"]].get_bbox_patch(), patchB=TXT[e["to"]].get_bbox_patch()))
    def note(k, text, dx, dy, ha):
        x, y = pos[k]; ax.text(x + dx, y + dy, text, ha=ha, va="center", fontsize=5.6, color=INK2, linespacing=1.2)
    note("ZHU12", "\n".join(N["ZHU12"]["tags"]), -0.12, -0.85, "right")
    note("M12", "\n".join(N["M12"]["tags"]), -1.1, 0, "right")
    note("ZHUX20", "\n".join(N["ZHUX20"]["tags"]), 0, 0.72, "center")
    note("TiO2", N["TiO2"]["why"], 0.85, 0, "left")
    note("ZG18", "2nd parent of Zhang 2019;\nits Table 1: 100 MPa [23]\n= Zhu 2012 (a relay,\nnot a third root)", -1.12, -0.05, "right")
    cm = LIN["comparison"]; xs = 7 * 1.5 + 1.1
    ax.plot([xs, xs], [-2.0, 6.5], color=INK2, lw=0.9, ls=(0, (3, 2)))
    ax.text(xs + 0.12, 2.3, f"{SCH:g} MPa, nominal\n(not a model input)\n\n" + cm["label"].replace(" (", "\n(").replace("across", "\nacross")
            + f"\n{MT['short']}", ha="left", va="center", fontsize=6.2, color=INK, linespacing=1.25)
    for yr, c in col.items():
        ax.text(c, 6.95, str(yr), ha="center", va="center", fontsize=7, color=INK2)
    Lh = [plt.Line2D([], [], color=INK2, lw=0.9, label="explicit citation for the 100 MPa value"),
          plt.Line2D([], [], color=MUTED, lw=0.9, ls=(0, (4, 3)), label="shared author, no citation (inference)"),
          plt.Line2D([], [], color=MUTED, lw=0.9, ls=(0, (2, 2)), label="estimated from (density analogy)")]
    Lh += [Patch(fc=SURF, ec=CAT[k][0], lw=1.2, label=f"review row [{CAT[k][3]}]") for k in ("b", "d", "e")]
    Lh += [Patch(fc=FILL, ec=INK2, lw=1.0, label="lineage only (not in review)"),
           Patch(fc=FILL, ec=MUTED, lw=1.0, ls=(0, (3, 2)), label="non-battery source value"),
           Patch(fc=SURF, ec=INK, lw=2.2, label="root (thick border)")]
    ax.legend(handles=Lh, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False, fontsize=6.2)
    ax.set_xlim(-2.0, 13.4); ax.set_ylim(-2.1, 7.2)
    save(fig, "fig2_lineage_100MPa")

if __name__ == "__main__":
    fig1(); fig2()
    print(f"mode = {MODE_V} MPa ({MODE_N}/{len(INC)}), ratio sigma_ch/mode = {RATIO:.2f}")
    print("wrote", sorted(f for f in os.listdir(OUT) if f.startswith("fig")))
