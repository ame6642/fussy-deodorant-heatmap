"""
Boundary simplification and choropleth construction for the heatmap.

Kept free of Streamlit so the geometry/name-matching logic (where the brief's
'silent region drop' bug lives) can be unit-tested without a browser. app.py
wraps load step with st.cache_data and the geoBoundaries fetch.
"""
import plotly.graph_objects as go

# geoBoundaries ADM1, pinned to commit 9469f09, served from the Git-LFS media host.
GEO_URLS = {
    "AU": "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/AUS/ADM1/geoBoundaries-AUS-ADM1_simplified.geojson",
    "NZ": "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/NZL/ADM1/geoBoundaries-NZL-ADM1_simplified.geojson",
}
COORD_DP = {"AU": 1, "NZ": 2}          # AU states are large -> coarser rounding is fine
DROP_FEATURES = {"Other Territories", "Chatham Islands Territory"}
NAME_FIX = {"Manawatu-Wanganui": "Manawatu-Whanganui"}


def _round_ring(ring, nd):
    out, last = [], None
    for p in ring:
        q = [round(p[0], nd), round(p[1], nd)]
        if q != last:
            out.append(q)
            last = q
    if out and out[0] != out[-1]:
        out.append(out[0])
    return out


def _round_geom(g, nd):
    t = g["type"]
    if t == "Polygon":
        rings = [r for r in (_round_ring(r, nd) for r in g["coordinates"]) if len(r) >= 4]
        return {"type": t, "coordinates": rings}
    if t == "MultiPolygon":
        polys = []
        for poly in g["coordinates"]:
            rings = [r for r in (_round_ring(r, nd) for r in poly) if len(r) >= 4]
            if rings:
                polys.append(rings)
        return {"type": t, "coordinates": polys}
    return g


def simplify_geojson(raw: dict, country: str) -> dict:
    """geoBoundaries -> light FeatureCollection with properties.region matching the CSVs."""
    nd = COORD_DP[country]
    feats = []
    for f in raw.get("features", []):
        name = f["properties"].get("shapeName", "")
        if name in DROP_FEATURES:
            continue
        region = name.replace(" Region", "")
        region = NAME_FIX.get(region, region)
        feats.append({"type": "Feature",
                      "properties": {"region": region},
                      "geometry": _round_geom(f["geometry"], nd)})
    return {"type": "FeatureCollection", "features": feats}


def make_map(df, gj: dict, title: str) -> go.Figure:
    cd = df[["tier", "direct_norm", "unaware_norm", "comp_net_norm",
             "comp_C", "climate_norm", "regulatory_norm", "population"]].copy()
    hover = ("<b>%{location}</b><br>"
             "Opportunity %{z:.1f}/100  (tier %{customdata[0]})<br>"
             "Direct intent %{customdata[1]:.2f} | Unaware %{customdata[2]:.2f}<br>"
             "Competition %{customdata[3]:.2f} (confidence %{customdata[4]:.2f})<br>"
             "Climate %{customdata[5]:.2f} | Regulatory %{customdata[6]:.2f}<br>"
             "Population %{customdata[7]:,.0f}<extra></extra>")
    fig = go.Figure(go.Choropleth(
        geojson=gj, featureidkey="properties.region",
        locations=df["region"], z=df["score_100"],
        colorscale="YlOrRd", zmin=0, zmax=100,
        marker_line_color="white", marker_line_width=0.6,
        colorbar_title="Opportunity", customdata=cd, hovertemplate=hover,
    ))
    low = df[df["low_confidence"]]
    if not low.empty:
        fig.add_trace(go.Choropleth(
            geojson=gj, featureidkey="properties.region",
            locations=low["region"], z=[0] * len(low), showscale=False,
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            marker_line_color="#2b6cb0", marker_line_width=3.0, hoverinfo="skip",
        ))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=title, margin=dict(l=0, r=0, t=40, b=0), height=560)
    return fig
