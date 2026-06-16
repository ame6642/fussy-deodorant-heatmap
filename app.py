"""
Natural Deodorant Acquisition Opportunity heatmap.

Interactive Streamlit choropleth ranking Australian states/territories and
New Zealand regions by opportunity score for a natural deodorant brand.

Run:   streamlit run app.py
"""
import os

import pandas as pd
import requests
import streamlit as st

import scoring
import mapviz

HERE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Natural Deodorant Acquisition Opportunity", layout="wide")


@st.cache_data
def load_regions(country: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(HERE, "au_regions.csv" if country == "AU" else "nz_regions.csv"))
    for c in ["direct_intent", "unaware_intent"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


_GEO_API = {
    "AU": "https://www.geoboundaries.org/api/current/gbOpen/AUS/ADM1/",
    "NZ": "https://www.geoboundaries.org/api/current/gbOpen/NZL/ADM1/",
}

_GEO_API_ADM2 = {
    "AU": "https://www.geoboundaries.org/api/current/gbOpen/AUS/ADM2/",
    "NZ": None,  # NZ ADM1 is fine
}


@st.cache_data(show_spinner="Loading region boundaries...")
def load_geojson(country: str) -> dict:
    meta = requests.get(_GEO_API[country], timeout=30).json()
    url = meta["gjDownloadURL"]
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return mapviz.simplify_geojson(r.json(), country)


@st.cache_data(show_spinner="Loading sub-region boundaries...")
def load_geojson_adm2(country: str) -> dict | None:
    api_url = _GEO_API_ADM2.get(country)
    if api_url is None:
        return None
    try:
        meta = requests.get(api_url, timeout=15).json()
        url = meta["gjDownloadURL"]
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return mapviz.simplify_geojson_adm2(r.json())
    except Exception:  # noqa: BLE001
        return None


with st.sidebar:
    st.header("Controls")
    country = st.radio(
        "Market",
        ["AU", "NZ"],
        format_func=lambda c: "Australia" if c == "AU" else "New Zealand",
    )
    st.divider()
    st.subheader("Criteria weights")
    st.caption("Renormalised to sum to 1. Competition is shown as context below, not scored.")
    w_direct = st.slider("Direct category intent", 0.0, 1.0, 0.30, 0.05)
    w_unaware = st.slider("Unaware adjacent intent", 0.0, 1.0, 0.25, 0.05)
    w_climate = st.slider("Climate / sweat", 0.0, 1.0, 0.10, 0.05)
    w_income = st.slider("Average income", 0.0, 1.0, 0.05, 0.05)
    conf_threshold = st.slider("Flag thin competitor data below C =", 0.0, 1.0, 0.40, 0.05)
    weights = {"direct": w_direct, "unaware": w_unaware,
               "climate": w_climate, "income": w_income}

country_name = "Australia" if country == "AU" else "New Zealand"

st.title(f"Natural Deodorant Acquisition Opportunity: {country_name}")
st.caption(
    "Where should a natural deodorant brand concentrate launch marketing? "
    "An opportunity index (0–100), not a raw demand ranking. "
    "Adjust the weights in the sidebar and the map re-ranks."
)

raw = load_regions(country)
if raw["direct_intent"].isna().all() and raw["unaware_intent"].isna().all():
    st.error("Demand data not populated. Run fetch_demand.py and recommit the CSVs.")
    st.stop()

df = scoring.score(raw, weights=weights, conf_threshold=conf_threshold)

try:
    gj = load_geojson(country)
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load region boundaries: {e}")
    st.stop()

missing = sorted(set(df["region"]) - {f["properties"]["region"] for f in gj["features"]})
if missing:
    st.error(f"These regions have no matching map boundary and would be dropped: {missing}")

# Load sub-region (ADM2) boundaries for zoom-in detail layer
gj2 = load_geojson_adm2(country)

# Full-width map
st.plotly_chart(
    mapviz.make_map(df, gj, f"{country_name} opportunity", country=country, gj2=gj2),
    use_container_width=True,
    config={"scrollZoom": True},
    key="main_map",
)
st.caption("Zoom and scroll to see local government area (LGA) boundaries. Competition is excluded from this score and shown as context below.")

# Full-width ranking table below the map
st.subheader("Ranking")
show = df[["rank", "region", "score_100", "tier", "direct_norm",
           "unaware_norm", "climate_norm", "income_norm", "avg_income", "population"]].copy()
for col in ["direct_norm", "unaware_norm", "climate_norm", "income_norm"]:
    show[col] = (show[col] * 100).round(0)
st.dataframe(
    show, hide_index=True, height=400,
    column_config={
        "rank": st.column_config.NumberColumn("#", width="small"),
        "region": "Region",
        "score_100": st.column_config.NumberColumn("Score", format="%.1f"),
        "tier": "Tier",
        "direct_norm": st.column_config.NumberColumn("Direct", format="%d"),
        "unaware_norm": st.column_config.NumberColumn("Unaware", format="%d"),
        "climate_norm": st.column_config.NumberColumn("Climate", format="%d"),
        "income_norm": st.column_config.NumberColumn("Income", format="%d"),
        "avg_income": st.column_config.NumberColumn("Avg Income ($)", format="%d"),
        "population": st.column_config.NumberColumn("Population", format="%d"),
    },
)
st.caption("Component columns are 0-100 normalised within the country. Avg Income and Population are shown raw, for context.")

# --- Competitive landscape (context, not scored) ---
st.subheader("Competitive landscape (context, not scored)")
summ = scoring.competition_summary(df, conf_threshold)
region_word = "states/territories" if country == "AU" else "regions"
if not summ["varies"]:
    verdict = (f"Competition is near-uniform across the {summ['n']} {region_word}: every region stocks "
               f"{summ['b_min']}-{summ['b_max']} of {summ['max_brands']} tracked natural-deodorant brands, total shelf "
               f"presence ranges only {summ['t_min']}-{summ['t_max']} of a possible {summ['max_presence']}, and no single "
               f"brand dominates. Because it barely varies across regions it carries no ranking signal, so it is shown "
               f"here as context and excluded from the opportunity score.")
elif not summ["reliable"]:
    verdict = (f"Competition does vary across the {summ['n']} {region_word}, but the competitor data here is thin and "
               f"low-confidence (median confidence {int(round(summ['median_C'] * 100))}%), so it is shown as context "
               f"and excluded from the opportunity score rather than trusted to rank regions.")
else:
    verdict = (f"Competition varies across the {summ['n']} {region_word} and the data clears the confidence bar, so by "
               f"the inclusion rule it would qualify to enter the score (held as context in this version).")
st.info(verdict + "\n\n**Inclusion rule:** a signal enters the score only if it varies across regions AND clears a "
        "confidence bar. Competition currently fails this in both markets, so it informs strategy, not the rank.")

land = df[["region", "comp_B", "comp_T", "comp_SP", "comp_C", "low_confidence"]].copy()
land = land.sort_values("comp_T", ascending=False)
land["comp_SP"] = (land["comp_SP"] * 100).round(0)
land["comp_C"] = (land["comp_C"] * 100).round(0)
st.dataframe(
    land, hide_index=True, height=360,
    column_config={
        "region": "Region",
        "comp_B": st.column_config.NumberColumn("Brands present (/7)", format="%d"),
        "comp_T": st.column_config.NumberColumn("Shelf presence (/21)", format="%d"),
        "comp_SP": st.column_config.NumberColumn("Concentration", format="%d"),
        "comp_C": st.column_config.NumberColumn("Data confidence", format="%d"),
        "low_confidence": st.column_config.CheckboxColumn("Thin data"),
    },
)
st.caption("Competitor presence is a documented distribution proxy (national chains vs indie home-state), not live "
           "store counts. Concentration is a 0-100 Herfindahl index (higher = more dominated by one brand). This is "
           "the layer that would benefit most from paid stockist data.")

with st.expander("Methodology, data sources and limitations"):
    _m = os.path.join(HERE, "methodology.md")
    st.markdown(open(_m, encoding="utf-8").read() if os.path.exists(_m) else "See README.md for methodology.")
