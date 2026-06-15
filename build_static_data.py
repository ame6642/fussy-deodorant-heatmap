"""
Build the static (non-search, non-competition) columns of the AU and NZ
region data files for the Fussy deodorant opportunity heatmap.

Static layers, all from free/public sources:
  - population: latest official ESTIMATES (not raw census counts)
        AU = ABS Estimated Resident Population, 30 Sep 2025 (rel. 19 Mar 2026)
        NZ = Stats NZ subnational population estimates (latest series, ~2025)
  - climate:  mean annual max temperature (C) + mean annual relative humidity (%)
        AU = Bureau of Meteorology climate normals, capital-city proxy
        NZ = NIWA climate normals, main-centre proxy
  - regulatory: single-use-plastic regulation stringency (1-5), used at 0.05 weight

Search-demand (direct_intent, unaware_intent) and competitor stockist counts
(s_*) are left blank here and filled by the Google Trends and competition steps.
The app coerces them to numeric and refuses to render if demand is all blank.
"""
import csv, os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- AUSTRALIA
# pop = ERP at 30 Sep 2025 (ABS).  temp_c / humidity = BOM annual normals,
# capital-city proxy; QLD/WA nudged up for their tropical north populations.
# reg = single-use plastic ban stringency, 1 (least) - 5 (most advanced).
au = [
    # region, code, lat, lon, population, temp_c, humidity_pct, reg, reg_note
    ("New South Wales",              "NSW", -32.0, 147.0, 8624500, 22.8, 66, 3.0, "Banned single-use plastics 2022 (later mover)"),
    ("Victoria",                     "VIC", -36.8, 144.5, 7104300, 20.4, 64, 3.5, "Single-use plastics banned Feb 2023"),
    ("Queensland",                   "QLD", -22.5, 144.4, 5692600, 28.0, 67, 4.0, "Comprehensive ban, expanded 2023-24; tropical north"),
    ("South Australia",              "SA",  -30.0, 135.5, 1908200, 22.4, 55, 5.0, "First Australian state to ban (2021), most progressive"),
    ("Western Australia",            "WA",  -25.5, 122.0, 3061700, 25.4, 56, 5.0, "Plan for Plastics, among most comprehensive rollouts"),
    ("Tasmania",                     "TAS", -42.0, 146.5,  576700, 17.3, 67, 3.0, "Rolling bans; smaller program"),
    ("Northern Territory",           "NT",  -19.5, 133.5,  265500, 32.0, 69, 2.0, "Least advanced single-use plastics program"),
    ("Australian Capital Territory", "ACT", -35.5, 149.1,  486200, 20.0, 60, 4.0, "Early mover, banned single-use plastics 2021-22"),
]

# ---------------------------------------------------------------- NEW ZEALAND
# pop = Stats NZ subnational estimate (latest series, ~2025).
# temp_c / humidity = NIWA annual normals, regional main-centre proxy.
# reg = national single-use plastic phase-out applies uniformly; minor council
# variation only, so values sit in a narrow band (0.05 weight, near-neutral).
nz = [
    ("Northland",            "NTL", -35.5, 173.8,  201100, 15.8, 80, 3.2, "National plastics phase-out; coastal council waste initiatives"),
    ("Auckland",             "AUK", -36.8, 174.7, 1816000, 15.3, 80, 3.5, "National phase-out + Auckland Council zero-waste plan"),
    ("Waikato",              "WKO", -37.8, 175.3,  532100, 13.7, 82, 3.0, "National phase-out applies"),
    ("Bay of Plenty",        "BOP", -38.0, 176.7,  351500, 14.2, 80, 3.0, "National phase-out applies"),
    ("Gisborne",             "GIS", -38.4, 177.9,   52700, 14.3, 78, 3.0, "National phase-out applies"),
    ("Hawke's Bay",          "HKB", -39.3, 176.7,  179700, 14.1, 75, 3.0, "National phase-out applies"),
    ("Taranaki",             "TKI", -39.3, 174.3,  130300, 13.6, 82, 3.0, "National phase-out applies"),
    ("Manawatu-Whanganui",   "MWT", -39.7, 175.6,  260700, 13.0, 80, 3.0, "National phase-out applies"),
    ("Wellington",           "WGN", -41.1, 175.1,  543400, 12.8, 80, 3.5, "National phase-out + active regional sustainability programs"),
    ("Tasman",               "TAS", -41.4, 172.7,   59900, 12.6, 80, 3.3, "National phase-out; strong local eco profile"),
    ("Nelson",               "NSN", -41.3, 173.3,   54300, 12.9, 78, 3.3, "National phase-out; strong local eco profile"),
    ("Marlborough",          "MBH", -41.6, 173.8,   50800, 12.9, 76, 3.0, "National phase-out applies"),
    ("West Coast",           "WTC", -42.8, 171.0,   34700, 11.8, 85, 3.0, "National phase-out applies"),
    ("Canterbury",           "CAN", -43.5, 171.8,  698200, 11.8, 76, 3.0, "National phase-out applies"),
    ("Otago",                "OTA", -45.4, 169.4,  253900, 10.8, 76, 3.0, "National phase-out applies"),
    ("Southland",            "STL", -45.9, 167.9,  104800,  9.9, 82, 3.0, "National phase-out applies"),
]

COMPETITOR_COLS = ["s_nopong", "s_woohoo", "s_kindly", "s_blackchicken",
                   "s_noosa", "s_native", "s_schmidts"]

HEADER = (["country", "region", "region_code", "lat", "lon",
           "population", "pop_source",
           "temp_c", "humidity_pct", "climate_source", "climate_flag",
           "regulatory_raw", "regulatory_note",
           "direct_intent", "unaware_intent", "demand_note"]
          + COMPETITOR_COLS + ["z_stability", "comp_note"])

def rows(data, country, pop_source, climate_source):
    out = []
    for (region, code, lat, lon, pop, temp, hum, reg, regnote) in data:
        out.append({
            "country": country, "region": region, "region_code": code,
            "lat": lat, "lon": lon,
            "population": pop, "pop_source": pop_source,
            "temp_c": temp, "humidity_pct": hum,
            "climate_source": climate_source, "climate_flag": "approximate",
            "regulatory_raw": reg, "regulatory_note": regnote,
            "direct_intent": "", "unaware_intent": "", "demand_note": "",
            "s_nopong": "", "s_woohoo": "", "s_kindly": "", "s_blackchicken": "",
            "s_noosa": "", "s_native": "", "s_schmidts": "",
            "z_stability": "", "comp_note": "",
        })
    return out

def write(path, data):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(data)
    print("wrote", path, "rows:", len(data))

write(os.path.join(OUT_DIR, "au_regions.csv"),
      rows(au, "AU", "ABS ERP 30 Sep 2025", "BOM annual normals (capital-city proxy)"))
write(os.path.join(OUT_DIR, "nz_regions.csv"),
      rows(nz, "NZ", "Stats NZ subnational estimate 2025", "NIWA annual normals (main-centre proxy)"))
