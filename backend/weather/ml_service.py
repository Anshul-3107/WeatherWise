import logging
from pathlib import Path
import joblib
import pandas as pd

logger = logging.getLogger(__name__)

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

RAIN_WEATHER_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

_temperature_model = None
_rain_model = None


def _load_models():
    """
    Loads both models into memory once, on first use, and caches them
    at module level so subsequent calls don't re-read from disk.
    """
    global _temperature_model, _rain_model

    temp_path = MODELS_DIR / "temperature_model.joblib"
    rain_path = MODELS_DIR / "rain_model.joblib"

    if not temp_path.exists() or not rain_path.exists():
        logger.warning("ML models not found in %s. Using heuristic fallback.", MODELS_DIR)
        return None, None

    if _temperature_model is None:
        _temperature_model = joblib.load(temp_path)

    if _rain_model is None:
        _rain_model = joblib.load(rain_path)

    return _temperature_model, _rain_model


def predict_next_24h(current_conditions: dict) -> dict:
    """
    Takes current weather conditions (matching FEATURE_COLUMNS) and returns
    a prediction for the next 24 hours: average temperature and rain likelihood.
    """
    temperature_model, rain_model = _load_models()

    # Graceful fallback if models are absent
    if temperature_model is None or rain_model is None:
        curr_temp = float(current_conditions.get("temperature_2m", 25.0))
        code = int(current_conditions.get("weather_code", 0))
        cloud = float(current_conditions.get("cloud_cover", 0.0))

        is_rain = code in RAIN_WEATHER_CODES or cloud > 80.0
        prob = 0.75 if code in RAIN_WEATHER_CODES else (0.45 if cloud > 70 else 0.15)

        return {
            "predicted_avg_temp_24h": round(curr_temp, 1),
            "will_rain_24h": is_rain,
            "rain_probability": prob,
        }

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