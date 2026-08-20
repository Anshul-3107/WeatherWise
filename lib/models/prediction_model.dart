class PredictionModel {
  final double predictedAvgTemp24h;
  final bool willRain24h;
  final double rainProbability;

  PredictionModel({
    required this.predictedAvgTemp24h,
    required this.willRain24h,
    required this.rainProbability,
  });

  factory PredictionModel.fromJson(Map<String, dynamic> json) {
    return PredictionModel(
      predictedAvgTemp24h: (json['predicted_avg_temp_24h'] as num).toDouble(),
      willRain24h: json['will_rain_24h'] as bool,
      rainProbability: (json['rain_probability'] as num).toDouble(),
    );
  }

  String toDisplayText() {
    final tempRounded = predictedAvgTemp24h.round();
    final rainPercent = (rainProbability * 100).round();

    if (willRain24h) {
      return 'Rain is likely in the next 24 hours ($rainPercent% chance). Expect an average temperature around $tempRounded°C.';
    } else {
      return 'Low chance of rain in the next 24 hours ($rainPercent%). Expect an average temperature around $tempRounded°C.';
    }
  }
}