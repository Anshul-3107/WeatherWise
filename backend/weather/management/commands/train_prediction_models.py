import pandas as pd
import numpy as np
from datetime import timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import joblib
from weather.models import HistoricalWeatherRecord


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

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "ml_models"


class Command(BaseCommand):
    help = "Trains RandomForest models to predict next-24h temperature and rain likelihood."

    def handle(self, *args, **options):
        self.stdout.write("Loading historical data from database...")

        records = HistoricalWeatherRecord.objects.all().order_by('city_name', 'recorded_at').values(
            'city_name', 'recorded_at', *FEATURE_COLUMNS
        )
        df = pd.DataFrame.from_records(records)

        if df.empty:
            self.stdout.write(self.style.ERROR("No historical data found. Run collect_historical_data first."))
            return

        self.stdout.write(f"Loaded {len(df)} rows across {df['city_name'].nunique()} cities.")
        self.stdout.write("Building training examples (this may take a moment)...")

        training_rows = self._build_training_examples(df)

        if training_rows.empty:
            self.stdout.write(self.style.ERROR("No valid training examples could be built."))
            return

        self.stdout.write(f"Built {len(training_rows)} training examples.")

        self._train_temperature_model(training_rows)
        self._train_rain_model(training_rows)

        self.stdout.write(self.style.SUCCESS("\nDone. Models saved to ml_models/"))

    def _build_training_examples(self, df):
        """
        For each hourly record, looks 24 hours ahead within the same city
        to find the actual outcome (avg temp, whether it rained), and pairs
        it with the current hour's conditions as features.
        """
        df = df.copy()
        df['recorded_at'] = pd.to_datetime(df['recorded_at'])
        df['is_rain_code'] = df['weather_code'].isin(RAIN_WEATHER_CODES)

        all_examples = []

        for city in df['city_name'].unique():
            city_df = df[df['city_name'] == city].sort_values('recorded_at').reset_index(drop=True)
            city_df = city_df.set_index('recorded_at')

            for idx, row in city_df.iterrows():
                window_start = idx
                window_end = idx + timedelta(hours=24)

                future_window = city_df.loc[window_start:window_end]

                if len(future_window) < 20:
                    continue

                avg_temp_next_24h = future_window['temperature_2m'].mean()
                rained_next_24h = bool(future_window['is_rain_code'].any())

                example = {col: row[col] for col in FEATURE_COLUMNS}
                example['target_avg_temp_24h'] = avg_temp_next_24h
                example['target_rain_24h'] = rained_next_24h
                all_examples.append(example)

        return pd.DataFrame(all_examples)

    def _train_temperature_model(self, data):
        self.stdout.write("\nTraining temperature regression model...")

        X = data[FEATURE_COLUMNS]
        y = data['target_avg_temp_24h']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        self.stdout.write(f"  Temperature model MAE: {mae:.2f}°C")

        MODELS_DIR.mkdir(exist_ok=True)
        joblib.dump(model, MODELS_DIR / "temperature_model.joblib", compress=3)
        self.stdout.write("  Saved: temperature_model.joblib (compressed)")

    def _train_rain_model(self, data):
        self.stdout.write("\nTraining rain classification model...")

        X = data[FEATURE_COLUMNS]
        y = data['target_rain_24h']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        self.stdout.write(f"  Rain model accuracy: {accuracy:.2%}")

        MODELS_DIR.mkdir(exist_ok=True)
        joblib.dump(model, MODELS_DIR / "rain_model.joblib", compress=3)
        self.stdout.write("  Saved: rain_model.joblib (compressed)")