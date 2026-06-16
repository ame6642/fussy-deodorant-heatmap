**Score.** `direct intent + unaware intent + climate + income`, all signals min-max normalised within the
country, with the sidebar weights renormalised to sum to 1. Default weights: direct 0.30, unaware 0.25,
climate 0.10, income 0.05. Competition is deliberately NOT in the score (see below).

**Direct / Unaware intent.** Google Trends interest-by-subregion (12-month, captured 2026-06-15). Each axis is
one combined OR query (a single search item, which avoids the multi-term "shares trap"). Direct = natural /
aluminium-free / refillable / plastic-free deodorant. Unaware = clean beauty / zero waste / plastic free /
shampoo bar / low tox. Resolution is state-level for AU and region-level for NZ; indices are relative
share-of-search, directional not absolute. Intent is winsorised at the 95th percentile so one low-population
region cannot dominate the map.

**Competition (context, not scored).** Distribution-intensity of 7 competitor brands (No Pong, Woohoo Body,
KIND-LY, Black Chicken, Noosa Basics, Native, Schmidt's), sourced from where each is actually sold (national
chains vs indie home-state), turned into category validation (more brands and presence = category proven) minus
saturation (a Herfindahl index; one brand dominating a region = harder to enter). It is excluded from the
opportunity score under a simple inclusion rule: a signal earns a place in the ranking only if it varies across
the regions AND is reliable enough to trust. In Australia competition is near-uniform (every state stocks most
brands; total shelf presence 10-12 of a possible 21; no regional monopoly), so min-max normalising it would
manufacture false differentiation. In New Zealand it varies more, but the competitor data is thin and
low-confidence. So competition is presented as a competitive-landscape layer (brands present, shelf presence,
concentration, data confidence) rather than a score input. It is the layer that would benefit most from paid
stockist data.

**Climate.** Heat + humidity index (0.6 temperature, 0.4 humidity) from Bureau of Meteorology (AU) and NIWA (NZ)
normals, capital / main-centre proxy. **Income.** Average household income (ABS / Stats NZ), normalised within
country, a proxy for ability to pay for a premium product. **Population.** ABS ERP (Sep 2025) and Stats NZ
subnational estimates (2025); shown for context only, deliberately not scored.

**Limitations (read honestly).** A directional portfolio model on free public data, not a precision tool. AU
search intent is high but compressed across states; NZ direct intent is low-volume (several regions sat below
Google's reporting threshold and are imputed low). The score is a relative, per-capita-style index across
regions, not a probability or a customer count, so the headline number is best read as a tier, not a precise
rank. Competition is a documented distribution proxy, not live store counts, and is shown as context rather
than scored.
