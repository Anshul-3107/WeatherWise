import os
from unittest.mock import patch, MagicMock
from django.test import TestCase
from weather.owm_mapping import owm_id_to_wmo_code
from weather.services import (
    pm25_to_us_aqi,
    fetch_weather_from_open_meteo,
    geocode_city,
    fetch_air_quality_from_open_meteo,
    save_weather_record,
    save_air_quality_record,
    generate_alerts_from_weather,
)
from weather.utils import WMO_WEATHER_CODES, WMO_ICON_MAP
from weather.models import WeatherRecord, AirQualityRecord
from weather.ml_service import predict_next_24h
from weather.advice_service import generate_personalized_advice


class OwmMappingTests(TestCase):
    def test_mapped_codes_exist_in_wmo_utils(self):
        sample_ids = [200, 300, 500, 511, 520, 600, 611, 701, 771, 781, 800, 801, 802, 803, 804]
        for owm_id in sample_ids:
            wmo_code = owm_id_to_wmo_code(owm_id)
            self.assertIn(wmo_code, WMO_WEATHER_CODES, f"Code {wmo_code} for OWM {owm_id} not in WMO_WEATHER_CODES")
            self.assertIn(wmo_code, WMO_ICON_MAP, f"Code {wmo_code} for OWM {owm_id} not in WMO_ICON_MAP")

    def test_unmapped_code_falls_back_to_3(self):
        self.assertEqual(owm_id_to_wmo_code(999999), 3)
        self.assertEqual(owm_id_to_wmo_code(-1), 3)
        self.assertEqual(owm_id_to_wmo_code(None), 3)
        self.assertEqual(owm_id_to_wmo_code("invalid"), 3)

    def test_key_mappings(self):
        self.assertEqual(owm_id_to_wmo_code(800), 0)    # Clear sky
        self.assertEqual(owm_id_to_wmo_code(801), 1)    # Few clouds
        self.assertEqual(owm_id_to_wmo_code(802), 2)    # Scattered clouds
        self.assertEqual(owm_id_to_wmo_code(804), 3)    # Overcast
        self.assertEqual(owm_id_to_wmo_code(211), 95)   # Thunderstorm
        self.assertEqual(owm_id_to_wmo_code(500), 61)   # Light rain
        self.assertEqual(owm_id_to_wmo_code(741), 45)   # Fog


class AqiConversionTests(TestCase):
    def test_pm25_to_us_aqi_breakpoints(self):
        self.assertEqual(pm25_to_us_aqi(0.0), 0)
        self.assertEqual(pm25_to_us_aqi(12.0), 50)
        self.assertEqual(pm25_to_us_aqi(35.4), 100)
        self.assertEqual(pm25_to_us_aqi(55.4), 150)
        self.assertEqual(pm25_to_us_aqi(150.4), 200)
        self.assertEqual(pm25_to_us_aqi(250.4), 300)
        self.assertEqual(pm25_to_us_aqi(350.4), 400)
        self.assertEqual(pm25_to_us_aqi(500.4), 500)
        self.assertEqual(pm25_to_us_aqi(600.0), 500)

    def test_pm25_to_us_aqi_intermediate(self):
        # 21.3 µg/m³ should fall in moderate range (51-100)
        aqi = pm25_to_us_aqi(21.3)
        self.assertTrue(51 <= aqi <= 100)

    def test_invalid_pm25(self):
        self.assertEqual(pm25_to_us_aqi(-5), 0)
        self.assertEqual(pm25_to_us_aqi(None), 0)


class ServicesTests(TestCase):
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    @patch("requests.get")
    def test_fetch_weather_reshaping(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "coord": {"lon": 72.8777, "lat": 19.076},
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
            "main": {
                "temp": 25.5,
                "feels_like": 26.2,
                "pressure": 1012,
                "humidity": 65,
                "sea_level": 1013,
            },
            "wind": {"speed": 5.0, "deg": 180},
            "clouds": {"all": 10},
            "dt": 1661850000,
            "sys": {
                "sunrise": 1661830000,
                "sunset": 1661875000,
            },
        }
        mock_get.return_value = mock_response

        data = fetch_weather_from_open_meteo(19.076, 72.8777)

        self.assertIn("current", data)
        self.assertIn("daily", data)

        current = data["current"]
        self.assertEqual(current["temperature_2m"], 25.5)
        self.assertEqual(current["relative_humidity_2m"], 65.0)
        self.assertEqual(current["apparent_temperature"], 26.2)
        # 5.0 m/s * 3.6 = 18.0 km/h
        self.assertEqual(current["wind_speed_10m"], 18.0)
        self.assertEqual(current["wind_direction_10m"], 180.0)
        self.assertEqual(current["weather_code"], 0)
        self.assertEqual(current["is_day"], 1)
        self.assertEqual(current["pressure_msl"], 1013.0)
        self.assertEqual(current["cloud_cover"], 10.0)

        daily = data["daily"]
        self.assertEqual(len(daily["sunrise"]), 1)
        self.assertEqual(len(daily["sunset"]), 1)

        # Test compatibility with save_weather_record
        record = save_weather_record("Mumbai", 19.076, 72.8777, data)
        self.assertIsInstance(record, WeatherRecord)
        self.assertEqual(record.city_name, "Mumbai")
        self.assertEqual(record.wind_speed_10m, 18.0)

        # Test compatibility with ML prediction
        prediction = predict_next_24h(current)
        self.assertIn("predicted_avg_temp_24h", prediction)
        self.assertIn("will_rain_24h", prediction)
        self.assertIn("rain_probability", prediction)

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    @patch("requests.get")
    def test_fetch_weather_missing_deg_and_night(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "coord": {"lon": 72.8777, "lat": 19.076},
            "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
            "main": {
                "temp": 20.0,
                "feels_like": 20.0,
                "pressure": 1010,
                "humidity": 80,
            },
            # Calm wind without 'deg'
            "wind": {"speed": 0.0},
            "clouds": {"all": 90},
            "dt": 1661880000,  # after sunset
            "sys": {
                "sunrise": 1661830000,
                "sunset": 1661875000,
            },
        }
        mock_get.return_value = mock_response

        data = fetch_weather_from_open_meteo(19.076, 72.8777)
        current = data["current"]

        self.assertEqual(current["wind_direction_10m"], 0.0)
        self.assertEqual(current["wind_speed_10m"], 0.0)
        self.assertEqual(current["is_day"], 0)
        self.assertEqual(current["weather_code"], 61)  # WMO 61 for OWM 500
        self.assertEqual(current["pressure_msl"], 1010.0)  # fell back to main.pressure

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    @patch("requests.get")
    def test_geocode_city_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "name": "London",
                "lat": 51.5073,
                "lon": -0.1276,
                "country": "GB",
                "state": "England",
            }
        ]
        mock_get.return_value = mock_response

        result = geocode_city("London")
        self.assertEqual(result, {
            "name": "London",
            "latitude": 51.5073,
            "longitude": -0.1276,
            "country": "GB",
            "admin1": "England",
        })

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    @patch("requests.get")
    def test_geocode_city_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            geocode_city("NonexistentCityXYZ123")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    @patch("requests.get")
    def test_fetch_air_quality_reshaping_and_alerts(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "coord": {"lon": 72.8777, "lat": 19.076},
            "list": [
                {
                    "main": {"aqi": 4},
                    "components": {
                        "pm2_5": 75.0,  # Unhealthy (> 55.4, US AQI will be > 150)
                        "pm10": 120.0,
                    },
                }
            ],
        }
        mock_get.return_value = mock_response

        aq_data = fetch_air_quality_from_open_meteo(19.076, 72.8777)
        self.assertIn("current", aq_data)
        current_aq = aq_data["current"]
        self.assertEqual(current_aq["pm2_5"], 75.0)
        self.assertEqual(current_aq["pm10"], 120.0)
        self.assertTrue(current_aq["us_aqi"] > 150)

        # Test save_air_quality_record
        record = save_air_quality_record("Mumbai", 19.076, 72.8777, aq_data)
        self.assertIsInstance(record, AirQualityRecord)
        self.assertEqual(record.us_aqi, current_aq["us_aqi"])

        # Test generate_alerts_from_weather with poor AQI
        weather_data = {
            "current": {
                "wind_speed_10m": 10.0,
                "temperature_2m": 25.0,
                "weather_code": 0,
            }
        }
        alerts = generate_alerts_from_weather(weather_data, aq_data)
        self.assertTrue(any(a["headline"] == "Poor Air Quality Warning" for a in alerts))

        # Test personalized advice with cyclist and traveler
        advice = generate_personalized_advice(weather_data["current"], current_aq["us_aqi"], ["cyclist", "traveler"])
        self.assertEqual(len(advice), 2)
