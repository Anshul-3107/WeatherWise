class AirQualityModel {
  final int usAqi;
  final String aqiLabel;
  final double pm25;
  final double pm10;

  AirQualityModel({
    required this.usAqi,
    required this.aqiLabel,
    required this.pm25,
    required this.pm10,
  });

  factory AirQualityModel.fromJson(Map<String, dynamic> json) {
    return AirQualityModel(
      usAqi: json['us_aqi'] as int,
      aqiLabel: json['aqi_label'] as String,
      pm25: (json['pm2_5'] as num).toDouble(),
      pm10: (json['pm10'] as num).toDouble(),
    );
  }
}