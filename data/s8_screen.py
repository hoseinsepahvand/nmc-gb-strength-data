#!/usr/bin/env python3
"""S8 screening: raw retrieval -> deduplicated, screened log.
   python3 s8_screen.py            (run from paper/data/)
Input : s8_atomistic_search_2026-09-27_raw.json (written by s8_atomistic_search.py, never edited)
        s8_abstract_cache_2026-09-27.json      (abstracts / page notes for the flagged records)
Output: s8_atomistic_search_2026-09-27.json    (final log read by build_si.py)
Deduplication: (1) record keys = lower-cased DOI, else OpenAlex/URL id;
               (2) works = record keys grouped after removing supplementary-file suffixes (.s001 ...)
                   and grouping identical case-folded titles (preprint/journal/peer-review copies)."""
import json, re, os
H = os.path.dirname(os.path.abspath(__file__))
RAW = json.load(open(os.path.join(H, "s8_atomistic_search_2026-09-27_raw.json"), encoding="utf-8"))
CACHE = json.load(open(os.path.join(H, "s8_abstract_cache_2026-09-27.json"), encoding="utf-8"))
AT = re.compile(r"first.principles|DFT|ab initio|density functional|molecular dynamics|interatomic potential|machine.learning potential|atomistic", re.I)
LAY = re.compile(r"LiCoO|LiNiO|\bNMC\b|\bNCM|\bNCA\b|Ni-rich|nickel-rich|layered oxide|layered cathode|LiMO", re.I)
GB = re.compile(r"grain boundar|intergranular|cleav|separation|decohes|cohes", re.I)
FLAG = {  # decisions after checking the abstract or page (cache)
 "10.1016/j.mtcomm.2024.108852": ("excluded_after_check", "bond-valence model of bulk elastic constants, hardness and fracture toughness; no grain boundary"),
 "10.1016/j.jpowsour.2025.236473": ("excluded_after_check", "experimental study of Li2RuO3 particles (XRD, SEM, TEM); not atomistic"),
 "10.1021/acsaem.4c00279": ("excluded_after_check", "electron microscopy of intragranular cracking; not atomistic"),
}
ALSO = [
 {"key": "10.1021/acs.chemmater.2c01246", "cite": "Dahl et al. 2022, Chem Mater 34:7788", "decision": "no_decohesion_quantity", "reason": "segregation energies and GB energies of Sigma3/Sigma5 boundaries in LiCoO2; no fracture property (full text)"},
 {"key": "10.1002/smll.202307678", "cite": "Kuo et al. 2024, Small", "decision": "no_decohesion_quantity", "reason": "dopant segregation to surfaces and grain boundaries in Ni-rich cathodes; no decohesion quantity in the abstract"},
 {"key": "10.1039/c7cp06615e", "cite": "Min & Cho 2018, PCCP 20:9045", "decision": "no_grain_boundary", "reason": "DFT ideal strength of the defect-free NMC811 lattice (used in Section 5 as an ideal-crystal reference scale)"},
 {"key": "10.1016/j.engfracmech.2026.112537", "cite": "Bian, Wei, Cheng, Yu & Zhao 2026, Eng Fract Mech", "decision": "no_gb_decohesion_quantity_by_abstract",
  "reason": "abstract only (cache): MD with machine-learning potentials trained on first-principles data gives 'composition-dependent anisotropic elasticity and fracture responses' for single-crystal and polycrystalline NCM, which enter a trilinear cohesive law, 'while grain-boundary Weibull heterogeneity is introduced for polycrystalline particles'; by the abstract the atomistic input is not a grain-boundary work of separation or traction-separation law, and the boundary strength is a statistical assignment; full text not read"}]
recs = {}
for q in RAW["queries"]:
    for r in q["results"]:
        recs.setdefault(r["doi_or_url"].lower(), {"r": r, "found_in": []})["found_in"].append(f"{q['id']}#{r['rank']}")
for c in RAW["citation_chains"]:
    for r in c.get("forward", {}).get("results", []):
        recs.setdefault(r["doi_or_url"].lower(), {"r": r, "found_in": []})["found_in"].append("cites:" + c["seed"])
def work_id(k, title):
    base = re.sub(r"\.s\d+$", "", k)
    return base, (title or "").strip().casefold()
groups, by_title = {}, {}
for k, v in recs.items():
    base, t = work_id(k, v["r"]["title"])
    wid = by_title.get(t) if t else None
    wid = wid or groups.get(base) and base or base
    if t: by_title.setdefault(t, wid)
    groups[k] = by_title.get(t, wid) if t else wid
out, cnt = [], {}
for k, v in recs.items():
    t = v["r"]["title"] or ""
    if k in FLAG: dec, why = FLAG[k]; basis = "abstract or page note in s8_abstract_cache_2026-09-27.json"
    elif AT.search(t) and LAY.search(t) and GB.search(t): dec, why = "check_needed", "atomistic + layered oxide + boundary terms in title"; basis = "title"
    elif AT.search(t) and GB.search(t): dec, why = "not_relevant", "atomistic GB study of a non-cathode material (metal, ceramic, electrolyte or other)"; basis = "title"
    else: dec, why = "not_relevant", "title: not an atomistic calculation of a GB decohesion quantity in a layered-oxide cathode"; basis = "title"
    cnt[dec] = cnt.get(dec, 0) + 1
    out.append({"key": k, "work_id": groups[k], "title": t, "year": v["r"]["year"], "found_in": v["found_in"], "screening": {"decision": dec, "reason": why, "basis": basis}})
hits_q = sum(len(q["results"]) for q in RAW["queries"])
chains = [{"seed": c["seed"], "doi": c["doi"], "openalex_id": c.get("openalex_id"), "cited_by_reported": c.get("cited_by_count"), "returned": c.get("forward", {}).get("n", 0)} for c in RAW["citation_chains"]]
hits = hits_q + sum(c["returned"] for c in chains)
works = len(set(groups.values()))
# regression checks on the 2026-09-27 run
assert hits == 678 and len(out) == 628 and cnt.get("check_needed", 0) == 0, (hits, len(out), cnt)
assert [c["returned"] for c in chains] == [10, 22, 109] and [c["cited_by_reported"] for c in chains] == [10, 22, 111]
final = {"_meta": {"step": "S8 atomistic search", "date": "2026-09-27",
  "claim_tested": "No DFT or MD/MLIP calculation of the work of separation, traction-separation law or tensile strength of a grain boundary in a layered-oxide cathode (LiCoO2, LiNiO2, NMC/NCM, NCA, Li-rich) has been reported.",
  "run_from": RAW["_meta"].get("run_from"), "fetch_script": "paper/data/s8_atomistic_search.py", "screen_script": "paper/data/s8_screen.py",
  "note": "decisions are nested in unique_results[*].screening; work_id groups record keys of one scholarly work",
  "supersedes": "the unlogged search of 2026-09-21 (four tools, eleven query framings)",
  "counts": {"queries_total": len(RAW["queries"]), "queries_ok": sum(q["status"] == "ok" for q in RAW["queries"]), "hits_from_queries": hits_q,
             "citation_chains": chains, "hits_total": hits, "unique_record_keys": len(out), "unique_works": works, "screening": cnt},
  "limitations": ["OpenAlex search and Crossref only; Semantic Scholar refused from this network", "screening by title, with abstracts or page notes for flagged items",
                  "OpenAlex searches capped at 50 results per query", "Min & Cho 2018 forward citations: 109 returned of 111 reported by OpenAlex",
                  "Bian et al. 2026 assessed from its abstract only (see also_examined)"]},
 "queries": RAW["queries"], "citation_chains": RAW["citation_chains"], "unique_results": out, "also_examined": ALSO}
json.dump(final, open(os.path.join(H, "s8_atomistic_search_2026-09-27.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"S8: {hits} hits, {len(out)} record keys, {works} works, {cnt}")
