"""S7 addendum: rerun the queries that failed on 2026-09-26 (OpenAlex search, Crossref, Semantic Scholar)
and the forward-citation chains, from the WSL bridge. Writes raw results to
paper/data/s7_search_2026-09-27_wsl.json. Screening is added afterwards (separate key)."""
import os, json, time, urllib.request, urllib.parse, datetime
UA = "paperB-s7-rerun (mailto:hosein.sepahvand@ut.ac.ir)"
def get(url):
    t = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return t, "ok", None, json.loads(r.read().decode("utf8"))
    except Exception as e:
        return t, "failed", repr(e)[:200], None
OA = "https://api.openalex.org/works?"
def oa_search(q, n=50):
    return OA + urllib.parse.urlencode({"search": q, "per-page": n, "select": "id,doi,title,publication_year,primary_location", "mailto": "hosein.sepahvand@ut.ac.ir"})
def oa_cites(wid):
    return OA + urllib.parse.urlencode({"filter": "cites:" + wid, "per-page": 200, "select": "id,doi,title,publication_year", "mailto": "hosein.sepahvand@ut.ac.ir"})
def cr(q, n=50):
    return "https://api.crossref.org/works?" + urllib.parse.urlencode({"query": q, "rows": n, "select": "DOI,title,issued,container-title", "mailto": "hosein.sepahvand@ut.ac.ir"})
def s2(q, n=50):
    return "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode({"query": q, "limit": n, "fields": "title,year,externalIds"})
Q = [
 ("W01","OpenAlex search", oa_search("grain boundary strength cathode micro-cantilever")),               # rerun of Q03
 ("W02","OpenAlex search", oa_search("grain boundary strength NMC micro tensile")),                       # rerun of Q23
 ("W03","OpenAlex search", oa_search("grain boundary fracture strength layered oxide cathode micropillar")),
 ("W04","OpenAlex search", oa_search("bicrystal grain boundary fracture LiCoO2 NCA LiNiO2 cathode")),
 ("W05","OpenAlex search", oa_search("intergranular fracture strength NMC secondary particle in situ micromechanical")),
 ("W06","OpenAlex search", oa_search("single grain boundary tensile strength lithium cathode")),
 ("W07","Crossref REST API", cr("bicrystal grain boundary fracture LiCoO2 OR NCA OR LiNiO2 cathode", 30)),   # rerun of Q21
 ("W08","Crossref REST API", cr("micropillar micro-cantilever fracture NMC cathode grain boundary", 30)),     # rerun of Q22
 ("W09","Semantic Scholar Graph API", s2("grain boundary fracture strength layered oxide cathode micropillar")),  # rerun of Q02
 ("W10","Semantic Scholar Graph API", s2("grain boundary strength NMC")),                                    # rerun of Q25
]
SEEDS = [("Sedlatschek 2026","10.1016/j.jpowsour.2026.240276"),("Wheatcroft 2023","10.1002/batt.202300032"),("Stallard 2022","10.1149/1945-7111/ac6244")]
out = {"_meta": {"step": "S7 addendum (R-15 item 3)", "run_from": "WSL bridge (jobs/inbox), user's Windows machine", "script": "paper/data/s7_rerun_wsl.py",
                  "note": "raw results only; screening decisions are added in key 'screening' by a separate pass"}, "queries": [], "citation_chains": []}
def norm(service, d):
    res = []
    if d is None: return res, None
    if service.startswith("OpenAlex"):
        for i, w in enumerate(d.get("results", [])):
            res.append({"rank": i+1, "title": w.get("title"), "year": w.get("publication_year"), "doi_or_url": (w.get("doi") or w.get("id") or "").replace("https://doi.org/","").lower(), "openalex_id": w.get("id")})
        return res, d.get("meta", {}).get("count")
    if service.startswith("Crossref"):
        m = d.get("message", {})
        for i, w in enumerate(m.get("items", [])):
            res.append({"rank": i+1, "title": (w.get("title") or [""])[0], "year": ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0], "doi_or_url": (w.get("DOI") or "").lower(), "venue": (w.get("container-title") or [""])[0]})
        return res, m.get("total-results")
    for i, w in enumerate(d.get("data", [])):
        ext = w.get("externalIds") or {}
        res.append({"rank": i+1, "title": w.get("title"), "year": w.get("year"), "doi_or_url": (ext.get("DOI") or ("arXiv:" + ext["ArXiv"] if ext.get("ArXiv") else "S2:" + w.get("paperId",""))).lower()})
    return res, d.get("total")
for qid, service, url in Q:
    t, st, err, d = get(url)
    if st == "failed" and "429" in (err or ""):
        time.sleep(5); t, st, err, d = get(url)
    res, tot = norm(service, d)
    out["queries"].append({"id": qid, "service": service, "query": url, "timestamp_utc": t, "status": st, "error": err, "n_results_returned": len(res), "n_results_reported_by_service": tot, "results": res})
    print(qid, service, st, len(res), err or "")
    time.sleep(1.5)
for name, doi in SEEDS:
    t, st, err, d = get("https://api.openalex.org/works/doi:" + doi + "?mailto=hosein.sepahvand@ut.ac.ir")
    ch = {"seed": name, "doi": doi, "resolution": {"timestamp_utc": t, "status": st, "error": err}}
    if d:
        wid = d["id"].split("/")[-1]; ch["openalex_id"] = wid; ch["cited_by_count"] = d.get("cited_by_count")
        t2, st2, err2, d2 = get(oa_cites(wid))
        res, tot = norm("OpenAlex", d2)
        ch["forward"] = {"url": oa_cites(wid), "timestamp_utc": t2, "status": st2, "error": err2, "n": len(res), "results": res}
        print(name, wid, d.get("cited_by_count"), st2, len(res))
    out["citation_chains"].append(ch); time.sleep(1.5)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "s7_search_2026-09-27_wsl.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("written")
