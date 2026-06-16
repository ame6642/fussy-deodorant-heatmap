"""
Boundary simplification and choropleth construction for the heatmap.

Uses go.Choroplethmap (MapLibre) with white-bg tiles.
Requires plotly>=5.24,<6 (pinned in requirements.txt).
"""
import plotly.graph_objects as go

COORD_DP = {"AU": 2, "NZ": 3}
DROP_FEATURES = {"Other Territories", "Chatham Islands Territory"}
NAME_FIX = {"Manawatu-Wanganui": "Manawatu-Whanganui"}

_MAP_CENTRE = {
    "AU": {"lat": -27.0, "lon": 134.0},
    "NZ": {"lat": -41.5, "lon": 173.0},
}
_MAP_ZOOM = {"AU": 3.0, "NZ": 4.2}


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
    """geoBoundaries ADM1 FeatureCollection -> light FeatureCollection matching CSVs."""
    nd = COORD_DP[country]
    feats = []
    for f in raw.get("features", []):
        name = f["properties"].get("shapeName", "")
        if name in DROP_FEATURES:
            continue
        region = name.replace(" Region", "")
        region = NAME_FIX.get(region, region)
        feats.append({
            "type": "Feature",
            "properties": {"region": region},
            "geometry": _round_geom(f["geometry"], nd),
        })
    return {"type": "FeatureCollection", "features": feats}


def simplify_geojson_adm2(raw: dict) -> dict:
    """geoBoundaries ADM2 FeatureCollection -> lightweight hover-only layer."""
    nd = 2  # aggressive simplification for sub-region overlay performance
    feats = []
    for f in raw.get("features", []):
        name = f["properties"].get("shapeName", "")
        if not name:
            continue
        geom = _round_geom(f["geometry"], nd)
        if geom["type"] == "Polygon" and not geom["coordinates"]:
            continue
        if geom["type"] == "MultiPolygon" and not geom["coordinates"]:
            continue
        feats.append({
            "type": "Feature",
            "properties": {"name": name},
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": feats}


def make_map(df, gj: dict, title: str, country: str = "AU",
             gj2: dict | None = None, show_low_conf: bool = False) -> go.Figure:
    # customdata cols: tier, direct_norm, unaware_norm, comp_net_norm,
    #                  comp_C, climate_norm, avg_income, population
    cd = df[["tier", "direct_norm", "unaware_norm", "comp_net_norm",
             "comp_C", "climate_norm", "avg_income", "population"]].copy()
    hover = (
        "<b>%{location}</b><br>"
        "Opportunity %{z:.1f}/100  (tier %{customdata[0]})<br>"
        "Direct intent %{customdata[1]:.2f} | Unaware %{customdata[2]:.2f}<br>"
        "Climate %{customdata[5]:.2f} | Avg income $%{customdata[6]:,.0f}<br>"
        "Population %{customdata[7]:,.0f}<extra></extra>"
    )

    centre = _MAP_CENTRE[country]
    zoom = _MAP_ZOOM[country]

    fig = go.Figure(go.Choroplethmap(
        geojson=gj,
        featureidkey="properties.region",
        locations=df["region"],
        z=df["score_100"],
        colorscale="YlOrRd",
        zmin=0, zmax=100,
        marker_line_color="white",
        marker_line_width=0.8,
        colorbar_title="Opportunity",
        colorbar=dict(thickness=15, len=0.6),
        customdata=cd,
        hovertemplate=hover,
    ))

    # Blue outline overlay for low-confidence regions (off by default; competition is context, not scored)
    low = df[df["low_confidence"]]
    if show_low_conf and not low.empty:
        fig.add_trace(go.Choroplethmap(
            geojson=gj,
            featureidkey="properties.region",
            locations=low["region"],
            z=[0] * len(low),
            showscale=False,
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            marker_line_color="#2b6cb0",
            marker_line_width=3.0,
            hoverinfo="skip",
        ))

    # ADM2 sub-region overlay — transparent fill, thin grey border, name-only hover
    if gj2 is not None:
        features = gj2.get("features", [])
        if features:
            names = [f["properties"]["name"] for f in features]
            fig.add_trace(go.Choroplethmap(
                geojson=gj2,
                featureidkey="properties.name",
                locations=names,
                z=[0] * len(names),
                showscale=False,
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                marker_line_color="rgba(60,60,60,0.35)",
                marker_line_width=0.5,
                hovertemplate="<b>%{location}</b><extra></extra>",
                name="",
            ))

    fig.update_layout(
        map_style="white-bg",
        map_center=centre,
        map_zoom=zoom,
        margin=dict(r=0, t=0, l=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=520,
    )
    return fig
