"""
Mapping from OpenWeatherMap condition IDs to WMO weather interpretation codes.
Used to preserve downstream compatibility with ML models, alerts, and advice logic
that expect the WMO 0-99 code scheme.
"""

OWM_TO_WMO_MAP: dict[int, int] = {
    # Group 2xx: Thunderstorm -> WMO 95 (or 99 for extreme)
    200: 95,  # Thunderstorm with light rain
    201: 95,  # Thunderstorm with rain
    202: 95,  # Thunderstorm with heavy rain
    210: 95,  # Light thunderstorm
    211: 95,  # Thunderstorm
    212: 95,  # Heavy thunderstorm
    221: 95,  # Ragged thunderstorm
    230: 95,  # Thunderstorm with light drizzle
    231: 95,  # Thunderstorm with drizzle
    232: 95,  # Thunderstorm with heavy drizzle

    # Group 3xx: Drizzle -> WMO 51, 53, 55
    300: 51,  # Light intensity drizzle
    301: 53,  # Drizzle
    302: 55,  # Heavy intensity drizzle
    310: 51,  # Light intensity drizzle rain
    311: 53,  # Drizzle rain
    312: 55,  # Heavy intensity drizzle rain
    313: 53,  # Shower rain and drizzle
    314: 55,  # Heavy shower rain and drizzle
    321: 53,  # Shower drizzle

    # Group 5xx: Rain -> WMO 61, 63, 65, 66, 80, 81, 82
    500: 61,  # Light rain
    501: 63,  # Moderate rain
    502: 65,  # Heavy intensity rain
    503: 65,  # Very heavy rain
    504: 65,  # Extreme rain
    511: 66,  # Freezing rain (Light freezing rain)
    520: 80,  # Light intensity shower rain
    521: 81,  # Shower rain
    522: 82,  # Heavy intensity shower rain
    531: 81,  # Ragged shower rain

    # Group 6xx: Snow -> WMO 71, 73, 75, 77, 85, 86
    600: 71,  # Light snow
    601: 73,  # Snow
    602: 75,  # Heavy snow
    611: 77,  # Sleet (Snow grains)
    612: 85,  # Light shower sleet
    613: 85,  # Shower sleet
    615: 71,  # Light rain and snow
    616: 73,  # Rain and snow
    620: 85,  # Light shower snow
    621: 85,  # Shower snow
    622: 86,  # Heavy shower snow

    # Group 7xx: Atmosphere -> WMO 45 (Fog), 82 (Squalls), 99 (Tornado)
    701: 45,  # Mist
    711: 45,  # Smoke
    721: 45,  # Haze
    731: 45,  # Sand/dust whirls
    741: 45,  # Fog
    751: 45,  # Sand
    761: 45,  # Dust
    762: 45,  # Volcanic ash
    771: 82,  # Squalls
    781: 99,  # Tornado

    # Group 800: Clear -> WMO 0
    800: 0,   # Clear sky

    # Group 80x: Clouds -> WMO 1, 2, 3
    801: 1,   # Few clouds: 11-25%
    802: 2,   # Scattered clouds: 25-50%
    803: 3,   # Broken clouds: 51-84%
    804: 3,   # Overcast clouds: 85-100%
}


def owm_id_to_wmo_code(owm_id: int) -> int:
    """
    Maps an OpenWeatherMap weather condition ID to the closest WMO weather
    interpretation code used in utils.py (WMO_WEATHER_CODES / WMO_ICON_MAP).
    Falls back to 3 (Overcast) for anything unmapped or unrecognized.
    """
    if not isinstance(owm_id, int):
        return 3
    return OWM_TO_WMO_MAP.get(owm_id, 3)
