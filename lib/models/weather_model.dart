class WeatherAlert {
  final String headline;
  final String description;
  final String severity;

  WeatherAlert({
    required this.headline,
    required this.description,
    required this.severity,
  });

  factory WeatherAlert.fromJson(Map<String, dynamic> json) {
    return WeatherAlert(
      headline: json['headline'] as String,
      description: json['description'] as String,
      severity: json['severity'] as String,
    );
  }
}

class WeatherModel {
  final String cityName;
  final double temperature;
  final double humidity;
  final double windSpeed;
  final double apparentTemperature;
  final int weatherCode;
  final String conditionLabel;
  final String iconKey;
  final bool isDay;
  final DateTime sunrise;
  final DateTime sunset;
  final DateTime? moonrise;
  final DateTime? moonset;
  final String? moonPhaseLabel;
  final List<WeatherAlert> alerts;

  WeatherModel({
    required this.cityName,
    required this.temperature,
    required this.humidity,
    required this.windSpeed,
    required this.apparentTemperature,
    required this.weatherCode,
    required this.conditionLabel,
    required this.iconKey,
    required this.isDay,
    required this.sunrise,
    required this.sunset,
    this.moonrise,
    this.moonset,
    this.moonPhaseLabel,
    required this.alerts,
  });

  factory WeatherModel.fromJson(Map<String, dynamic> json) {
    final alertsJson = json['alerts'] as List<dynamic>? ?? [];

    return WeatherModel(
      cityName: json['city_name'] as String,
      temperature: (json['temperature_2m'] as num).toDouble(),
      humidity: (json['relative_humidity_2m'] as num).toDouble(),
      windSpeed: (json['wind_speed_10m'] as num).toDouble(),
      apparentTemperature: (json['apparent_temperature'] as num).toDouble(),
      weatherCode: json['weather_code'] as int,
      conditionLabel: json['condition_label'] as String,
      iconKey: json['icon_key'] as String,
      isDay: json['is_day'] as bool,
      sunrise: DateTime.parse(json['sunrise'] as String),
      sunset: DateTime.parse(json['sunset'] as String),
      moonrise: json['moonrise'] != null ? DateTime.parse(json['moonrise'] as String) : null,
      moonset: json['moonset'] != null ? DateTime.parse(json['moonset'] as String) : null,
      moonPhaseLabel: json['moon_phase_label'] as String?,
      alerts: alertsJson
          .map((item) => WeatherAlert.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}