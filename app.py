"""
TripGenius — AI Travel Planner backend.

Internship project domain: Data Science & AI/ML using Python.

Two pieces of "intelligence" work together on every request:
  1. A trained Linear Regression model (see model/train_model.py) predicts
     a realistic estimated total spend for the trip from engineered features.
  2. A rule-based content recommender composes a day-by-day itinerary and a
     budget split, using a small curated knowledge base (data/knowledge_base.py).

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import pickle
import random

from flask import Flask, render_template, request, jsonify

from data.knowledge_base import (
    DESTINATIONS, BUDGET_SPLIT, ACTIVITY_POOL, DAY_THEME_TEMPLATES
)
from model.train_model import train_and_save, _featurize
import pandas as pd

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(APP_DIR, "model", "trip_cost_model.pkl")

app = Flask(__name__)


def load_model():
    """Load the trained model, training it on first run if missing."""
    if not os.path.exists(MODEL_PATH):
        train_and_save(MODEL_PATH)
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


MODEL_BUNDLE = load_model()


def predict_estimated_cost(days, budget, tier, style):
    row = pd.DataFrame([{
        "days": days,
        "budget": budget,
        "per_day_budget": budget / max(days, 1),
        "destination_tier": tier,
        "travel_style": style,
    }])
    X = _featurize(row)
    X = X.reindex(columns=MODEL_BUNDLE["feature_columns"], fill_value=0)
    pred = MODEL_BUNDLE["pipeline"].predict(X)[0]
    return max(0, round(pred))


def build_budget_breakdown(budget, style):
    split = BUDGET_SPLIT.get(style, BUDGET_SPLIT["relaxed"])
    return {
        category: round(budget * pct)
        for category, pct in split.items()
    }


def build_itinerary(destination_key, days, tier, style):
    pool = ACTIVITY_POOL.get(tier, ACTIVITY_POOL["tier2"])[style]
    themes = (
        [DAY_THEME_TEMPLATES[0]]
        + DAY_THEME_TEMPLATES[1:-1]
        + [DAY_THEME_TEMPLATES[-1]]
    )

    itinerary = []
    used = set()
    for day_num in range(1, days + 1):
        if day_num == 1:
            theme = "Arrival & First Impressions"
        elif day_num == days and days > 1:
            theme = "Departure Day"
        else:
            mid_themes = [t for t in themes if t not in ("Arrival & First Impressions", "Departure Day")]
            theme = mid_themes[(day_num - 2) % len(mid_themes)]

        available = [a for a in pool if a not in used] or list(pool)
        picks = random.sample(available, k=min(2, len(available)))
        used.update(picks)

        if day_num == 1:
            morning = "Check-in and settle into your stay"
            afternoon = picks[0] if picks else "Explore the neighbourhood on foot"
            evening = "An easy dinner near your stay to beat jet lag"
        elif day_num == days and days > 1:
            morning = picks[0] if picks else "Last-minute local shopping"
            afternoon = "Pack up and check out"
            evening = "Head to the airport / station"
        else:
            morning = picks[0] if picks else "Free exploration"
            afternoon = picks[1] if len(picks) > 1 else "Rest and recharge"
            evening = "Dinner at a locally recommended spot"

        itinerary.append({
            "day": day_num,
            "theme": theme,
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
        })

    return itinerary


@app.route("/")
def home():
    return render_template("index.html", destinations=DESTINATIONS)


@app.route("/api/plan", methods=["POST"])
def api_plan():
    data = request.get_json(force=True) or {}

    try:
        budget = int(data.get("budget", 0))
        days = int(data.get("days", 0))
        destination_key = str(data.get("destination", "")).strip().lower()
        style = str(data.get("style", "relaxed")).strip().lower()
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input types."}), 400

    if budget < 1000:
        return jsonify({"error": "Budget should be at least Rs.1,000."}), 400
    if not (1 <= days <= 21):
        return jsonify({"error": "Days should be between 1 and 21."}), 400
    if destination_key not in DESTINATIONS:
        return jsonify({"error": "Please choose a supported destination."}), 400
    if style not in BUDGET_SPLIT:
        style = "relaxed"

    tier = DESTINATIONS[destination_key]["tier"]
    label = DESTINATIONS[destination_key]["label"]

    estimated_cost = predict_estimated_cost(days, budget, tier, style)
    within_budget = estimated_cost <= budget
    breakdown = build_budget_breakdown(budget, style)
    itinerary = build_itinerary(destination_key, days, tier, style)

    tips = []
    if not within_budget:
        overshoot_pct = round(((estimated_cost - budget) / budget) * 100)
        tips.append(
            f"Our model predicts this trip typically runs about {overshoot_pct}% over your budget "
            f"for {label} in {style} style — consider a mid-range hotel tier or trimming a day."
        )
    else:
        tips.append(
            f"Your budget comfortably covers a {style} trip to {label} — you have room for one "
            f"extra activity or a nicer hotel tier."
        )
    tips.append("Book transport and hotels 2-3 weeks ahead for the best local prices.")
    tips.append("Keep the buffer amount aside for unexpected costs and currency swings.")

    return jsonify({
        "destination": label,
        "days": days,
        "style": style,
        "budget": budget,
        "estimated_cost": estimated_cost,
        "within_budget": within_budget,
        "budget_breakdown": breakdown,
        "itinerary": itinerary,
        "tips": tips,
        "model_metrics": MODEL_BUNDLE["metrics"],
    })


if __name__ == "__main__":
    app.run(debug=True)
