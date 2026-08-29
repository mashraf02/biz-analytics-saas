"""
Simple linear-trend revenue forecasting.

Uses scikit-learn's LinearRegression over daily revenue history to project
future revenue. This is intentionally simple: with small order volumes,
anything more complex (ARIMA, LSTM, etc.) would overfit noise rather than
capture real signal. As real transaction volume grows, this same interface
can be swapped for a more sophisticated model without changing the API.
"""

from datetime import date, timedelta
from decimal import Decimal
import numpy as np
from sklearn.linear_model import LinearRegression

MIN_DATA_POINTS = 3  # below this, a trend line is not meaningful


def forecast_revenue(history: list[tuple[date, Decimal]], days_ahead: int = 7) -> dict:
    """
    history: list of (day, revenue) tuples, ordered by day ascending.
    Returns a dict with the forecast and whether it should be trusted.
    """
    if len(history) < MIN_DATA_POINTS:
        return {
            "reliable": False,
            "reason": f"Need at least {MIN_DATA_POINTS} days of order history for a forecast; have {len(history)}.",
            "forecast": [],
        }

    base_day = history[0][0]
    X = np.array([(day - base_day).days for day, _ in history]).reshape(-1, 1)
    y = np.array([float(revenue) for _, revenue in history])

    model = LinearRegression()
    model.fit(X, y)

    last_day_offset = (history[-1][0] - base_day).days
    future_offsets = np.array(
        [last_day_offset + i for i in range(1, days_ahead + 1)]
    ).reshape(-1, 1)
    predictions = model.predict(future_offsets)

    forecast = [
        {
            "day": (history[-1][0] + timedelta(days=i)).isoformat(),
            "predicted_revenue": round(max(0.0, float(pred)), 2),  # revenue can't go negative
        }
        for i, pred in enumerate(predictions, start=1)
    ]

    return {
        "reliable": True,
        "reason": None,
        "trend": "increasing" if model.coef_[0] > 0 else "decreasing" if model.coef_[0] < 0 else "flat",
        "forecast": forecast,
    }
