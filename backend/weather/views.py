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
        raw_aqi_data = fetch_air_quality_from_open_meteo(latitude, longitude)
    except Exception:
        raw_aqi_data = None

    weather_record = save_weather_record(city_name, latitude, longitude, raw_weather_data)
    weather_serialized = WeatherRecordSerializer(weather_record).data

    alerts = []
    if raw_aqi_data is not None:
        alerts = generate_alerts_from_weather(raw_weather_data, raw_aqi_data)

    response_data = dict(weather_serialized)
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

    record = save_air_quality_record(city_name, latitude, longitude, raw_data)
    serializer = AirQualityRecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)


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