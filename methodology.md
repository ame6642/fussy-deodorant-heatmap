**Score.** `0.30 direct intent + 0.25 unaware intent + 0.30 x (confidence) competition + 0.10 climate + 0.05 regulatory`,
all signals min-max normalised within the country. The competition weight is multiplied by a per-region confidence
factor **C**; the freed weight `0.30 x (1 - C)` is reallocated to the two intent axes, so a region with thin competitor
data is scored almost entirely on search demand. The sidebar weights are renormalised to sum to 1.

**Direct / Unaware intent.** Google Trends interest-by-subregion (12-month, captured 2026-06-15). Each axis is one
combined OR query (a single search item, which avoids the multi-term "shares trap"). Direct = natural / aluminium-free /
refillable / plastic-free deodorant. Unaware = clean beauty / zero waste / plastic free / shampoo bar / low tox.
Resolution is state-level for AU and region-level for NZ; indices are relative share-of-search, directional not absolute.
Intent is winsorised at the 95th percentile so one low-population region cannot dominate the map.

**Competition.** Distribution-intensity of 7 competitor brands (No Pong, Woohoo Body, KIND-LY, Black Chicken, Noosa
Basics, Native, Schmidt's), sourced from where each is actually sold (national chains vs indie home-state). Category
validation (more brands / more presence = category proven) minus saturation (a Herfindahl index; one brand dominating a
region = harder to enter). Confidence C combines brand count, total presence and Trends data-stability Z; regions below
the C threshold are outlined on the map and lean on search intent.

**Climate.** Heat + humidity index (0.6 temperature, 0.4 humidity) from Bureau of Meteorology (AU) and NIWA (NZ) normals,
capital / main-centre proxy. **Regulatory.** Single-use-plastic ban stringency, a minor 0.05 tiebreaker. **Population.**
ABS ERP (Sep 2025) and Stats NZ subnational estimates (2025); shown for context only, deliberately not scored.

**Limitations (read honestly).** A directional portfolio model on free public data, not a precision tool. AU search
intent is high but compressed across states; NZ direct intent is low-volume (several regions sat below Google's
reporting threshold and are imputed low and flagged). The competition layer is a documented distribution proxy, not live
store counts. Low-confidence regions are marked rather than silently trusted.
