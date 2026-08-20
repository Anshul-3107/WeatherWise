from django.contrib import admin
from .models import WeatherRecord, AirQualityRecord



@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'temperature_2m', 'weather_code', 'fetched_at')
    list_filter = ('city_name',)
    ordering = ('-fetched_at',)
    
@admin.register(AirQualityRecord)
class AirQualityRecordAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'us_aqi', 'fetched_at')
    ordering = ('-fetched_at',)