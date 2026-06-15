"""
Opportunity scoring for the Fussy AU/NZ deodorant heatmap.

Pure pandas, no Streamlit, so it can be unit-tested without a browser or the app.
Implements the handoff-brief model with the confidence gate:

    Opportunity = w_direct * direct_intent_norm
                + w_unaware * unaware_intent_norm
                + (w_comp * C) * competition_net_norm
                + w_climate * climate_norm
                + w_reg * regulatory_norm

    where the freed competition weight  w_comp * (1 - C)  is reallocated pro-rata
    to the two intent axes, so the five effective weights always sum to 1 in every
    region. C is the per-region confidence in the competition data.

All signals are min-max normalised WITHIN a country (AU and NZ are separate maps
and separate rankings, and Google Trends indices are already country-relative).
Intent axes are winsorised at the 95th percentile before normalising so a single
low-population region cannot dominate the map.
"""
import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "direct": 0.30, "unaware": 0.25, "competition": 0.30, "climate": 0.10, "regulatory": 0.05,
}
BRAND_COLS = ["s_nopong", "s_woohoo", "s_kindly", "s_blackchicken", "s_noosa", "s_native", "s_schmidts"]
CONF_THRESHOLD = 0.40


def norm(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(0.5, index=s.index)        # no spread -> neutral
    return (s - lo) / (hi - lo)


def norm_robust(s: pd.Series, q: float = 0.95) -> pd.Series:
    """Winsorise at the q-th percentile, then min-max normalise. NaN-safe."""
    s = pd.to_numeric(s, errors="coerce")
    cap = s.quantile(q)
    if pd.isna(cap) or cap == 0:
        return norm(s).fillna(0.0)
    return norm(s.clip(upper=cap)).fillna(0.0)


def _competition(df: pd.DataFrame) -> pd.DataFrame:
    """Brief's competition method from the per-brand presence columns + Z."""
    out = pd.DataFrame(index=df.index)
    presence = df[BRAND_COLS].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    T = presence.sum(axis=1)                         # total presence
    B = (presence > 0).sum(axis=1)                   # distinct brands present
    out["comp_T"], out["comp_B"] = T, B

    # category validation: proven where more brands AND more presence
    CV = (norm(B) + norm(T)) / 2.0
    # saturation via Herfindahl concentration; one brand owning a region is bad
    def sat(row):
        t = row.sum()
        b = int((row > 0).sum())
        if t == 0 or b == 0:
            return 0.0
        if b == 1:
            return 1.0                               # single brand = maximal concentration
        hhi = float(((row / t) ** 2).sum())
        return (hhi - 1.0 / b) / (1.0 - 1.0 / b)
    SP = presence.apply(sat, axis=1)
    out["comp_CV"], out["comp_SP"] = CV, SP
    out["comp_net"] = CV - SP

    Z = pd.to_numeric(df["z_stability"], errors="coerce").fillna(0.0)
    C = (np.minimum(T / 5.0, 1.0) + np.minimum(B / 3.0, 1.0) + Z) / 3.0
    out["comp_C"] = C
    out["comp_net_norm"] = norm(out["comp_net"]).fillna(0.0)
    return out


def score(df: pd.DataFrame, weights: dict | None = None,
          conf_threshold: float = CONF_THRESHOLD) -> pd.DataFrame:
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)
    total = sum(w.values()) or 1.0
    w = {k: v / total for k, v in w.items()}          # renormalise to sum 1

    df = df.copy()
    # --- normalise the non-competition signals (within this country) ---
    df["direct_norm"] = norm_robust(df["direct_intent"])
    df["unaware_norm"] = norm_robust(df["unaware_intent"])
    df["climate_norm"] = 0.6 * norm(df["temp_c"]) + 0.4 * norm(df["humidity_pct"])
    df["regulatory_norm"] = norm(df["regulatory_raw"])

    comp = _competition(df)
    df = pd.concat([df, comp], axis=1)

    # --- confidence-gated weights, per region ---
    C = df["comp_C"].clip(0, 1)
    eff_comp = w["competition"] * C
    freed = w["competition"] * (1.0 - C)
    intent_base = w["direct"] + w["unaware"]
    if intent_base > 0:
        wd = w["direct"] + freed * (w["direct"] / intent_base)
        wu = w["unaware"] + freed * (w["unaware"] / intent_base)
        w_comp_eff = eff_comp
    else:
        # user zeroed both intent axes -> nowhere to reallocate; keep weight on competition
        wd = pd.Series(0.0, index=df.index)
        wu = pd.Series(0.0, index=df.index)
        w_comp_eff = eff_comp + freed

    df["w_direct_eff"], df["w_unaware_eff"], df["w_comp_eff"] = wd, wu, w_comp_eff
    df["score"] = (wd * df["direct_norm"]
                   + wu * df["unaware_norm"]
                   + w_comp_eff * df["comp_net_norm"]
                   + w["climate"] * df["climate_norm"]
                   + w["regulatory"] * df["regulatory_norm"])
    df["score_100"] = (df["score"] * 100).round(1)
    df["low_confidence"] = df["comp_C"] < conf_threshold

    # A/B/C tiers within country (by score tertiles)
    try:
        df["tier"] = pd.qcut(df["score"], 3, labels=["C", "B", "A"]).astype(str)
    except ValueError:
        df["tier"] = "B"
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df
