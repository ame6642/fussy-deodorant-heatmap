# HANDOFF BRIEF — Fussy Heatmap & Related Brand Work

---

## PURPOSE & SCOPE

Amman is targeting a strategy / biz ops / founder's associate role at a small London startup as pre-consulting experience. He is building standalone, public-data tools for small consumer brands to demonstrate commercial value and use in cold outreach. Three brands are in scope:

- **Hello Klean** (filtered showerheads, London): building a UK geo-targeted acquisition heatmap driven by water hardness. A Canada/NA version is planned and can be shown to Canopy directly.
- **Canopy** (filtered showerheads + humidifiers, US): the NA heatmap from the Hello Klean work is a direct fit and can be shown to them without a separate build.
- **Fussy** (refillable natural deodorant, London): the active build. An acquisition heatmap for Australia and New Zealand, built entirely in Cowork with no manual steps and no code.

The three artefacts form a matched set demonstrating the same analytical capability across different brands and markets.

---

## COMPLETED WORK

### Brand research: Fussy

- **What they do:** Refillable natural deodorant. Plastic-free, compostable refills made from waste sugarcane, letterbox-delivered on subscription, paired with a durable reusable case. Aluminium-free, vegan, probiotic. Multiple scents and case colours. Founded 2020 by Matt Kennedy (CEO) and Eddie Fisher.
- **Headcount:** 19 employees (PitchBook confirmed, pitchbook.com/profiles/company/462299-41). Under 20.
- **Run rate:** in excess of £30m annual run rate at end of August 2025 (dunelmpartners.co.uk/fussy/).
- **Funding:** ~$16.6m total. Seed 2022. Backers include Dunelm Partners, Guinness Ventures, Velocity Capital, Deborah Meaden, and Peter Jones (Dragons' Den 2022).
- **Distribution:** UK retail in Tesco, Sainsbury's, Waitrose, Boots, Urban Outfitters, Amazon. Continental Europe ~15% of revenue (newly entered). **Australia recently launched. US and NZ on the roadmap.**
- **Product expansion:** September 2025 launch of a refillable natural body wash in plastic-free packaging, signalling a move from single-product to a broader plastic-free bathroom range.
- **Critical operational quirk:** Fussy's UK model depends on letterbox-sized, post-delivered compostable refills. This works in markets with similar postal/letterbox infrastructure and may need rethinking in the US (different mailbox formats and mail economics). This is a genuine market-entry constraint that a generic model misses.

### Why AU/NZ was chosen as the target market

- Australia recently launched, making it live and high-stakes.
- New Zealand is adjacent and likely next.
- Both markets have state/regional government data, Google Trends works at region level, and competitor presence is researched at region level.
- Geography is coarser than the US (8 Australian states/territories, 16 NZ regions), which means the choropleth will be chunkier but data is cleaner per unit.

### Core strategic insight (must carry through)

Fussy has no hard physical signal analogous to Hello Klean's water hardness. Deodorant works everywhere. The heatmap must therefore lead with **category search intent** (hard, measurable) and treat sustainability proxies as supporting context. Being honest about this softness when presenting is what keeps the artefact credible.

However, one hard signal is available and has been added: **climate and humidity**. Northern Australia is tropical, the south is temperate. Hotter, more humid regions drive higher deodorant usage intensity. This is the AU-specific hard axis the US map lacked and it has been incorporated.

### Build decision: Cowork entirely, no manual steps, no code

The entire build is automated via Cowork driving desktop applications. No Python scripts, no APIs, no manual research. Cowork handles:
1. Data collection via browser automation (Google Trends UI, competitor store finders, government sites).
2. Populating a structured Google Sheet with pre-built normalisation and weighting formulas.
3. Exporting and uploading to Datawrapper or Flourish to render the choropleth.

### Heatmap model — full specification

#### Geographic unit
Australian states and territories (8): NSW, VIC, QLD, SA, WA, TAS, ACT, NT.
NZ regions (16): Auckland, Wellington, Canterbury, Waikato, Bay of Plenty, Manawatu-Whanganui, Otago, Hawke's Bay, Tasman, Northland, Marlborough, Taranaki, Southland, Gisborne, Nelson, West Coast.

#### Composite score formula
`Opportunity = (0.30 × direct_intent_norm) + (0.25 × unaware_intent_norm) + (0.30 × C × competition_net) + (0.10 × climate_norm) + (0.05 × regulatory_norm)`

Where competition weight is gated by confidence C (see below), and freed weight is reallocated to intent axes.

#### Final weights

| Axis | Sub-component | Weight |
|---|---|---|
| Direct category intent | People searching for natural/refillable/aluminium-free deodorant | 0.30 |
| Unaware adjacent audience intent | People buying natural products who may not know natural deodorant exists | 0.25 |
| Competition / market reception | Category validation minus saturation difficulty, gated by confidence | 0.30 |
| Climate / deodorant usage intensity | Heat and humidity index | 0.10 |
| Sustainability / regulatory tailwind | Plastic regulation, recycling rates, organic spend | 0.05 |
| **Total** | | **1.00** |

**Key rationale for weights:**
- Intent axes carry 0.55 combined because revealed demand is the best proxy for product-customer fit in a newly entered market.
- Competition carries 0.30 because it answers whether the market is proven and contestable, but this weight is variable via the confidence gate (see below).
- Climate at 0.10 is intentionally kept low to avoid the map being pulled toward sparsely populated tropical regions (NT, far north QLD) where raw need is high but market size is thin.
- Sustainability / regulatory at 0.05 is intentionally low. This was debated and deliberately reduced from 0.15. The reasoning: single-use plastic regulation is a structural backdrop, not a driver of individual purchase decisions. Product-customer fit is what converts. Regulation has a real second-order effect (raising competitor costs, priming cultural conversation) but should be a minor tiebreaker only.

**All weights stay as adjustable parameters** so Fussy can re-run with different splits.

#### Direct category intent keyword set
- natural deodorant
- refillable deodorant
- aluminium free deodorant
- natural deodorant australia (and NZ variant)
- plastic free deodorant
- compostable deodorant
- zero waste deodorant
- deodorant without aluminium
- best natural deodorant

#### Unaware adjacent audience keyword set (full list, AU/NZ English, British spelling)

**Adjacent natural bodycare and skincare:**
- natural body wash
- plastic free body wash
- natural soap
- plastic free soap
- natural moisturiser
- clean beauty
- natural skincare
- organic skincare
- zero waste beauty

**Adjacent natural haircare:**
- shampoo bar
- conditioner bar
- plastic free shampoo
- zero waste shampoo
- natural haircare
- sustainable haircare

**Zero-waste and plastic-free lifestyle:**
- zero waste products
- zero waste swaps
- plastic free bathroom
- plastic free living
- plastic free swaps
- refillable products
- reusable products
- compostable packaging
- sustainable living
- eco friendly products

**Health and ingredient concern (added after discussion — people moving away from industrial/artificial products):**
- microplastics
- toxin free
- non toxic deodorant
- chemical free deodorant
- paraben free
- sulphate free
- fragrance free
- all natural products
- clean ingredients
- no nasties
- what's in my deodorant
- is aluminium deodorant safe
- natural alternatives
- low tox
- low tox living

**Values and ethics:**
- aluminium free
- vegan beauty
- cruelty free beauty
- reef safe products

**AU/NZ-specific cultural signals (high priority, these are what a generic build misses):**
- plastic free july (founded in Western Australia, strong local signal)
- war on waste (ABC programme that drove Australian anti-plastic sentiment)
- reef safe sunscreen (proxy for Great Barrier Reef-driven eco-consciousness)
- boomerang bags

**Note on cultural signals:** check volume before relying on them. Plastic Free July and War on Waste are seasonal. Drop any that return too sparse at region level.

#### Competition scoring — revised method (full specification)

This was extensively debated and redesigned. The key insight: treating "less contested" as automatically better was wrong. In a nascent category, competitor presence is also a signal of validated demand. A region where multiple natural deodorant brands have traction has proven it will buy the category. A region with no competitors may be empty because the product was tried and rejected, not because it is virgin territory.

**Inputs collected per region (all via Cowork browser automation):**
- S_b = stockist count for each competitor brand b, pulled from each brand's store-finder
- B = number of distinct competitor brands with at least one stockist in the region
- T = total competitor stockists in the region (sum of S_b)
- Z = Google Trends data stability (1 minus the proportion of zero-data weeks for the direct category terms)

**Competitor brands to collect:** No Pong, Woohoo Body, KIND-LY, Black Chicken Remedies Axilla, Noosa Basics, Native, Schmidt's. (All AU/NZ-relevant natural deodorant competitors.)

**Component 1: Category validation CV (positive, more is better)**
Proves the category sells in that region.
- Normalise B and T across all regions (0 to 1)
- CV = mean(B_norm, T_norm)

**Component 2: Saturation difficulty SP (negative, less is better)**
Captures whether one incumbent owns the region. Uses a Herfindahl-style concentration index.
- For each brand: share_b = S_b / T
- HHI = Σ (share_b)²
- SP = (HHI − 1/B) / (1 − 1/B) when B > 1
- SP = 1 when B = 1 (single brand = maximal concentration)

**Net competition score:** CV − SP
A region high on validation and low on saturation scores best. An empty market scores low on CV. A monopolised market scores low via high SP. This is the correct resolution to the original flaw.

**Component 3: Confidence factor C (gates everything)**
Measures whether there is enough data to trust the competition scores.
- C = mean(min(T/5, 1), min(B/3, 1), Z)
- C ranges 0 to 1
- **Any region with C < 0.4 is flagged low-confidence** and visually marked on the map (e.g. hatched fill)

**Confidence gate on weighting:**
- Effective competition weight = 0.30 × C
- Freed weight = 0.30 × (1 − C), reallocated pro-rata to the two intent axes
- Result: high-confidence regions are scored with the full competition signal; low-confidence regions are scored almost entirely on search intent

**In plain English:** the model counts how many natural deodorant brands are stocked in each region and how evenly spread they are, rewarding regions where demand is proven but no single brand dominates. It checks how reliable that data is, and for regions without enough information it automatically falls back to search intent as the primary signal. A healthy competitive region scores higher than an empty one, a monopolised region scores lower than a contested one, and thin-data regions are visually flagged rather than silently misjudged.

**Thresholds (tunable once real data comes in):**
- T ≥ 5 for a meaningful HHI (Australian/NZ stockist counts may run lower than expected, so this may need loosening)
- C < 0.4 for the low-confidence flag

#### Climate and humidity layer
- Source: Bureau of Meteorology (AU) and NIWA (NZ) climate data, automatable via Cowork.
- Metric: mean annual temperature and mean relative humidity by region, composited into a single heat-humidity index.
- Normalise 0 to 1 across all regions.
- Weight intentionally low (0.10) to avoid the map being dominated by sparsely populated tropical regions.

#### Sustainability and regulatory layer
- Source: state government environment sites, NZ Ministry for the Environment, recycling rate databases.
- Metric: single-use plastic regulation stringency (SA, WA, and QLD are ahead in Australia) plus recycling rates and organic/sustainable spend proxies.
- Weight: 0.05 (deliberately low, reduced from 0.15 after debate. Regulation is a structural backdrop, not a purchase driver).

#### Visualisation
- Tool: Datawrapper or Flourish (both browser-based, driveable by Cowork).
- Output: interactive choropleth, one map for AU and one for NZ, or combined if the data allows.
- Visual flag for low-confidence regions: hatched fill or greyed-out border.
- Hover detail: composite score plus individual component scores for each region.
- Note alongside the map: NSW and Victoria will dominate any absolute view because Sydney and Melbourne hold most of the population. The map is an opportunity index, not a raw demand ranking.

---

## CONSTRAINTS & RULES

### Writing style (for any written output or outreach)
- No em dashes, ever. Use commas, parentheses, or separate sentences.
- No AI tropes or telltale punctuation patterns.
- Brief, concise, report-style, neutral technical tone. Task-relevant only.
- Deep-cut specific research that explains significance, not surface-level observation.

### Coding and build guidelines (from CLAUDE.md)
1. State assumptions before implementing; surface tradeoffs; ask if unclear.
2. Minimum code; no speculative features or unnecessary abstractions.
3. Surgical edits only; do not touch adjacent code.
4. Define success criteria and verify each step.

### Build constraints (Fussy-specific)
- Cowork only. No Python scripts, no APIs, no manual steps.
- Public data only; no Fussy internal data required.
- Reconcile every figure against source headline numbers before sharing. Unit mismatches have been the single biggest recurring error in prior builds (remittances off by 1,000,000 in nSave model; quit rate inflated 17x in Stepful model).
- Check the company's existing tools and site before building anything to avoid duplicating what already exists.

### Recurring failure modes to avoid
- Unit mismatches in live data (reconcile against source headlines).
- Building for a problem that does not exist (check existing tools first).
- Manufacturing analysis not supported by source material.
- Overclaiming the soft values axis as a hard predictor. For Fussy: lead with search intent, treat sustainability as supporting context.
- Assigning misleadingly clean scores to thin-data regions. Use the confidence gate.

---

## OPEN ITEMS & PENDING DECISIONS

1. **Confirm whether NZ is included in the build or deferred.** NZ is on the roadmap but not launched yet. Including it is useful for forward planning; excluding it keeps the build focused. Not yet decided.
2. **Confirm Fussy brand palette** for the choropleth colour scheme (pull from getfussy.com before building the visualisation layer).
3. **Confirm Fussy leadership names and current headcount** via LinkedIn before any outreach. PitchBook says 19; verify.
4. **Thresholds for the confidence gate** (T ≥ 5, B ≥ 3, C < 0.4) are provisional. They should be reviewed once the real competitor stockist data comes in, since AU/NZ regional counts may run lower than the defaults assume.
5. **Cultural search terms validation:** Plastic Free July and War on Waste are seasonal and may return sparse at region level. Check volume before including them in the composite.
6. **Google Trends resolution:** Cowork will pull from the Google Trends browser UI. Confirm that region-level data is available for the 8 AU states and 16 NZ regions at sufficient granularity before building the full keyword set run. If resolution is too coarse, fall back to city-level and aggregate up.
7. **Competitor store-finder automation:** confirm each brand's store-finder is scrapeable by Cowork (some use JavaScript rendering that may resist standard browser automation). If any break, flag and handle manually as a one-off or drop that brand from the competition layer.
8. **No written outreach or cover letter for Fussy has been drafted yet.** This is the next written deliverable after the map is built.

---

## NEXT ACTIONS (prioritised)

1. **Decide NZ inclusion** before starting the build. It affects the geographic unit setup and the boundary files needed for the choropleth.
2. **Pull Fussy brand palette** from getfussy.com. Needed before the visualisation step.
3. **Run the Google Trends pull first, in isolation.** Check that region-level data returns for the AU states (and NZ regions if included) for both the direct category terms and a sample of the unaware audience terms. This is the viability check for the entire intent layer.
4. **Run the competitor store-finder collection second, in isolation.** Pull stockist counts for all 7 competitor brands across all regions. Check that Cowork can navigate each store-finder successfully. Compute B, T, and Z, and check whether the confidence factor C comes back above 0.4 for enough regions to make the competition axis meaningful.
5. **Collect climate and regulatory data** via Cowork from Bureau of Meteorology, NIWA, and state government environment sites.
6. **Populate the Google Sheet** with all four datasets, normalise, apply the composite formula with the confidence gate, and compute the opportunity score per region.
7. **Upload to Datawrapper or Flourish** and render the choropleth. Mark low-confidence regions visually.
8. **Audit every figure** against source headline data before sharing. Spot-check 3 regions against raw source for each data layer.
9. **Draft the outreach note** for Fussy: what the map shows, how they would action it (where to concentrate AU launch spend, which regions have the strongest proven demand), and the two-sentence pitch for the artefact. The actionable interpretation is what makes it land, not the map itself.
10. **Verify Fussy leadership and headcount on LinkedIn** before sending any outreach.
