#!/usr/bin/env python3
"""Figure 4 of Paper B: the reporting protocol as a flowchart (schematic; no data).
Text of every box follows Sections 4 and 6 of the draft. Writes paper/figures/fig4_protocol.{pdf,png}.
    python3 paper/data/make_fig4.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
INK, INK2, MUTED, SURF, FILL, BLUE, ORANGE = "#0b0b0b", "#52514e", "#8a8984", "#ffffff", "#f3f2ee", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 600, "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(7.2, 3.3)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.4)
def box(x, y, text, ec=INK2, fc=SURF, bold=False):
    return ax.text(x, y, text, ha="center", va="center", fontsize=6.6, color=INK, linespacing=1.3,
                   weight="bold" if bold else "normal",
                   bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.4", fc=fc, ec=ec, lw=1.2))
B = {}
B[1] = box(1.05, 3.3, "1  Which scale does\nthe model resolve?\n(grain boundary /\nwhole particle)", ec=BLUE)
B[2] = box(3.35, 3.3, r"2  Calibrate $\sigma_{GB}^{eff}$ against" + "\nthe measurement of that\nscale (geometry, volume,\nlithiation state)", ec=BLUE)
B[3] = box(5.75, 3.3, r"3  Compute" + "\n" + r"$\ell_{ch} = E G_c/\sigma^2$" + "\n" + r"and $b/\ell_{ch}$", ec=BLUE)
B[4] = box(8.35, 3.3, r"4  $b/\ell_{ch}$ ≤ threshold?" + "\n(convexity: 0.85;\noperative: ≪ 1, e.g. 0.1)", ec=INK, bold=False)
B[5] = box(8.35, 1.25, "yes → run", ec=BLUE)
B[6] = box(5.3, 1.25, "no → refine b and h, or use\nanother validated formulation;\notherwise do not run. A lower σ\nonly as a labelled sensitivity run", ec=ORANGE)
B[7] = box(1.85, 1.0, r"ALWAYS REPORT" + "\nσ with its provenance category ·\ntest geometry, volume, n, scatter,\nlithiation state · law shape, mixed-mode\nrule · E, " + r"$G_c$, b, local h, $\ell_{ch}$, $b/\ell_{ch}$" + "\nthreshold, convergence evidence", ec=INK, fc=FILL, bold=False)
fig.canvas.draw()
def arrow(a, b, ls="-", rad=0.0, col=INK2):
    ax.annotate("", xy=(0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", mutation_scale=9, lw=1.0, color=col, ls=ls,
                connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=3, patchA=B[a].get_bbox_patch(), patchB=B[b].get_bbox_patch()),
                annotation_clip=False)
for a, b in ((1, 2), (2, 3), (3, 4), (4, 5), (4, 6)): pass
def link(a, b, rad=0.0, ls="-"):
    pa, pb = B[a].get_position(), B[b].get_position()
    ax.annotate("", xy=pb, xytext=pa, arrowprops=dict(arrowstyle="-|>", mutation_scale=9, lw=1.0, color=INK2, ls=ls,
                connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=3,
                patchA=B[a].get_bbox_patch(), patchB=B[b].get_bbox_patch()))
link(1, 2); link(2, 3); link(3, 4); link(4, 5); link(4, 6)
link(6, 3, rad=-0.25, ls=(0, (3, 2)))
link(5, 7, rad=0.25, ls=(0, (1, 1.5))); link(6, 7, ls=(0, (1, 1.5)))
fig.savefig(os.path.join(OUT, "fig4_protocol.pdf"), bbox_inches="tight", facecolor=SURF)
fig.savefig(os.path.join(OUT, "fig4_protocol.png"), bbox_inches="tight", facecolor=SURF)
print("wrote fig4_protocol")
