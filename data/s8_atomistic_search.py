"""S8: logged search for atomistic (DFT, MD, MLIP) grain-boundary decohesion data in layered-oxide cathodes, run from the WSL bridge.
Formerly: S7 addendum: rerun the queries that failed on 2026-09-26 (OpenAlex search, Crossref, Semantic Scholar)
and the forward-citation chains, from the WSL bridge. Writes raw results to
paper/data/s8_atomistic_search_2026-09-27_raw.json. Screening is added afterwards (separate key)."""
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
 ("A01","OpenAlex search", oa_search("work of separation grain boundary LiCoO2")),
 ("A02","OpenAlex search", oa_search("grain boundary cohesion first-principles LiNiO2")),
 ("A03","OpenAlex search", oa_search("first-principles grain boundary tensile strength layered oxide cathode")),
 ("A04","OpenAlex search", oa_search("molecular dynamics grain boundary fracture NMC cathode")),
 ("A05","OpenAlex search", oa_search("machine learning interatomic potential grain boundary fracture cathode")),
 ("A06","OpenAlex search", oa_search("traction-separation law grain boundary density functional theory oxide cathode")),
 ("A07","OpenAlex search", oa_search("ab initio tensile test grain boundary lithium cobalt oxide")),
 ("A08","OpenAlex search", oa_search("grain boundary decohesion lithium transition metal oxide")),
 ("A09","OpenAlex search", oa_search("grain boundary DFT NCM811 intergranular cracking")),
 ("A10","OpenAlex search", oa_search("cleavage energy grain boundary layered cathode atomistic")),
 ("A11","Crossref REST API", cr("work of separation grain boundary LiCoO2 OR LiNiO2 OR NMC first-principles", 40)),
 ("A12","Crossref REST API", cr("grain boundary fracture molecular dynamics layered oxide cathode lithium", 40)),
]
SEEDS = [("Dahl 2022","10.1021/acs.chemmater.2c01246"),("Kuo 2024","10.1002/smll.202307678"),("Min & Cho 2018","10.1039/c7cp06615e")]
out = {"_meta": {"step": "S8 atomistic search (third external audit, finding B1)", "run_from": "WSL bridge (jobs/inbox), user's Windows machine", "script": "paper/data/s8_atomistic_search.py",
                  "note": "raw retrieval; screening is done by s8_screen.py"}, "queries": [], "citation_chains": []}
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
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "s8_atomistic_search_2026-09-27_raw.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("written")
