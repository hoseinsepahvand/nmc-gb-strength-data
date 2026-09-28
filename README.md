# Data and code: grain-boundary strength in NMC fracture models

This repository holds the data and scripts behind the Perspective

> H. Sepahvand, M.M. Seyyed Fakhrabadi, *Three quantities behind the grain-boundary strength in NMC fracture models* (submitted to Journal of Power Sources, 2026).

Archived version 1.0: https://doi.org/10.5281/zenodo.23019792 (Zenodo).

It contains the review records, the logged literature searches, the values plotted in the figures, and the scripts that turn them into the tables, figures and Supplementary Information. It does not contain the manuscript text, third-party full texts or publisher abstracts.

## Contents

`protocol/`
- `PREREG_B01_review_2026-09-22.md`: the review protocol (in Persian). It was committed on 22 September 2026, before the first search, in the authors' private project repository.
- `PROVENANCE.json`: the first commit and the SHA-256 of the unmodified protocol file. Two references to private folder paths are replaced in this copy.

`data/`: records
- `review_b01.json`: the 12 classified models, 23 exclusions and 7 unclassified candidates. Each record has its category and the source statement as quoted from the paper.
- `search_log_2026-09-25.json`, `screening_ledger_2026-09-25.json`, `new_candidates_2026-09-26.json`: the logged repeat search, with a screening decision for every record (SI S2).
- `fig1_measurements.json`: the measured strengths in Fig. 1, with the verbatim statements.
- `lineage_100MPa.json`: the citation lineage of the 100 MPa value (Fig. 2).
- `lch_inputs.json`: every parameter set screened in Section 4 and Fig. 3, with verbatim table entries and the stated emendation of Chen et al. 2025.
- `s7_search_*.json`: the logged search for boundary-resolved measurements (SI S7).
- `s8_atomistic_search_2026-09-27*.json`: the logged search for atomistic decohesion data (SI S8), raw and screened.

`data/`: scripts
- `review_b01_tally.py`: the category counts.
- `lch_audit.py`: the ℓ_ch screen (SI S6).
- `make_fig1_fig2.py`, `make_fig3.py`, `make_fig4.py`, `make_table1.py`: the figures and Table 1.
- `build_si.py`: the tables of the Supplementary Information.
- `search_log.py`, `s7_rerun_wsl.py`, `s8_atomistic_search.py`, `s8_screen.py`: the retrieval and screening scripts.

## Reproducing

Python 3.10 or later, with `numpy` and `matplotlib`:

```
cd data
python3 review_b01_tally.py
python3 lch_audit.py
mkdir -p ../figures && python3 make_fig1_fig2.py && python3 make_fig3.py && python3 make_fig4.py
```

Two scripts cannot be rerun exactly from this repository:
- `s8_screen.py` also reads a cache of publisher abstracts, which is withheld for copyright reasons. Its output, `s8_atomistic_search_2026-09-27.json`, is included.
- The retrieval scripts query OpenAlex and Crossref, so a rerun today will return a different result set. The logged results used in the paper are the JSON files here.

## Coverage and limits

The searches were run between 21 and 27 September 2026. They used OpenAlex, Crossref and web search; Scopus and Web of Science were not used. Screening was by title, and by abstract or full text for flagged records. A negative finding reads "we found no", not "none exists". Literature screening was assisted by Claude (Anthropic). Every classification of the twelve models rests on a source statement quoted from the full text.

## License

Data (`*.json`, `protocol/`): CC BY 4.0. Code (`*.py`): MIT. See `LICENSE`.

## Contact

Hosein Sepahvand, School of Mechanical Engineering, College of Engineering, University of Tehran (hosein.sepahvand7@gmail.com).
