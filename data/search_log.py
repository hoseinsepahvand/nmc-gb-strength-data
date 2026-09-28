#!/usr/bin/env python3
"""Documented re-run of the B-01 literature search (2026-09-25) for the Supplementary Information.
Two services (Crossref, OpenAlex), five query framings each, 40 hits per query. Writes
paper/data/search_log_2026-09-25.json with query, service, date, hit count and every hit (DOI, title, year),
and flags hits whose DOI is not already in review_b01.json (included / excluded / unresolved)."""
import json, os, sys, urllib.request, urllib.parse, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
REV = json.load(open(os.path.join(HERE, "review_b01.json"), encoding="utf-8"))
known = set()
for k in ("included", "excluded", "unresolved_f"):
    for r in REV[k]:
        if r.get("doi"): known.add(r["doi"].lower())
Q = ["cohesive zone grain boundary strength intergranular fracture NMC cathode particle",
     "phase-field fracture polycrystalline cathode intergranular cracking lithium-ion",
     "grain boundary decohesion Ni-rich layered oxide cathode chemo-mechanical model",
     "interfacial strength primary particles secondary particle cracking lithium-ion cathode simulation",
     "intergranular fracture LiCoO2 NCA polycrystal simulation cohesive"]
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-b-sigma-gb search log (mailto:hosein.sepahvand@ut.ac.ir)"})
    return json.load(urllib.request.urlopen(req, timeout=60))
log = {"date": str(datetime.date.today()), "queries": []}
for q in Q:
    cr = get("https://api.crossref.org/works?rows=40&select=DOI,title,issued&query.bibliographic=" + urllib.parse.quote(q))
    hits = [{"doi": i["DOI"].lower(), "title": (i.get("title") or [""])[0], "year": (i.get("issued", {}).get("date-parts") or [[None]])[0][0]} for i in cr["message"]["items"]]
    log["queries"].append({"service": "Crossref REST /works query.bibliographic", "query": q, "n": len(hits), "hits": hits})
    oa = get("https://api.openalex.org/works?per-page=40&search=" + urllib.parse.quote(q))
    hits = [{"doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(), "title": w.get("title") or "", "year": w.get("publication_year")} for w in oa["results"]]
    log["queries"].append({"service": "OpenAlex /works search", "query": q, "n": len(hits), "hits": hits})
new = {}
for e in log["queries"]:
    for h in e["hits"]:
        h["already_screened"] = h["doi"] in known
        if h["doi"] and not h["already_screened"]: new[h["doi"]] = (h["title"], h["year"])
log["not_yet_screened"] = [{"doi": d, "title": t, "year": y} for d, (t, y) in sorted(new.items())]
json.dump(log, open(os.path.join(HERE, "search_log_2026-09-25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"queries {len(log['queries'])}; hits {sum(e['n'] for e in log['queries'])}; not yet screened {len(new)}")
