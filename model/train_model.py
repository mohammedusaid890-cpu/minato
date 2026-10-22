"""
TripGenius — Cost Prediction Model
-----------------------------------
Trains a small regression model that predicts a realistic *per-day spend
multiplier* for a trip, based on:
    - number of days
    - traveller's declared budget
    - destination cost tier (metro / tier-2 / leisure-hill / beach)
    - travel style (relaxed / active / family)

This is intentionally a transparent, explainable model (Linear Regression
on engineered features) rather than a black box — appropriate for an
internship-level Data Science / ML demo, and fast enough to retrain on
every server start with no external dataset needed.

The synthetic data below is generated from hand-set domain rules with
noise, standing in for real historical booking data a production version
would train on.

Run directly to (re)generate model/trip_cost_model.pkl:
    python model/train_model.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

RANDOM_SEED = 42

# Destination cost tiers: base cost-per-day multiplier (relative to budget/day)
DESTINATION_TIERS = {
    "metro":       1.25,   # Mumbai, Delhi, Bengaluru
    "tier2":       0.95,   # Jaipur, Lucknow, Indore
    "hill":        1.05,   # Manali, Munnar, Darjeeling
    "beach":       1.15,   # Goa, Pondicherry, Andaman
    "heritage":    1.00,   # Agra, Hampi, Varanasi
}

STYLE_MULTIPLIER = {
    "relaxed": 1.10,
    "active":  1.00,
    "family":  1.20,
}


def _synthesize_dataset(n=4000, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)

    days = rng.integers(1, 15, size=n)
    budget = rng.integers(3000, 200000, size=n)  # INR total trip budget
    tiers = rng.choice(list(DESTINATION_TIERS.keys()), size=n)
    styles = rng.choice(list(STYLE_MULTIPLIER.keys()), size=n)

    rows = []
    for d, b, t, s in zip(days, budget, tiers, styles):
        per_day_budget = b / d
        tier_mult = DESTINATION_TIERS[t]
        style_mult = STYLE_MULTIPLIER[s]

        # Diminishing per-day cost as trip gets longer (bulk discounts,
        # travellers naturally economize on longer trips), plus domain noise.
        length_decay = 1.0 / (1.0 + 0.015 * d)
        noise = rng.normal(0, 0.06)

        actual_spend_ratio = tier_mult * style_mult * length_decay + noise
        actual_spend_ratio = max(0.55, min(1.6, actual_spend_ratio))

        predicted_total_spend = per_day_budget * actual_spend_ratio * d

        rows.append({
            "days": d,
            "budget": b,
            "per_day_budget": per_day_budget,
            "destination_tier": t,
            "travel_style": s,
            "spend_ratio": actual_spend_ratio,
            "target_estimated_cost": predicted_total_spend,
        })

    return pd.DataFrame(rows)


def _featurize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for tier in DESTINATION_TIERS:
        out[f"tier_{tier}"] = (out["destination_tier"] == tier).astype(int)
    for style in STYLE_MULTIPLIER:
        out[f"style_{style}"] = (out["travel_style"] == style).astype(int)
    feature_cols = (
        ["days", "budget", "per_day_budget"]
        + [f"tier_{t}" for t in DESTINATION_TIERS]
        + [f"style_{s}" for s in STYLE_MULTIPLIER]
    )
    return out[feature_cols]


def train_and_save(model_path=None):
    df = _synthesize_dataset()
    X = _featurize(df)
    y = df["target_estimated_cost"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", LinearRegression()),
    ])
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"[TripGenius model] Test MAE: Rs.{mae:,.0f}  |  R2: {r2:.3f}")

    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), "trip_cost_model.pkl")

    with open(model_path, "wb") as f:
        pickle.dump({
            "pipeline": pipeline,
            "feature_columns": list(X.columns),
            "destination_tiers": list(DESTINATION_TIERS.keys()),
            "travel_styles": list(STYLE_MULTIPLIER.keys()),
            "metrics": {"mae": mae, "r2": r2},
        }, f)

    print(f"[TripGenius model] Saved to {model_path}")
    return model_path


if __name__ == "__main__":
    train_and_save()
