import time
import requests
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from weather.models import HistoricalWeatherRecord


TRAINING_CITIES = [
    {"name": "Patna", "latitude": 25.5941, "longitude": 85.1376},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Delhi", "latitude": 28.7041, "longitude": 77.1025},
    {"name": "Bangalore", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
    {"name": "Jaipur", "latitude": 26.9124, "longitude": 75.7873},
]

HISTORICAL_API_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "wind_speed_10m",
    "wind_direction_10m",
    "weather_code",
    "precipitation",
    "pressure_msl",
    "cloud_cover",
]


class Command(BaseCommand):
    help = "Collects historical weather data for training the ML prediction model."

    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            type=int,
            default=2,
            help='Number of years of historical data to collect (default: 2)',
        )

    def handle(self, *args, **options):
        years = options['years']
        end_date = date.today()
        start_date = end_date - relativedelta(years=years)

        self.stdout.write(f"Collecting {years} year(s) of data from {start_date} to {end_date}")
        self.stdout.write(f"Cities: {', '.join(c['name'] for c in TRAINING_CITIES)}")

        total_saved = 0

        for city in TRAINING_CITIES:
            self.stdout.write(f"\n--- {city['name']} ---")
            current_start = start_date

            while current_start < end_date:
                current_end = min(current_start + relativedelta(months=1), end_date)

                saved_count = self._fetch_and_save_month(
                    city_name=city['name'],
                    latitude=city['latitude'],
                    longitude=city['longitude'],
                    start=current_start,
                    end=current_end,
                )
                total_saved += saved_count

                self.stdout.write(
                    f"  {current_start} to {current_end}: {saved_count} records saved"
                )

                current_start = current_end
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS(f"\nDone. Total records saved: {total_saved}"))

    def _fetch_and_save_month(self, city_name, latitude, longitude, start, end):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": HOURLY_VARIABLES,
            "timezone": "auto",
        }

        try:
            response = requests.get(HISTORICAL_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"  Failed to fetch: {e}"))
            return 0

        hourly = data.get("hourly")
        if not hourly:
            return 0

        times = hourly.get("time", [])
        saved_count = 0

        existing_times = set(
            HistoricalWeatherRecord.objects.filter(
                city_name=city_name,
                recorded_at__gte=start,
                recorded_at__lt=end,
            ).values_list('recorded_at', flat=True)
        )

        records_to_create = []
        for i, time_str in enumerate(times):
            recorded_at = time_str

            if recorded_at in existing_times:
                continue

            try:
                records_to_create.append(HistoricalWeatherRecord(
                    city_name=city_name,
                    latitude=latitude,
                    longitude=longitude,
                    recorded_at=recorded_at,
                    temperature_2m=hourly["temperature_2m"][i],
                    relative_humidity_2m=hourly["relative_humidity_2m"][i],
                    apparent_temperature=hourly["apparent_temperature"][i],
                    wind_speed_10m=hourly["wind_speed_10m"][i],
                    wind_direction_10m=hourly["wind_direction_10m"][i],
                    weather_code=hourly["weather_code"][i],
                    precipitation=hourly["precipitation"][i],
                    pressure_msl=hourly["pressure_msl"][i],
                    cloud_cover=hourly["cloud_cover"][i],
                ))
            except (KeyError, IndexError, TypeError):
                continue

        if records_to_create:
            HistoricalWeatherRecord.objects.bulk_create(records_to_create)
            saved_count = len(records_to_create)

        return saved_count