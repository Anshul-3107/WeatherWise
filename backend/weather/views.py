from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import (
    fetch_weather_from_open_meteo,
    save_weather_record,
    geocode_city,
    fetch_air_quality_from_open_meteo,
    save_air_quality_record,
    generate_alerts_from_weather,
    get_astronomy_data,
)
from .serializers import WeatherRecordSerializer, AirQualityRecordSerializer
from .ml_service import predict_next_24h
from .advice_service import generate_personalized_advice


@api_view(['GET'])
def get_current_weather(request):
    city_name = request.query_params.get('city')
    latitude = request.query_params.get('lat')
    longitude = request.query_params.get('lon')

    if not all([city_name, latitude, longitude]):
        return Response(
            {"error": "city, lat, and lon query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {"error": "lat and lon must be valid numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        raw_weather_data = fetch_weather_from_open_meteo(latitude, longitude)
    except Exception:
        return Response(
            {"error": "Failed to fetch weather data. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        astro_data = get_astronomy_data(latitude, longitude)
        raw_weather_data.update(astro_data)
    except Exception:
        pass

    try:
        raw_aqi_data = fetch_air_quality_from_open_meteo(latitude, longitude)
    except Exception:
        raw_aqi_data = None

    # Resolve real city name if client passed generic placeholder
    if not city_name or city_name.strip().lower() in ("current location", "current_location", "unknown", "none"):
        resolved_city = raw_weather_data.get("city_name")
        if resolved_city:
            city_name = resolved_city
        else:
            try:
                from .services import reverse_geocode
                geo = reverse_geocode(latitude, longitude)
                if geo and geo.get("name"):
                    city_name = geo["name"]
            except Exception:
                pass

    try:
        weather_record = save_weather_record(city_name, latitude, longitude, raw_weather_data)
        response_data = dict(WeatherRecordSerializer(weather_record).data)
    except Exception:
        current = raw_weather_data.get("current", {})
        daily = raw_weather_data.get("daily", {})
        response_data = {
            "city_name": city_name,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "temperature_2m": current.get("temperature_2m", 0.0),
            "relative_humidity_2m": current.get("relative_humidity_2m", 0.0),
            "apparent_temperature": current.get("apparent_temperature", 0.0),
            "wind_speed_10m": current.get("wind_speed_10m", 0.0),
            "wind_direction_10m": current.get("wind_direction_10m", 0.0),
            "weather_code": current.get("weather_code", 0),
            "is_day": bool(current.get("is_day", True)),
            "sunrise": daily.get("sunrise", [None])[0],
            "sunset": daily.get("sunset", [None])[0],
            "moonrise": raw_weather_data.get("moonrise"),
            "moonset": raw_weather_data.get("moonset"),
            "moon_phase": raw_weather_data.get("moon_phase"),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

    alerts = []
    if raw_aqi_data is not None:
        alerts = generate_alerts_from_weather(raw_weather_data, raw_aqi_data)

    response_data['alerts'] = alerts

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def search_city(request):
    city_name = request.query_params.get('city')

    if not city_name:
        return Response(
            {"error": "city query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        location = geocode_city(city_name)
    except ValueError:
        return Response(
            {"error": f"No location found for '{city_name}'."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        return Response(
            {"error": "Failed to search city. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(location, status=status.HTTP_200_OK)


@api_view(['GET'])
def reverse_geocode_view(request):
    latitude = request.query_params.get('lat')
    longitude = request.query_params.get('lon')

    if not latitude or not longitude:
        return Response(
            {"error": "lat and lon query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {"error": "lat and lon must be valid numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from .services import reverse_geocode
        location = reverse_geocode(latitude, longitude)
    except ValueError:
        return Response(
            {"error": "No location found for coordinates."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        return Response(
            {"error": "Failed to reverse geocode. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(location, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_air_quality(request):
    city_name = request.query_params.get('city')
    latitude = request.query_params.get('lat')
    longitude = request.query_params.get('lon')

    if not all([city_name, latitude, longitude]):
        return Response(
            {"error": "city, lat, and lon query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {"error": "lat and lon must be valid numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        raw_data = fetch_air_quality_from_open_meteo(latitude, longitude)
    except Exception:
        return Response(
            {"error": "Failed to fetch air quality data. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        record = save_air_quality_record(city_name, latitude, longitude, raw_data)
        serializer = AirQualityRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception:
        curr = raw_data.get("current", {})
        fallback_data = {
            "city_name": city_name,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "us_aqi": curr.get("us_aqi", 0),
            "pm2_5": curr.get("pm2_5", 0.0),
            "pm10": curr.get("pm10", 0.0),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        return Response(fallback_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_prediction(request):
    latitude = request.query_params.get('lat')
    longitude = request.query_params.get('lon')

    if not latitude or not longitude:
        return Response(
            {"error": "lat and lon query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {"error": "lat and lon must be valid numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        raw_weather_data = fetch_weather_from_open_meteo(latitude, longitude)
        raw_aqi_data = fetch_air_quality_from_open_meteo(latitude, longitude)
    except Exception:
        return Response(
            {"error": "Failed to fetch current conditions for prediction."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    current = raw_weather_data["current"]

    try:
        prediction = predict_next_24h(current)
    except Exception as e:
        print(f"PREDICTION ERROR: {type(e).__name__}: {e}")
        return Response(
            {"error": "Failed to generate prediction."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(prediction, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_advice(request):
    latitude = request.query_params.get('lat')
    longitude = request.query_params.get('lon')
    profiles_param = request.query_params.get('profiles', '')

    if not latitude or not longitude:
        return Response(
            {"error": "lat and lon query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    selected_profiles = [p.strip() for p in profiles_param.split(',') if p.strip()]

    if not selected_profiles:
        return Response({"advice": []}, status=status.HTTP_200_OK)

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {"error": "lat and lon must be valid numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        raw_weather_data = fetch_weather_from_open_meteo(latitude, longitude)
        raw_aqi_data = fetch_air_quality_from_open_meteo(latitude, longitude)
    except Exception:
        return Response(
            {"error": "Failed to fetch current conditions for advice."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    current = raw_weather_data["current"]
    aqi = raw_aqi_data["current"]["us_aqi"]

    advice = generate_personalized_advice(current, aqi, selected_profiles)

    return Response({"advice": advice}, status=status.HTTP_200_OK)