import os
import requests
from datetime import datetime, timezone, date
# pyrefly: ignore [missing-import]
from astral import LocationInfo
# pyrefly: ignore [missing-import]
from astral import moon as astral_moon
from .models import WeatherRecord, AirQualityRecord
from .owm_mapping import owm_id_to_wmo_code


OPENWEATHER_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def _get_api_key() -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENWEATHER_API_KEY", "")
        except ImportError:
            pass
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
    return api_key


def pm25_to_us_aqi(pm25: float) -> int:
    """
    Converts PM2.5 concentration (µg/m³) to US AQI using the standard EPA
    linear breakpoint formula.
    """
    if pm25 is None or pm25 < 0:
        return 0

    c = round(float(pm25), 1)

    # Breakpoints: (c_low, c_high, i_low, i_high)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= c <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low
            return round(aqi)

    if c > 500.4:
        return 500

    return 0


def fetch_weather_from_open_meteo(latitude: float, longitude: float) -> dict:
    """
    Calls OpenWeatherMap's Current Weather API and reshapes the response into
    the internal structure expected by downstream models, serializers, and ML services:
    {"current": {...}, "daily": {"sunrise": [...], "sunset": [...]}}
    """
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": _get_api_key(),
        "units": "metric",
    }

    response = requests.get(OPENWEATHER_WEATHER_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    main = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    sys = data.get("sys", {})
    weather_list = data.get("weather", [])

    owm_id = weather_list[0]["id"] if weather_list else 800
    weather_code = owm_id_to_wmo_code(owm_id)

    # Convert wind speed from m/s to km/h
    wind_speed_ms = wind.get("speed", 0.0)
    wind_speed_kmh = round(float(wind_speed_ms) * 3.6, 2)

    # OpenWeatherMap can omit 'deg' during calm or variable winds
    wind_direction_10m = float(wind.get("deg", 0.0))

    temp = float(main.get("temp", 0.0))
    humidity = float(main.get("humidity", 0.0))
    apparent_temp = float(main.get("feels_like", temp))

    # Prefer mean sea-level pressure if available, fall back to standard pressure
    pressure = float(main.get("sea_level", main.get("pressure", 1013.25)))
    cloud_cover = float(clouds.get("all", 0.0))

    current_dt = data.get("dt", int(datetime.now(timezone.utc).timestamp()))
    sunrise_ts = sys.get("sunrise", current_dt)
    sunset_ts = sys.get("sunset", current_dt)

    is_day = 1 if (sunrise_ts <= current_dt < sunset_ts) else 0

    sunrise_iso = datetime.fromtimestamp(sunrise_ts, tz=timezone.utc).isoformat()
    sunset_iso = datetime.fromtimestamp(sunset_ts, tz=timezone.utc).isoformat()

    return {
        "current": {
            "temperature_2m": temp,
            "relative_humidity_2m": humidity,
            "apparent_temperature": apparent_temp,
            "wind_speed_10m": wind_speed_kmh,
            "wind_direction_10m": wind_direction_10m,
            "weather_code": weather_code,
            "is_day": is_day,
            "pressure_msl": pressure,
            "cloud_cover": cloud_cover,
        },
        "daily": {
            "sunrise": [sunrise_iso],
            "sunset": [sunset_iso],
        },
    }


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
        moonrise=raw_data.get("moonrise"),
        moonset=raw_data.get("moonset"),
        moon_phase=raw_data.get("moon_phase"),
    )
    return record


def get_astronomy_data(latitude: float, longitude: float) -> dict:
    """
    Computes sunrise/sunset/moonrise/moonset/moon phase locally using
    the astral library.
    """
    loc = LocationInfo(latitude=latitude, longitude=longitude)
    d = datetime.now(timezone.utc).date()
    
    try:
        m_rise = astral_moon.moonrise(loc.observer, date=d)
    except Exception:
        m_rise = None
        
    try:
        m_set = astral_moon.moonset(loc.observer, date=d)
    except Exception:
        m_set = None
        
    try:
        phase = astral_moon.phase(d)
    except Exception:
        phase = None
        
    return {
        "moonrise": m_rise,
        "moonset": m_set,
        "moon_phase": phase,
    }


def geocode_city(city_name: str) -> dict:
    """
    Resolves a city name to latitude/longitude using OpenWeatherMap's Geocoding API.
    Returns a dict with 'name', 'latitude', 'longitude', 'country', 'admin1'.
    Raises ValueError if no match is found.
    """
    params = {
        "q": city_name,
        "limit": 1,
        "appid": _get_api_key(),
    }

    response = requests.get(OPENWEATHER_GEOCODING_URL, params=params, timeout=10)
    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"No location found for '{city_name}'")

    match = results[0]
    return {
        "name": match["name"],
        "latitude": match["lat"],
        "longitude": match["lon"],
        "country": match.get("country", ""),
        "admin1": match.get("state", ""),
    }


def reverse_geocode(latitude: float, longitude: float) -> dict:
    """
    Resolves latitude/longitude to a city name using OpenWeatherMap's Reverse Geocoding API.
    """
    url = "http://api.openweathermap.org/geo/1.0/reverse"
    params = {
        "lat": latitude,
        "lon": longitude,
        "limit": 1,
        "appid": _get_api_key(),
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"No location found for coordinates.")

    match = results[0]
    return {
        "name": match["name"],
        "latitude": match["lat"],
        "longitude": match["lon"],
        "country": match.get("country", ""),
        "admin1": match.get("state", ""),
    }


def fetch_air_quality_from_open_meteo(latitude: float, longitude: float) -> dict:
    """
    Calls OpenWeatherMap's Air Pollution API and reshapes the response into
    the internal structure expected by save_air_quality_record:
    {"current": {"us_aqi": ..., "pm2_5": ..., "pm10": ...}}
    """
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": _get_api_key(),
    }

    response = requests.get(OPENWEATHER_AIR_POLLUTION_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    results_list = data.get("list", [])
    components = results_list[0].get("components", {}) if results_list else {}

    pm2_5 = float(components.get("pm2_5", 0.0))
    pm10 = float(components.get("pm10", 0.0))
    us_aqi = pm25_to_us_aqi(pm2_5)

    return {
        "current": {
            "us_aqi": us_aqi,
            "pm2_5": pm2_5,
            "pm10": pm10,
        }
    }


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