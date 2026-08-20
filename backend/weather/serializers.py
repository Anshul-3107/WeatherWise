from rest_framework import serializers
from .models import WeatherRecord, AirQualityRecord
from .utils import get_weather_condition_label, get_weather_icon_key, get_aqi_label


class WeatherRecordSerializer(serializers.ModelSerializer):
    condition_label = serializers.SerializerMethodField()
    icon_key = serializers.SerializerMethodField()

    class Meta:
        model = WeatherRecord
        fields = '__all__'

    def get_condition_label(self, obj):
        return get_weather_condition_label(obj.weather_code)

    def get_icon_key(self, obj):
        return get_weather_icon_key(obj.weather_code)
    
class AirQualityRecordSerializer(serializers.ModelSerializer):
    aqi_label = serializers.SerializerMethodField()

    class Meta:
        model = AirQualityRecord
        fields = '__all__'

    def get_aqi_label(self, obj):
        return get_aqi_label(obj.us_aqi)