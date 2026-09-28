#!/usr/bin/env python3
"""Figure 3 of Paper B: the admissible window of the cohesive strength for a given regularisation length.
Reproducible: takes the audited parameter sets (ROWS) from lch_audit.py and the measured bounds from
fig1_measurements.json; writes paper/figures/fig3_admissible_window.{pdf,png}.
    python3 paper/data/make_fig3.py
b/l_ch with l_ch = E*Gc/sigma^2 (Wu & Nguyen 2018). Convexity bound b <= 8 l_ch/(3 pi);
operative requirement b << l_ch, scored here as b/l_ch <= 0.1 (a convention, stated in the caption).
Example curve: b = 0.4 um, E = 169.8 GPa, Gc = 1 J/m^2 (private import ledger); dashed: Gc = 0.53 J/m^2.
"""
import os, io, json, math, runpy, contextlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "figures")
with contextlib.redirect_stdout(io.StringIO()):
    NS = runpy.run_path(os.path.join(HERE, "lch_audit.py"))
ROWS, lch_um = NS["ROWS"], NS["lch_um"]
MEAS = json.load(open(os.path.join(HERE, "fig1_measurements.json"), encoding="utf-8"))
LOWER = MEAS["particle_compression"][0]["mean_MPa"]          # Wheatcroft 207 (flat platen)
UPPER = MEAS["micro_tensile"]["weibull"]["sigma_ch_MPa"]      # 745
CONV, SMALL = 8 / (3 * math.pi), 0.1
EX = [r for r in ROWS if r[0].startswith("this work: sigma = 210")][0]
E0, GC, B = EX[1], EX[2], EX[4]
R2 = [r for r in ROWS if "Gc = 0.53" in r[0]][0]; E2, GC2 = R2[1], R2[2]

INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#ffffff"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.linewidth": 0.6,
                     "xtick.color": INK2, "ytick.color": INK2, "savefig.dpi": 600, "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(7.2, 3.9))
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(50, 1000); ax.set_ylim(0.01, 5)
ax.grid(which="both", color=GRID, lw=0.5); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
# zones
ax.axhspan(CONV, 5, color=INK, alpha=0.07, lw=0)
ax.axhspan(SMALL, CONV, color=INK, alpha=0.03, lw=0)
ax.axhline(CONV, color=INK2, lw=0.9); ax.axhline(SMALL, color=INK2, lw=0.9, ls=(0, (4, 2)))
ax.text(52, CONV * 1.12, f"convexity bound of the Wu–Nguyen law  $b = 8\\ell_{{ch}}/3\\pi$  ($b/\\ell_{{ch}}$ = {CONV:.2f})", fontsize=6.6, color=INK2, va="bottom")
ax.text(52, SMALL * 1.12, r"operative $b \ll \ell_{ch}$, scored by convention as $b/\ell_{ch} \leq 0.1$", fontsize=6.6, color=INK2, va="bottom")
ax.text(55, 2.4, "fails the convexity bound", ha="left", fontsize=7, color=INK)
ax.text(55, 0.3, r"convex, $b/\ell_{ch} > 0.1$", ha="left", fontsize=7, color=INK2)
ax.text(55, 0.035, r"passes the 0.1 screen", ha="left", fontsize=7, color=INK2)
# measured bounds
ax.axvspan(LOWER, UPPER, color=BLUE, alpha=0.06, lw=0)
for v, lab in ((LOWER, f"{LOWER:g} MPa\nwhole-particle\n(nominal; what-if)"), (UPPER, f"{UPPER:g} MPa\nmicro-tensile\n(nominal, n = 3;\nwhat-if)")):
    ax.axvline(v, color=BLUE, lw=0.8, ls=(0, (1, 1.5)))
    ax.text(v * 1.03, 0.012, lab, fontsize=6.2, color=INK2, va="bottom", ha="left")
# example curves
s = np.logspace(math.log10(50), 3, 300)
r1 = B / np.array([lch_um(E0, GC, x) for x in s]); r2 = B / np.array([lch_um(E2, GC2, x) for x in s])
ax.plot(s, r1, color=BLUE, lw=2, label=f"b = {B:g} µm, E = {E0:g} GPa, $G_c$ = {GC:g} J/m²")
ax.plot(s, r2, color=BLUE, lw=1.2, ls=(0, (4, 2)), label=f"b = {B:g} µm, E = {E2:g} GPa, $G_c$ = {GC2:g} J/m² (micro-tensile pair)")
# audited literature sets (b reported)
for lab, E, Gc, sig, b, h, note in ROWS:
    if b is None or lab.startswith("this work"): continue
    r = b / lch_um(E, Gc, sig)
    gb = "GB" in lab
    ax.scatter(sig, r, s=30, marker="o" if gb else "s", facecolors=ORANGE if gb else "none", edgecolors=ORANGE,
               linewidths=1.2, zorder=4)
ax.scatter([], [], marker="o", color=ORANGE, label="published set, grain boundary")
ax.scatter([], [], marker="s", facecolors="none", edgecolors=ORANGE, label="published set, grain / bulk")
ax.set_xlabel("Cohesive strength σ  [MPa]", color=INK); ax.set_ylabel(r"$b/\ell_{ch}$  ($\ell_{ch} = E G_c/\sigma^2$)", color=INK)
ax.set_xticks([50, 100, 200, 500, 1000]); ax.set_xticklabels(["50", "100", "200", "500", "1000"])
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False, fontsize=6.6)
fig.savefig(os.path.join(OUT, "fig3_admissible_window.pdf"), bbox_inches="tight", facecolor=SURF)
fig.savefig(os.path.join(OUT, "fig3_admissible_window.png"), bbox_inches="tight", facecolor=SURF)
x_conv = math.sqrt(CONV * E0 * 1e9 * GC / (B * 1e-6)) / 1e6
x_small = math.sqrt(SMALL * E0 * 1e9 * GC / (B * 1e-6)) / 1e6
n_pub=[r for r in ROWS if r[4] is not None and not r[0].startswith("this work")]
print("published sets with b:",len(n_pub),"| conv fail:",sum(r[4]/lch_um(r[1],r[2],r[3])>CONV for r in n_pub),"| small:",sum(r[4]/lch_um(r[1],r[2],r[3])<=SMALL for r in n_pub))
print(f"example b={B} um: strength at convexity bound = {x_conv:.0f} MPa; at b/l_ch=0.1 = {x_small:.0f} MPa")
