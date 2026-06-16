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
        meta = requests.get(api_url, timeout=30).json()
        url = meta["gjDownloadURL"]
        r = requests.get(url, timeout=120)
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
    st.caption("Renormalised to sum to 1.")
    w_direct = st.slider("Direct category intent", 0.0, 1.0, 0.30, 0.05)
    w_unaware = st.slider("Unaware adjacent intent", 0.0, 1.0, 0.25, 0.05)
    w_comp = st.slider("Competition (confidence-gated)", 0.0, 1.0, 0.30, 0.05)
    w_climate = st.slider("Climate / sweat", 0.0, 1.0, 0.10, 0.05)
    w_income = st.slider("Average income", 0.0, 1.0, 0.05, 0.05)
    conf_threshold = st.slider("Low-confidence flag below C =", 0.0, 1.0, 0.40, 0.05)
    weights = {"direct": w_direct, "unaware": w_unaware, "competition": w_comp,
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
)
st.caption("Thick blue outline = low confidence (thin competitor data; score leans on search intent). Zoom in to see local government area boundaries.")

# Full-width ranking table below the map
st.subheader("Ranking")
show = df[["rank", "region", "score_100", "tier", "low_confidence", "direct_norm",
           "unaware_norm", "comp_net_norm", "comp_C", "climate_norm", "avg_income", "population"]].copy()
for col in ["direct_norm", "unaware_norm", "comp_net_norm", "comp_C", "climate_norm"]:
    show[col] = (show[col] * 100).round(0)
st.dataframe(
    show, hide_index=True, height=400,
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
        "avg_income": st.column_config.NumberColumn("Avg Income ($)", format="%d"),
        "population": st.column_config.NumberColumn("Population", format="%d"),
    },
)
st.caption("Component columns are 0–100 normalised within the country. Avg Income and Population are context, not normalised here.")

with st.expander("Methodology, data sources and limitations"):
    _m = os.path.join(HERE, "methodology.md")
    st.markdown(open(_m, encoding="utf-8").read() if os.path.exists(_m) else "See README.md for methodology.")
