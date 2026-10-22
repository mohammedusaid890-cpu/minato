# TripGenius — AI Travel Planner

An internship project (Data Science & AI/ML using Python) that plans a
budget-aware, day-by-day trip from three inputs: **destination, days, budget**.

## What's "AI/ML" about it

1. **Trained cost-prediction model** (`model/train_model.py`)
   A scikit-learn `LinearRegression` pipeline (with `StandardScaler`) trained
   on a synthetic-but-domain-realistic dataset of trips, engineered from
   destination cost-tier, travel style, trip length, and budget. It predicts
   a realistic **estimated total spend**, which the app compares against the
   traveller's stated budget. Metrics (MAE, R²) are computed on a held-out
   test split and shown live in the UI so the model's honesty is visible,
   not hidden.

2. **Rule-based recommendation engine** (`data/knowledge_base.py` +
   `app.py: build_itinerary`, `build_budget_breakdown`)
   A curated content model (destinations → cost tier → activity pool) drives
   itinerary generation and the hotel/food/transport/activities budget split —
   a transparent, explainable recommender, appropriate to present and defend
   in a viva.

Both pieces are real, working Python — nothing is faked or hardcoded per
destination; change the model's training data or the activity pool and the
output changes accordingly.

## Project structure

```
tripgenius/
├── app.py                     # Flask app + API route
├── requirements.txt
├── model/
│   ├── train_model.py         # trains & saves the regression model
│   └── trip_cost_model.pkl    # generated on first run (git-ignoreable)
├── data/
│   └── knowledge_base.py      # destinations, activities, budget-split rules
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Run it locally

```bash
cd tripgenius
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** — the model trains automatically on first run
(takes under a second) and is cached to `model/trip_cost_model.pkl` after that.

To retrain manually:
```bash
python model/train_model.py
```

## Demoing / for your report

- Fill the form (destination, days, budget, style) and click **Plan my trip**.
- The results panel shows: the model's cost estimate vs. your budget, a
  category-wise budget split, a full day-by-day itinerary, and notes.
- **Save as PDF** uses the browser's print dialog (`window.print()`) with a
  dedicated print stylesheet — no extra library needed.
- The `model_metrics` (MAE, R²) returned by `/api/plan` are worth screenshotting
  for your report as evidence of a trained, evaluated model rather than a
  lookup table.

## Extending it (good "future scope" talking points)

- Swap the synthetic training data for real scraped/booking data.
- Add more destinations to `data/knowledge_base.py` — no code changes needed
  elsewhere as long as the destination has a `tier`.
- Replace `LinearRegression` with a `RandomForestRegressor` or `XGBoost` model
  and compare metrics — the pipeline structure already supports it.
- Add a weather/price-alerts service (stubbed in the landing page today).

## Notes

- All costs are indicative model estimates, not live prices — the UI states
  this explicitly, which is worth keeping for academic honesty.
- No external API keys or internet access are required to run this project.
