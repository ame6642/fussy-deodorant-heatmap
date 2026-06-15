"""
Populate the competitor presence columns (s_nopong ... s_schmidts) per region.

WHY A PRESENCE PROXY, NOT LIVE STORE COUNTS
The 7 competitor brands either sell direct-to-consumer or distribute through
national chains, and the few that publish "stockists" do so via JavaScript
postcode-search widgets that do not expose per-region counts. Scraping exact
store counts is therefore not reliably possible, and inventing precise counts
is the failure mode the brief explicitly warns against. Instead each brand x
region cell holds a documented DISTRIBUTION-INTENSITY score, sourced from where
the brand is actually sold (verified June 2026):

  0 = no meaningful presence
  1 = online / limited independent stockists
  2 = stocked in a national chain (Woolworths / Coles / Chemist Warehouse)
  3 = national chain PLUS the brand's home state (local concentration)

Sources for the AU footprint:
  No Pong         - Woolworths + Coles (national)                  -> 2
  Woohoo Body     - Woolworths (national); HQ Newcastle NSW        -> 2, NSW 3
  KIND-LY         - Chemist Warehouse (national)                   -> 2
  Schmidt's       - Chemist Warehouse AU + NZ (national)           -> 2
  Black Chicken   - Adelaide SA; indie / DTC                       -> 1, SA 2
  Noosa Basics    - Noosa QLD; indie / DTC                         -> 1, QLD 2
  Native (P&G US) - limited AU retail, mostly online               -> 1

The app turns these into the brief's competition score: category validation CV
(more brands / more presence = category proven), saturation SP via a
Herfindahl index (one brand dominating = bad), net = CV - SP, all gated by a
confidence factor C built from brand count B, total presence T and the Trends
data-stability Z. NZ presence for these (AU-centric) brands is thin, so NZ
confidence is low and the gate reallocates competition weight to search intent,
exactly as intended.
"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
BRANDS = ["s_nopong", "s_woohoo", "s_kindly", "s_blackchicken", "s_noosa", "s_native", "s_schmidts"]

# order: nopong, woohoo, kindly, blackchicken, noosa, native, schmidts
AU = {
    "New South Wales":              [2, 3, 2, 1, 1, 1, 2],
    "Victoria":                     [2, 2, 2, 1, 1, 1, 2],
    "Queensland":                   [2, 2, 2, 1, 2, 1, 2],
    "South Australia":              [2, 2, 2, 2, 1, 1, 2],
    "Western Australia":            [2, 2, 2, 1, 1, 1, 2],
    "Tasmania":                     [2, 2, 2, 1, 1, 1, 2],
    "Northern Territory":           [2, 1, 2, 1, 1, 1, 2],
    "Australian Capital Territory": [2, 2, 2, 1, 1, 1, 2],
}
AU_NOTE = "National chains (Woolworths/Coles/Chemist Warehouse) + indie home-state texture"

# NZ: only Schmidt's has clear national presence (Chemist Warehouse NZ). No Pong
# and Woohoo reach the three main metros via online/independent retail. The other
# AU indie brands are effectively absent; NZ's own brands (e.g. Ethique) are out
# of the brief's competitor set. Hence deliberately thin -> low confidence.
NZ_METRO = [1, 1, 0, 0, 0, 0, 2]   # Auckland, Wellington, Canterbury
NZ_REST  = [0, 0, 0, 0, 0, 0, 2]
NZ_METROS = {"Auckland", "Wellington", "Canterbury"}
NZ_NOTE_METRO = "Schmidt's (Chemist Warehouse NZ) + No Pong/Woohoo online in main metros"
NZ_NOTE_REST = "Schmidt's (Chemist Warehouse NZ) only; AU indie brands absent (thin, confidence-gated)"

def populate(csv_name, presence_for, note_for):
    path = os.path.join(HERE, csv_name)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f)); fields = rows[0].keys()
    for r in rows:
        vals = presence_for(r["region"])
        for col, v in zip(BRANDS, vals):
            r[col] = v
        r["comp_note"] = note_for(r["region"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"{csv_name}: competitor presence written for {len(rows)} rows")

populate("au_regions.csv", lambda reg: AU[reg], lambda reg: AU_NOTE)
populate("nz_regions.csv",
         lambda reg: NZ_METRO if reg in NZ_METROS else NZ_REST,
         lambda reg: NZ_NOTE_METRO if reg in NZ_METROS else NZ_NOTE_REST)
print("done")
