"""
Fussy AU + NZ deodorant acquisition heatmap.

Interactive Streamlit choropleth that ranks Australian states/territories and
New Zealand regions by opportunity score for a premium / natural ("fussy")
deodorant brand: live search intent (Google Trends), a confidence-gated
competition layer, climate and regulatory signals. Adjust the sidebar weights
and both the map and the ranking table update.

Run:   streamlit run app.py
"""
import json
import os

import pandas as pd
import requests
import streamlit as st

import scoring
import mapviz

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "geojson_cache")

st.set_page_config(page_title="Fussy AU/NZ deodorant heatmap", layout="wide")


@st.cache_data
def load_regions(country: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(HERE, "au_regions.csv" if country == "AU" else "nz_regions.csv"))
    for c in ["direct_intent", "unaware_intent"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data(show_spinner="Loading region boundaries...")
def load_geojson(country: str) -> dict:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"{country}.geojson")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    r = requests.get(mapviz.GEO_URLS[country], timeout=60)
    r.raise_for_status()
    gj = mapviz.simplify_geojson(r.json(), country)
    try:
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(gj, f)
    except OSError:
        pass  # read-only/ephemeral host FS -> rely on st.cache_data in-memory cache
    return gj


st.title("Fussy - Australia & New Zealand acquisition heatmap")
st.caption("Where should a premium / natural deodorant brand concentrate launch marketing? "
           "An opportunity index (0-100), not a raw demand ranking. Adjust the weights and the map re-ranks.")

with st.sidebar:
    st.header("Criteria weights")
    st.caption("Defaults follow the agreed model; renormalised to sum to 1.")
    w_direct = st.slider("Direct category intent", 0.0, 1.0, 0.30, 0.05)
    w_unaware = st.slider("Unaware adjacent intent", 0.0, 1.0, 0.25, 0.05)
    w_comp = st.slider("Competition (confidence-gated)", 0.0, 1.0, 0.30, 0.05)
    w_climate = st.slider("Climate / sweat", 0.0, 1.0, 0.10, 0.05)
    w_reg = st.slider("Sustainability / regulatory", 0.0, 1.0, 0.05, 0.05)
    conf_threshold = st.slider("Low-confidence flag below C =", 0.0, 1.0, 0.40, 0.05)
    weights = {"direct": w_direct, "unaware": w_unaware, "competition": w_comp,
               "climate": w_climate, "regulatory": w_reg}

country = st.radio("Market", ["AU", "NZ"], horizontal=True,
                   format_func=lambda c: "Australia" if c == "AU" else "New Zealand")

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

left, right = st.columns([1.05, 1.0])
with left:
    st.plotly_chart(
        mapviz.make_map(df, gj, f"{'Australia' if country == 'AU' else 'New Zealand'} opportunity"),
        width="stretch")
    st.caption("Thick blue outline = low confidence (thin competitor data; score leans on search intent).")

with right:
    st.subheader("Ranking")
    show = df[["rank", "region", "score_100", "tier", "low_confidence", "direct_norm",
               "unaware_norm", "comp_net_norm", "comp_C", "climate_norm", "regulatory_norm", "population"]].copy()
    for c in ["direct_norm", "unaware_norm", "comp_net_norm", "comp_C", "climate_norm", "regulatory_norm"]:
        show[c] = (show[c] * 100).round(0)
    st.dataframe(
        show, hide_index=True, height=560,
        column_config={
            "rank": st.column_config.NumberColumn("#", width="small"),
            "region": "Region",
            "score_100": st.column_config.NumberColumn("Score", format="%.1f"),
            "tier": "Tier",
            "low_confidence": st.column_config.CheckboxColumn("Low conf."),
            "direct_norm": st.column_config.NumberColumn("Direct", format="%d"),
            "unaware_norm": st.column_config.NumberColumn("Unaware", format="%d"),
            "comp_net_norm": st.column_config.NumberColumn("Compet.", format="%d"),
            "comp_C": st.column_config.NumberColumn("Conf.", format="%d"),
            "climate_norm": st.column_config.NumberColumn("Climate", format="%d"),
            "regulatory_norm": st.column_config.NumberColumn("Reg.", format="%d"),
            "population": st.column_config.NumberColumn("Population", format="%d"),
        },
    )
    st.caption("Component columns are 0-100 normalised within the country. Population is context, not scored.")

if country == "AU":
    st.info('Live validation: "fussy natural deodorant" is currently a breakout rising query in Australian '
            "Google Trends, evidence the brand is already generating branded demand in-market.")

with st.expander("Methodology, data sources and limitations"):
    _m = os.path.join(HERE, "methodology.md")
    st.markdown(open(_m, encoding="utf-8").read() if os.path.exists(_m) else "See README.md for methodology.")
