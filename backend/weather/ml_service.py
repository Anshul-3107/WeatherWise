from pathlib import Path
import joblib
import pandas as pd

MODELS_DIR = Path(__file__).resolve().parent / "ml_models"

FEATURE_COLUMNS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "wind_speed_10m",
    "wind_direction_10m",
    "pressure_msl",
    "cloud_cover",
    "weather_code",
]

_temperature_model = None
_rain_model = None


def _load_models():
    """
    Loads both models into memory once, on first use, and caches them
    at module level so subsequent calls don't re-read from disk.
    """
    global _temperature_model, _rain_model

    if _temperature_model is None:
        _temperature_model = joblib.load(MODELS_DIR / "temperature_model.joblib")

    if _rain_model is None:
        _rain_model = joblib.load(MODELS_DIR / "rain_model.joblib")

    return _temperature_model, _rain_model


def predict_next_24h(current_conditions: dict) -> dict:
    """
    Takes current weather conditions (matching FEATURE_COLUMNS) and returns
    a prediction for the next 24 hours: average temperature and rain likelihood.
    """
    temperature_model, rain_model = _load_models()

    features = pd.DataFrame([{
        col: current_conditions[col] for col in FEATURE_COLUMNS
    }])

    predicted_avg_temp = temperature_model.predict(features)[0]

    rain_prediction = rain_model.predict(features)[0]
    rain_probability = rain_model.predict_proba(features)[0][1]

    return {
        "predicted_avg_temp_24h": round(float(predicted_avg_temp), 1),
        "will_rain_24h": bool(rain_prediction),
        "rain_probability": round(float(rain_probability), 2),
    }