# Fussy AU + NZ acquisition heatmap

An interactive Streamlit choropleth that ranks Australian states/territories (8) and New Zealand
regions (16) by opportunity score for a premium / natural ("fussy") deodorant brand deciding where
to concentrate launch marketing. It mirrors the North America (Hello Klean) build, adapted to a
deodorant category and the confidence-gated scoring model.

## What it scores

`Opportunity = 0.30 direct intent + 0.25 unaware intent + 0.30 x C competition + 0.10 climate + 0.05 regulatory`

All signals are min-max normalised within each country. The competition weight is multiplied by a
per-region confidence factor **C**; the freed weight `0.30 x (1 - C)` is reallocated to the two intent
axes, so a region with thin competitor data is scored almost entirely on search demand. Sidebar
weights are renormalised to sum to 1, so the map and ranking re-rank live as you adjust them.

See the in-app "Methodology" expander (or `methodology.md`) for the full definition of every layer.

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app fetches the AU/NZ boundary polygons once from the public geoBoundaries dataset (pinned commit)
and caches them under `geojson_cache/`. It needs internet on first run; Streamlit Community Cloud and a
normal local machine both have it.

## Data and provenance

| Layer | Source | Captured |
|---|---|---|
| Search intent (direct + unaware) | Google Trends interest-by-subregion, 12-month, one combined OR query per axis | 2026-06-15 |
| Competition | Distribution-intensity of 7 competitor brands (national chains vs indie home-state) | 2026-06 |
| Climate (heat + humidity) | Bureau of Meteorology (AU) / NIWA (NZ) normals, capital / main-centre proxy | normals |
| Regulatory | State single-use-plastic ban stringency (AU); national phase-out (NZ) | 2026 |
| Population (context only, not scored) | ABS ERP 30 Sep 2025; Stats NZ subnational estimate 2025 | 2025 |

Demand values are committed in `au_regions.csv` / `nz_regions.csv` and cached in `demand_cache.json`.
The app only ever reads finished CSVs; it never calls Google Trends at run time.

## Refreshing the search demand

`fetch_demand.py` writes the demand columns from `demand_cache.json`. The cache was captured through the
Google Trends UI (browser) because Trends rate-limits unattended scrapers; a VPN avoids the throttling.
To refresh, re-pull each axis as a single combined `term1 + term2 + ...` query (one search item, which
avoids the multi-term "shares trap"), update `demand_cache.json`, then run `python fetch_demand.py` and
confirm it prints zero blank demand cells before deploying.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repo (commit the populated CSVs and `demand_cache.json`).
2. On share.streamlit.io, create an app from the repo with `app.py` as the main file.
3. On push, Streamlit auto-redeploys. Unpinned `requirements.txt` installs current versions at build time.

## Limitations (read honestly when presenting)

Directional portfolio model on free public data, not a precision tool. AU search intent is high but
compressed across states. NZ direct intent is low-volume (several regions fell below Google's reporting
threshold and are imputed low and flagged). The competition layer is a documented distribution proxy,
not live store counts. Low-confidence regions are outlined on the map rather than silently trusted.

## Files

```
app.py                Streamlit UI (map + ranking + methodology)
scoring.py            opportunity score + confidence gate (pure pandas, unit-testable)
mapviz.py             boundary simplification + plotly choropleth
build_static_data.py  builds the static CSV columns (climate, regulatory, population, geo)
fetch_demand.py       writes search-demand columns from demand_cache.json
build_competition.py  writes competitor presence columns
au_regions.csv        8 AU states/territories, fully populated
nz_regions.csv        16 NZ regions, fully populated
demand_cache.json     captured Google Trends values + provenance
methodology.md        methodology text rendered in the app
requirements.txt      unpinned dependencies
```
