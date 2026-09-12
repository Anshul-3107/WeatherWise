import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:weatherwise/models/weather_model.dart';
import 'package:weatherwise/models/air_quality_model.dart';
import 'package:weatherwise/models/prediction_model.dart';
import 'package:weatherwise/models/advice_model.dart';

class GeocodeResult {
  final String name;
  final double latitude;
  final double longitude;
  final String country;

  GeocodeResult({
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.country,
  });

  factory GeocodeResult.fromJson(Map<String, dynamic> json) {
    return GeocodeResult(
      name: json['name'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      country: json['country'] as String? ?? '',
    );
  }
}

class WeatherService {
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/weather',
  );

  static const Duration _timeout = Duration(seconds: 40);

  Future<GeocodeResult> searchCity(String cityName) async {
    final uri = Uri.parse(
      '$_baseUrl/search/?city=${Uri.encodeComponent(cityName)}',
    );

    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      return GeocodeResult.fromJson(jsonData);
    } else if (response.statusCode == 404) {
      throw Exception('City not found');
    } else {
      throw Exception('Failed to search city (${response.statusCode})');
    }
  }

  Future<GeocodeResult> reverseGeocode(double latitude, double longitude) async {
    final uri = Uri.parse(
      '$_baseUrl/reverse-geocode/?lat=$latitude&lon=$longitude',
    );

    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      return GeocodeResult.fromJson(jsonData);
    } else if (response.statusCode == 404) {
      throw Exception('Location not found');
    } else {
      throw Exception('Failed to reverse geocode (${response.statusCode})');
    }
  }

  Future<WeatherModel> fetchCurrentWeather({
    required String cityName,
    required double latitude,
    required double longitude,
  }) async {
    final uri = Uri.parse(
      '$_baseUrl/current/?city=${Uri.encodeComponent(cityName)}&lat=$latitude&lon=$longitude',
    );

    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      return WeatherModel.fromJson(jsonData);
    } else {
      throw Exception('Failed to load weather data (${response.statusCode})');
    }
  }

  Future<AirQualityModel> fetchAirQuality({
    required String cityName,
    required double latitude,
    required double longitude,
  }) async {
    final uri = Uri.parse(
      '$_baseUrl/air-quality/?city=${Uri.encodeComponent(cityName)}&lat=$latitude&lon=$longitude',
    );

    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      return AirQualityModel.fromJson(jsonData);
    } else {
      throw Exception('Failed to load air quality data (${response.statusCode})');
    }
  }

  Future<PredictionModel> fetchPrediction({
    required double latitude,
    required double longitude,
  }) async {
    final uri = Uri.parse(
      '$_baseUrl/predict/?lat=$latitude&lon=$longitude',
    );

    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      return PredictionModel.fromJson(jsonData);
    } else {
      throw Exception('Failed to load prediction (${response.statusCode})');
    }
  }

  Future<List<AdviceModel>> fetchPersonalizedAdvice({
    required double latitude,
    required double longitude,
    required List<String> selectedProfiles,
  }) async {
    final profilesParam = selectedProfiles.join(',');
    final uri = Uri.parse(
      '$_baseUrl/advice/?lat=$latitude&lon=$longitude&profiles=${Uri.encodeComponent(profilesParam)}',
    );

    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      final adviceList = jsonData['advice'] as List<dynamic>;
      return adviceList
          .map((item) => AdviceModel.fromJson(item as Map<String, dynamic>))
          .toList();
    } else {
      throw Exception('Failed to load personalized advice (${response.statusCode})');
    }
  }
}