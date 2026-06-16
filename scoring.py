"""
Opportunity scoring for the AU/NZ natural-deodorant heatmap.

Pure pandas, no Streamlit, so it can be unit-tested without a browser or the app.

    Opportunity = w_direct * direct_intent_norm
                + w_unaware * unaware_intent_norm
                + w_climate * climate_norm
                + w_income  * income_norm        (weights renormalised to sum to 1)

Competition is DELIBERATELY NOT in the score. It is computed and exposed as a
competitive-landscape context layer (see competition_summary), because a signal
should only enter a ranking when it (a) varies across the regions being ranked
and (b) is reliable enough to trust. In both AU and NZ today competition fails
that test: in AU it is near-uniform (every state stocks most brands), and in NZ
it varies but the data is thin and low-confidence. Min-max normalising a
near-constant manufactures false spread, so competition is shown as context
instead. The rule is stated, not hard-coded into the score.

All signals are min-max normalised WITHIN a country (AU and NZ are separate maps
and rankings, and Google Trends indices are already country-relative). Intent
axes are winsorised at the 95th percentile so one low-population region cannot
dominate the map.
"""
import numpy as np
import pandas as pd

SCORING_KEYS = ["direct", "unaware", "climate", "income"]
DEFAULT_WEIGHTS = {"direct": 0.30, "unaware": 0.25, "climate": 0.10, "income": 0.05}
BRAND_COLS = ["s_nopong", "s_woohoo", "s_kindly", "s_blackchicken", "s_noosa", "s_native", "s_schmidts"]
CONF_THRESHOLD = 0.40
VARIES_CV_MIN = 0.15          # coefficient of variation of shelf presence to call competition "varying"
MAX_BRANDS = 7
MAX_PRESENCE = 21             # 7 brands x max intensity 3


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
    """Competitor presence diagnostics from the per-brand presence columns + Z.
    Computed for the competitive-landscape context layer only; not scored."""
    out = pd.DataFrame(index=df.index)
    presence = df[BRAND_COLS].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    T = presence.sum(axis=1)                         # total shelf presence (0-21)
    B = (presence > 0).sum(axis=1)                   # distinct brands present (0-7)
    out["comp_T"], out["comp_B"] = T, B

    CV = (norm(B) + norm(T)) / 2.0                   # category validation (more = proven)

    def sat(row):                                    # saturation via Herfindahl concentration
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
    out["comp_C"] = (np.minimum(T / 5.0, 1.0) + np.minimum(B / 3.0, 1.0) + Z) / 3.0
    out["comp_net_norm"] = norm(out["comp_net"]).fillna(0.0)
    return out


def score(df: pd.DataFrame, weights: dict | None = None,
          conf_threshold: float = CONF_THRESHOLD) -> pd.DataFrame:
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        for k in SCORING_KEYS:                       # ignore any non-scoring keys (e.g. legacy "competition")
            if k in weights:
                w[k] = weights[k]
    total = sum(w.values()) or 1.0
    w = {k: v / total for k, v in w.items()}          # renormalise to sum 1

    df = df.copy()
    df["direct_norm"] = norm_robust(df["direct_intent"])
    df["unaware_norm"] = norm_robust(df["unaware_intent"])
    df["climate_norm"] = 0.6 * norm(df["temp_c"]) + 0.4 * norm(df["humidity_pct"])
    if "avg_income" not in df.columns:
        df["avg_income"] = float("nan")          # crash-proof: missing income -> neutral 0.5
    df["income_norm"] = norm(df["avg_income"])

    # competition: computed for context, NOT added to the score
    df = pd.concat([df, _competition(df)], axis=1)
    df["low_confidence"] = df["comp_C"] < conf_threshold

    df["score"] = (w["direct"] * df["direct_norm"]
                   + w["unaware"] * df["unaware_norm"]
                   + w["climate"] * df["climate_norm"]
                   + w["income"] * df["income_norm"])
    df["score_100"] = (df["score"] * 100).round(1)

    try:
        df["tier"] = pd.qcut(df["score"], 3, labels=["C", "B", "A"]).astype(str)
    except ValueError:
        df["tier"] = "B"
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def competition_summary(scored_df: pd.DataFrame, conf_threshold: float = CONF_THRESHOLD) -> dict:
    """Apply the inclusion rule to the competition layer: a signal earns a place
    in the score only if it varies across regions AND is reliable. Returns the
    inputs and verdict so the app can explain why competition is context-only."""
    T = pd.to_numeric(scored_df["comp_T"], errors="coerce")
    B = pd.to_numeric(scored_df["comp_B"], errors="coerce")
    C = pd.to_numeric(scored_df["comp_C"], errors="coerce")
    t_cv = float(T.std(ddof=0) / T.mean()) if T.mean() else 0.0
    b_spread = int(B.max() - B.min())
    varies = bool(t_cv >= VARIES_CV_MIN or b_spread >= 2)
    median_C = float(C.median())
    reliable = bool(median_C >= conf_threshold)
    return {
        "n": int(len(scored_df)),
        "b_min": int(B.min()), "b_max": int(B.max()),
        "t_min": int(T.min()), "t_max": int(T.max()),
        "t_cv": round(t_cv, 3), "median_C": round(median_C, 2),
        "varies": varies, "reliable": reliable, "scored": bool(varies and reliable),
        "max_brands": MAX_BRANDS, "max_presence": MAX_PRESENCE,
    }
