#!/usr/bin/env python3
"""Tally for step B-01. Acceptance criterion AC-4: the ratio comes from this script,
not from counting by eye. Criteria are defined in protocol/PREREG_B01_review_2026-09-22.md"""
import json, os
D = json.load(open(os.path.join(os.path.dirname(__file__), "review_b01.json"), encoding="utf-8"))
inc, exc, unres = D["included"], D["excluded"], D["unresolved_f"]
LABEL = {"a":"(a) cited to a specific MEASUREMENT",
         "b":"(b) cited to another MODELLING paper / blanket citation",
         "c":"(c) inverse calibration / fit",
         "d":"(d) explicit 'trial and error' / 'assumed' / 'chosen'",
         "e":"(e) NO source given (text seen, quote held)",
         "f":"(f) UNRESOLVED - table could not be opened"}
counts = {k: 0 for k in LABEL}
for r in inc:
    counts[r["category"]] += 1
counts["f"] = len([u for u in unres if not str(u.get("blocker", "")).startswith("RESOLVED")])
n_cat = len(inc)
# Regression guard (external audit 2026-09-26, finding C2): Guichard M01 is an inverse
# calibration to whole-particle indentation (arXiv:2601.02879 p. 5), not an author choice.
assert [r["category"] for r in inc if r["id"] == "M01"] == ["c"], "M01 Guichard must be category (c)"
assert not any(str(u.get("blocker", "")).startswith("RESOLVED") for u in unres), "resolved rows belong in resolved_history"
print("=" * 72)
print("STEP B-01 TALLY -- source of the grain-boundary strength in layered-oxide")
print("cathode fracture models.  compiled 2026-09-22")
print("=" * 72)
for k in "abcdef":
    bar = "#" * counts[k]
    print(f"  {LABEL[k]:<52s} {counts[k]:3d} {bar}")
print("-" * 72)
print(f"  categorised papers (denominator, excludes f)        n = {n_cat}")
print(f"  excluded with a stated reason                           {len(exc)}")
print(f"  still unresolved (f)                                    {counts['f']}")
print()
pct_a = 100.0 * counts["a"] / n_cat if n_cat else float("nan")
print(f"  FRACTION CITED TO A MEASUREMENT: {counts['a']}/{n_cat} = {pct_a:.1f}%")
print()
print("ACCEPTANCE CRITERIA (pre-registered 2026-09-22, before any search)")
ac1 = counts["a"] == 0
ac2 = n_cat >= 15
ac3 = all(r.get("source_verbatim") for r in inc if r["category"] == "e")
ac4 = True
print(f"  AC-1  category (a) == 0 ................... {'PASS' if ac1 else 'FAIL'}  (a={counts['a']})")
print(f"  AC-2  n >= 15 ............................. {'PASS' if ac2 else 'FAIL'}  (n={n_cat})")
print(f"  AC-3  every (e) row carries a verbatim quote {'PASS' if ac3 else 'FAIL'}")
print(f"  AC-4  ratio produced by this script ....... {'PASS' if ac4 else 'FAIL'}")
print()
if not ac2:
    print("  >>> AC-2 FAILED, so the pre-registered consequence is MANDATORY:")
    print("      the paper may NOT claim 'none of the literature'. It must claim")
    print(f"      'of the {n_cat} papers whose parameter table we could open, none'")
    print(f"      and must state the {counts['f']} unresolved papers in the text.")
print()
print("The 100 MPa cluster:", [r["id"] for r in inc if r["value_MPa"] == 100])
print("  Two roots (full graph: lineage_100MPa.json, figure: make_fig1_fig2.py):")
print("  (1) Xu et al. 2018 Exp Mech (M12): 'We set the interfacial strength ... as 100 MPa' - no source.")
print("  (2) Zhu, Park & Sastry 2012: a TiO2 density-analogy estimate of the BULK strength")
print("      of a LiMn2O4 SPINEL single particle, with no GB in the model (reaches M05 only).")
