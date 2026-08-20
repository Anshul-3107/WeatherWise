from django.db import models


class WeatherRecord(models.Model):
    city_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    temperature_2m = models.FloatField(help_text="°C")
    relative_humidity_2m = models.FloatField(help_text="%")
    apparent_temperature = models.FloatField(help_text="°C, feels-like")
    wind_speed_10m = models.FloatField(help_text="km/h")
    wind_direction_10m = models.FloatField(help_text="degrees")
    weather_code = models.IntegerField(help_text="WMO weather interpretation code")
    is_day = models.BooleanField(default=True)

    sunrise = models.DateTimeField(null=True, blank=True)
    sunset = models.DateTimeField(null=True, blank=True)

    moonrise = models.DateTimeField(null=True, blank=True)
    moonset = models.DateTimeField(null=True, blank=True)

    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city_name} @ {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-fetched_at']


class AirQualityRecord(models.Model):
    city_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    us_aqi = models.IntegerField(help_text="US Air Quality Index (0-500)")
    pm2_5 = models.FloatField(help_text="PM2.5 concentration, µg/m³")
    pm10 = models.FloatField(help_text="PM10 concentration, µg/m³")

    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city_name} AQI={self.us_aqi} @ {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-fetched_at']


class HistoricalWeatherRecord(models.Model):
    """
    Training data for the ML prediction model. Each row represents one
    historical hour of weather at a given city, used to teach the model
    patterns between conditions and outcomes.
    """
    city_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    recorded_at = models.DateTimeField(help_text="The actual historical timestamp this data represents")

    temperature_2m = models.FloatField()
    relative_humidity_2m = models.FloatField()
    apparent_temperature = models.FloatField()
    wind_speed_10m = models.FloatField()
    wind_direction_10m = models.FloatField()
    weather_code = models.IntegerField()
    precipitation = models.FloatField(help_text="mm, actual recorded precipitation")
    pressure_msl = models.FloatField(help_text="hPa, mean sea level pressure")
    cloud_cover = models.FloatField(help_text="%")

    class Meta:
        ordering = ['city_name', 'recorded_at']
        indexes = [
            models.Index(fields=['city_name', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.city_name} @ {self.recorded_at}"