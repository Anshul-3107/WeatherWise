def _get_pilot_advice(current: dict) -> str:
    wind_speed = current["wind_speed_10m"]
    weather_code = current["weather_code"]
    cloud_cover = current.get("cloud_cover", 0)

    if weather_code in (95, 96, 99):
        return "Thunderstorms in the area — flying conditions are unsafe. Delay departure if possible."
    if wind_speed >= 30:
        return f"Strong winds at {wind_speed} km/h. Expect turbulence and crosswind challenges on approach."
    if cloud_cover >= 80:
        return "Heavy cloud cover may reduce visibility. Check ceiling reports before departure."
    if wind_speed <= 15 and cloud_cover <= 30:
        return "Calm winds and clear skies — good flying conditions today."
    return "Moderate conditions. Standard pre-flight checks recommended."


def _get_farmer_advice(current: dict) -> str:
    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    weather_code = current["weather_code"]

    if weather_code in (61, 63, 65, 80, 81, 82):
        return "Rain expected — good for irrigation, but delay any pesticide or fertilizer spraying."
    if temperature >= 38:
        return f"High temperature of {temperature}°C may stress crops. Ensure adequate irrigation."
    if humidity >= 85:
        return "High humidity increases fungal disease risk. Monitor crops closely."
    if temperature <= 10:
        return f"Low temperature of {temperature}°C — watch for frost risk on sensitive crops."
    return "Favorable conditions for regular field activity today."


def _get_traveler_advice(current: dict, aqi: int) -> str:
    temperature = current["temperature_2m"]
    weather_code = current["weather_code"]

    if weather_code in (61, 63, 65, 80, 81, 82, 95, 96, 99):
        return "Rain or storms expected — pack an umbrella and plan indoor alternatives."
    if aqi > 150:
        return f"Air quality is poor (AQI {aqi}). Consider a mask if spending time outdoors."
    if temperature >= 38:
        return f"Very hot at {temperature}°C. Stay hydrated and plan outdoor activities for cooler hours."
    if temperature <= 10:
        return f"Cool weather at {temperature}°C. Pack warm layers."
    return "Pleasant conditions for sightseeing and outdoor activities."


def _get_cyclist_advice(current: dict, aqi: int) -> str:
    wind_speed = current["wind_speed_10m"]
    weather_code = current["weather_code"]
    temperature = current["temperature_2m"]

    if weather_code in (61, 63, 65, 80, 81, 82, 95, 96, 99):
        return "Wet roads expected — reduce speed and increase braking distance, or consider indoor training."
    if wind_speed >= 25:
        return f"Strong winds at {wind_speed} km/h will slow you down. Plan routes accordingly."
    if aqi > 150:
        return f"Poor air quality (AQI {aqi}) — consider an indoor ride instead."
    if temperature >= 35:
        return f"Hot at {temperature}°C. Ride early morning or evening, and carry extra water."
    return "Good conditions for a ride today."


def _get_student_advice(current: dict, aqi: int) -> str:
    weather_code = current["weather_code"]
    temperature = current["temperature_2m"]

    if weather_code in (61, 63, 65, 80, 81, 82, 95, 96, 99):
        return "Rain expected during commute hours — leave extra time and carry rain protection."
    if aqi > 150:
        return f"Air quality is poor (AQI {aqi}). Limit outdoor activity between classes."
    if temperature >= 38:
        return f"Very hot at {temperature}°C. Stay hydrated between classes."
    return "Normal conditions for your daily commute and activities."


PROFILE_ADVICE_GENERATORS = {
    "pilot": lambda current, aqi: _get_pilot_advice(current),
    "farmer": lambda current, aqi: _get_farmer_advice(current),
    "traveler": lambda current, aqi: _get_traveler_advice(current, aqi),
    "cyclist": lambda current, aqi: _get_cyclist_advice(current, aqi),
    "student": lambda current, aqi: _get_student_advice(current, aqi),
}


def generate_personalized_advice(current: dict, aqi: int, selected_profiles: list[str]) -> list[dict]:
    """
    Generates advice for each selected profile based on current weather
    and air quality. Returns a list of {profile, advice} dicts, one per
    valid selected profile.
    """
    results = []

    for profile_id in selected_profiles:
        generator = PROFILE_ADVICE_GENERATORS.get(profile_id)
        if generator is None:
            continue

        advice_text = generator(current, aqi)
        results.append({
            "profile": profile_id,
            "advice": advice_text,
        })

    return results