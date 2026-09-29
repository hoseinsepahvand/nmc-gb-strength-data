#!/usr/bin/env python3
"""
lch_audit.py -- Figure 3 / SI S6 of Paper B.
Tests every published parameter set against the PF-CZM resolution criteria.

Criteria, with their anchors:
  l_ch := E0*Gc/sigma_c^2                     Wu & Nguyen 2018, Eq. (2.8)
  CONVEXITY : b <= 8*l_ch/(3*pi) ~ 0.85*l_ch  Wu & Nguyen 2018, Eq. (2.39)
                                              restated as Chen et al. 2024, Eq. (B.3)
  MESH      : h <= b/3 <= 8*l_ch/(9*pi)       Chen et al. 2024, Eq. (B.4)
  OPERATIVE : b << l_ch                       Wu & Nguyen 2018, text after Eq. (2.39):
              "it is necessary to consider a small length scale parameter b << l_ch
               in order to sufficiently resolve the phase-field regularization"
              -> we score b/l_ch <= 0.1 as "small", 0.1-0.85 as "convex, >0.1"
Every input, with DOI, anchor and verbatim source string, is in lch_inputs.json (same folder).
"""
import math

PI = math.pi

import json, os
_IN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lch_inputs.json"), encoding="utf-8"))
# label, E0[GPa], Gc[J/m^2 = N/m], sigma_c[MPa], b[um] or None, h[um] or None, note  -- all from lch_inputs.json
ROWS = [(r["label"], r["E_GPa"], r["Gc_J_m2"], r["sigma_MPa"], r["b_um"], r["h_um"], r["note"]) for r in _IN["rows"]]
ORIGIN = {r["label"]: r["origin"] for r in _IN["rows"]}
# (Tu et al. core-shell row removed 2026-09-24 by the strict audit: no verbatim strength, AT2 model.)

def lch_um(E_GPa, Gc, sig_MPa):
    return (E_GPa*1e9 * Gc) / (sig_MPa*1e6)**2 * 1e6   # metres -> micrometres

print(f"{'case':44s} {'l_ch':>7s} {'b':>6s} {'b/l_ch':>7s} {'conv':>5s} {'h':>6s} {'h<=b/3':>7s} {'small?':>18s}")
print("-"*116)
n_conv_fail = n_mesh_fail = n_small = n_tested = 0
for lab, E, Gc, sig, b, h, note in ROWS:
    L = lch_um(E, Gc, sig)
    bconv = 8.0*L/(3.0*PI)
    if b is None:
        print(f"{lab:44s} {L:7.3f} {'--':>6s} {'--':>7s} {'n/a':>5s} {'--':>6s} {'n/a':>7s} {'no length reported':>18s}")
        continue
    n_tested += 1
    r = b/L
    conv = "PASS" if b <= bconv else "FAIL"
    if conv == "FAIL": n_conv_fail += 1
    if h is None:
        mesh = "n/a"
    else:
        mesh = "h<=b/3" if h <= b/3.0 + 1e-12 else "h>b/3"
        if mesh == "h>b/3": n_mesh_fail += 1
    if r <= 0.10:
        small = "small (b<<l_ch)"; n_small += 1
    elif b <= bconv:
        small = "convex, >0.1"
    else:
        small = "over the bound"
    hs = f"{h:6.3f}" if h is not None else f"{'--':>6s}"
    print(f"{lab:44s} {L:7.3f} {b:6.3f} {r:7.3f} {conv:>5s} {hs} {mesh:>7s} {small:>18s}")
print("-"*116)
n_pub_b = sum(1 for lab, E, Gc, sig, b, h, note in ROWS if b is not None and ORIGIN[lab] == "published")
print(f"evaluated rows with a length scale: {n_tested} = {n_pub_b} published + {n_tested - n_pub_b} illustrative (this work)")
print(f"  failing the convexity bound b <= 8 l_ch/3pi : {n_conv_fail}")
print(f"  reported (average) h above b/3, where h given: {n_mesh_fail}")
print(f"  meeting Wu's operative requirement b << l_ch (b/l_ch <= 0.1): {n_small}")
print()
print("cross-check of Chen 2024's own Appendix B arithmetic (inputs from lch_inputs.json):")
_X = _IN["appendixB_crosscheck"]; _R = [r for r in _IN["rows"] if r["label"] == _X["row_label"]][0]
L = lch_um(_R["E_GPa"], _R["Gc_J_m2"], _R["sigma_MPa"])
print(f"  l_ch(grain) = {L:.4f} um  ->  8*l_ch/(9*pi) = {8*L/(9*PI):.4f} um   (paper prints {_X['paper_reported_um']} um)")
n_run_fail = 0
for m in _IN["mesh_cases"]:
    lim = m["b_um"]/3.0; ex = 100*(m["h_um"]/lim - 1); fail = m["h_um"] > lim + 1e-12; n_run_fail += fail
    print(f"  {m['id']}: b = {m['b_um']} um -> b/3 = {lim:.4f} um ; h = {m['h_um']} um -> {'mean h above' if fail else 'mean h within'} b/3 by {ex:.1f}% (a mean cannot verify the local rule)")
print(f"  simulation runs checked: {len(_IN['mesh_cases'])}, reported mean h above b/3: {n_run_fail}  (run-level count, separate from the parameter-set count above)")
for _e in _IN.get("emendations", []):
    print(f"  note: {_e['rows']} {_e['field']}: the printed '{_e['printed']}' is read as {_e['read_as']}; this is our assumption of a unit typo, not confirmed by the authors ({_e['reason']})")
# regression: no source-specific numeric text in this script outside lch_inputs.json
import re as _re
_src = open(__file__, encoding="utf-8").read().split("# regression:")[0]
assert not _re.search(r"93000|0\.217|0\.144|0\.141", _src), "source-specific number typed in lch_audit.py"
