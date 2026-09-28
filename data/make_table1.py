#!/usr/bin/env python3
"""Table 1 of Paper B: every model-assumed GB strength and the source each paper states.
Reads ONLY review_b01.json; writes paper/sections/table1.md (Markdown) and table1.tex.
    python3 paper/data/make_table1.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "sections"); os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(HERE, "review_b01.json"), encoding="utf-8"))
CAT = {"a": "cites a measurement", "b": "cites another model / blanket", "c": "inverse calibration",
       "d": "set by the authors", "e": "no source given"}
rows = sorted(D["included"], key=lambda r: (r["value_MPa"], r["cite"]))
def short(c): return c.split(" (")[0].split(",")[0] + " et al." if "," in c.split(" (")[0] else c.split(" (")[0]
def year(c): return c.split("(")[1].split(")")[0]
def quote(r):
    return r["table_quote"]            # paper's own words; editorial notes in [square brackets]
md = ["| Model | Year | Value [MPa] | What the paper gives as the source (verbatim; our notes in [ ]) | Category |", "|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {short(r['cite'])} | {year(r['cite'])} | {r['value_MPa']:g} | {quote(r).replace('|', '/')} | {CAT[r['category']]} |")
n = len(rows); na = sum(r["category"] == "a" for r in rows)
unres = [u for u in D["unresolved_f"] if not str(u.get("blocker", "")).startswith("RESOLVED")]
md.append("")
md.append(f"*{n} models whose parameter table could be opened; {na} cite a measurement. "
          f"{len(unres)} further models could not be classified and {len(D['excluded'])} were excluded with a stated reason (full list in the Supplementary Information). "
          "Categories follow a protocol registered before the search.*")
open(os.path.join(OUT, "table1.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
esc = lambda s: s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")
tex = [r"\begin{tabular}{p{2.6cm}p{0.8cm}p{1.2cm}p{7.2cm}p{2.4cm}}", r"\hline",
       r"Model & Year & Value [MPa] & Source stated by the paper (verbatim, abridged) & Category \\ \hline"]
for r in rows:
    tex.append(f"{esc(short(r['cite']))} & {year(r['cite'])} & {r['value_MPa']:g} & {esc(quote(r))} & {CAT[r['category']]} \\\\")
tex += [r"\hline", r"\end{tabular}"]
open(os.path.join(OUT, "table1.tex"), "w", encoding="utf-8").write("\n".join(tex) + "\n")
print(f"table1: {n} rows, category a = {na}, unresolved = {len(unres)}")
