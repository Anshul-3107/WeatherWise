import requests
from datetime import datetime
from .models import WeatherRecord, AirQualityRecord


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather_from_open_meteo(latitude: float, longitude: float) -> dict:
    """
    Calls Open-Meteo's forecast API and returns the raw parsed JSON.
    Raises requests.RequestException if the call fails.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "wind_speed_10m",
            "wind_direction_10m",
            "weather_code",
            "is_day",
            "pressure_msl",
            "cloud_cover",
        ],
        "daily": ["sunrise", "sunset"],
        "timezone": "auto",
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def save_weather_record(city_name: str, latitude: float, longitude: float, raw_data: dict) -> WeatherRecord:
    """
    Takes Open-Meteo's raw JSON response and creates a new WeatherRecord from it.
    """
    current = raw_data["current"]
    daily = raw_data["daily"]

    sunrise = datetime.fromisoformat(daily["sunrise"][0])
    sunset = datetime.fromisoformat(daily["sunset"][0])

    record = WeatherRecord.objects.create(
        city_name=city_name,
        latitude=latitude,
        longitude=longitude,
        temperature_2m=current["temperature_2m"],
        relative_humidity_2m=current["relative_humidity_2m"],
        apparent_temperature=current["apparent_temperature"],
        wind_speed_10m=current["wind_speed_10m"],
        wind_direction_10m=current["wind_direction_10m"],
        weather_code=current["weather_code"],
        is_day=bool(current["is_day"]),
        sunrise=sunrise,
        sunset=sunset,
    )
    return record


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode_city(city_name: str) -> dict:
    """
    Resolves a city name to latitude/longitude using Open-Meteo's Geocoding API.
    Returns a dict with 'name', 'latitude', 'longitude', 'country', 'admin1'.
    Raises ValueError if no match is found.
    """
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = requests.get(GEOCODING_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        raise ValueError(f"No location found for '{city_name}'")

    match = results[0]
    return {
        "name": match["name"],
        "latitude": match["latitude"],
        "longitude": match["longitude"],
        "country": match.get("country", ""),
        "admin1": match.get("admin1", ""),
    }


AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def fetch_air_quality_from_open_meteo(latitude: float, longitude: float) -> dict:
    """
    Calls Open-Meteo's Air Quality API and returns the raw parsed JSON.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["us_aqi", "pm2_5", "pm10"],
    }

    response = requests.get(AIR_QUALITY_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def save_air_quality_record(city_name: str, latitude: float, longitude: float, raw_data: dict) -> AirQualityRecord:
    """
    Takes Open-Meteo's raw air quality JSON and creates a new AirQualityRecord.
    """
    current = raw_data["current"]

    record = AirQualityRecord.objects.create(
        city_name=city_name,
        latitude=latitude,
        longitude=longitude,
        us_aqi=current["us_aqi"],
        pm2_5=current["pm2_5"],
        pm10=current["pm10"],
    )
    return record


def generate_alerts_from_weather(weather_data: dict, air_quality_data: dict) -> list[dict]:
    """
    Derives simple alert messages from current weather and air quality data,
    based on reasonable thresholds. Returns an empty list if nothing
    warrants an alert.
    """
    alerts = []
    current = weather_data["current"]

    wind_speed = current["wind_speed_10m"]
    if wind_speed >= 40:
        alerts.append({
            "headline": "Strong Wind Warning",
            "description": f"Wind speeds of {wind_speed} km/h expected. Secure loose objects outdoors.",
            "severity": "Moderate",
        })

    temperature = current["temperature_2m"]
    if temperature >= 40:
        alerts.append({
            "headline": "Extreme Heat Warning",
            "description": f"Temperature of {temperature}°C expected. Stay hydrated and avoid prolonged sun exposure.",
            "severity": "Moderate",
        })
    elif temperature <= 2:
        alerts.append({
            "headline": "Cold Weather Advisory",
            "description": f"Temperature of {temperature}°C expected. Dress warmly and watch for icy conditions.",
            "severity": "Minor",
        })

    weather_code = current["weather_code"]
    if weather_code in (95, 96, 99):
        alerts.append({
            "headline": "Thunderstorm Warning",
            "description": "Thunderstorms expected in the area. Seek shelter and avoid open areas.",
            "severity": "Severe",
        })

    us_aqi = air_quality_data["current"]["us_aqi"]
    if us_aqi > 150:
        alerts.append({
            "headline": "Poor Air Quality Warning",
            "description": f"US AQI of {us_aqi} expected. Consider limiting outdoor activity, especially for sensitive groups.",
            "severity": "Moderate",
        })

    return alerts