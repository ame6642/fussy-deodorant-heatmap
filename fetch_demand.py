"""
Populate the search-demand columns (direct_intent, unaware_intent, z_stability)
in au_regions.csv and nz_regions.csv.

Primary source is demand_cache.json, the values captured from the Google Trends
Explore UI on 2026-06-15 (browser automation, using the user's VPN to avoid the
rate limiting that blocks unattended scrapers). The cache is committed so the app
only ever READS finished CSVs and never depends on a live Trends call at deploy time.

If you want to refresh the data and pytrends works from your network, set
USE_PYTRENDS = True. Query ONE combined OR term per axis (a single search item),
never multiple comma-separated terms, or Google returns cross-term shares instead
of cross-region interest (the "shares trap"). Then rewrite demand_cache.json.
"""
import csv, json, os

USE_PYTRENDS = False  # cache is authoritative; pytrends path left as a stub
HERE = os.path.dirname(os.path.abspath(__file__))

def load_cache():
    with open(os.path.join(HERE, "demand_cache.json"), encoding="utf-8") as f:
        return json.load(f)

def populate(csv_name, country, cache):
    path = os.path.join(HERE, csv_name)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fields = rows[0].keys()
    cc = cache[country]
    missing = []
    for r in rows:
        region = r["region"]
        if region not in cc:
            missing.append(region)
            continue
        d = cc[region]
        r["direct_intent"] = d["direct"]
        r["unaware_intent"] = d["unaware"]
        r["z_stability"] = d["z"]
        r["demand_note"] = d.get("flag", "Trends UI 2026-06-15")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    if missing:
        raise SystemExit(f"ERROR: {csv_name} regions not in cache: {missing}")
    print(f"{csv_name}: populated demand for {len(rows)} rows")

def verify(csv_name):
    path = os.path.join(HERE, csv_name)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    bad = 0
    for c in ["direct_intent", "unaware_intent"]:
        for r in rows:
            try:
                float(r[c])
            except (ValueError, TypeError):
                bad += 1
    print(f"{csv_name}: blank/non-numeric demand cells = {bad}  (must be 0)")
    return bad

if __name__ == "__main__":
    if USE_PYTRENDS:
        raise SystemExit("pytrends path not implemented; this environment blocks Google. Use the cache.")
    cache = load_cache()
    populate("au_regions.csv", "AU", cache)
    populate("nz_regions.csv", "NZ", cache)
    total_bad = verify("au_regions.csv") + verify("nz_regions.csv")
    print("OK: zero blank demand cells" if total_bad == 0 else "FAILED: blank demand cells present")
