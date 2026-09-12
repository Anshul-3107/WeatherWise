from rest_framework import serializers
from .models import WeatherRecord, AirQualityRecord
from .utils import get_weather_condition_label, get_weather_icon_key, get_aqi_label


class WeatherRecordSerializer(serializers.ModelSerializer):
    condition_label = serializers.SerializerMethodField()
    icon_key = serializers.SerializerMethodField()
    moon_phase_label = serializers.SerializerMethodField()

    class Meta:
        model = WeatherRecord
        fields = '__all__'

    def get_condition_label(self, obj):
        return get_weather_condition_label(obj.weather_code)

    def get_icon_key(self, obj):
        return get_weather_icon_key(obj.weather_code)
        
    def get_moon_phase_label(self, obj):
        if obj.moon_phase is None:
            return None
        phase = obj.moon_phase
        if phase < 1.0 or phase > 27.0:
            return "New Moon"
        elif phase < 6.5:
            return "Waxing Crescent"
        elif phase < 7.5:
            return "First Quarter"
        elif phase < 13.5:
            return "Waxing Gibbous"
        elif phase < 15.5:
            return "Full Moon"
        elif phase < 20.5:
            return "Waning Gibbous"
        elif phase < 21.5:
            return "Last Quarter"
        else:
            return "Waning Crescent"
    
class AirQualityRecordSerializer(serializers.ModelSerializer):
    aqi_label = serializers.SerializerMethodField()

    class Meta:
        model = AirQualityRecord
        fields = '__all__'

    def get_aqi_label(self, obj):
        return get_aqi_label(obj.us_aqi)