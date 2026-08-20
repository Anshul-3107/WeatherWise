import 'package:flutter/material.dart';
import 'package:weatherwise/core/utils/weather_icon_mapper.dart';
import 'package:weatherwise/models/advice_model.dart';
import 'package:weatherwise/models/air_quality_model.dart';
import 'package:weatherwise/models/prediction_model.dart';
import 'package:weatherwise/models/weather_model.dart';
import 'package:weatherwise/screens/search/search_city_screen.dart';
import 'package:weatherwise/screens/settings/settings_screen.dart';
import 'package:weatherwise/services/storage_service.dart';
import 'package:weatherwise/services/weather_services.dart';
import 'package:weatherwise/widgets/home/location_header.dart';
import 'package:weatherwise/widgets/home/weather_card.dart';
import 'package:weatherwise/widgets/home/ai_prediction_card.dart';
import 'package:weatherwise/widgets/home/personalized_advice_card.dart';
import 'package:weatherwise/widgets/home/air_quality_card.dart';
import 'package:weatherwise/widgets/home/astronomy_card.dart';
import 'package:weatherwise/widgets/home/alert_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final WeatherService _weatherService = WeatherService();
  final StorageService _storageService = StorageService();

  String _cityName = 'Patna';
  double _latitude = 25.5941;
  double _longitude = 85.1376;
  List<String> _selectedProfiles = [];

  WeatherModel? _weather;
  AirQualityModel? _airQuality;
  PredictionModel? _prediction;
  List<AdviceModel> _advice = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initializeCityAndLoadData();
  }

  Future<void> _initializeCityAndLoadData() async {
    final savedCity = await _storageService.getSelectedCity();
    final savedProfiles = await _storageService.getSelectedProfiles();

    if (savedCity != null) {
      _cityName = savedCity['cityName'] as String;
      _latitude = savedCity['latitude'] as double;
      _longitude = savedCity['longitude'] as double;
    }
    _selectedProfiles = savedProfiles;

    await _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await Future.wait([
        _weatherService.fetchCurrentWeather(
          cityName: _cityName,
          latitude: _latitude,
          longitude: _longitude,
        ),
        _weatherService.fetchAirQuality(
          cityName: _cityName,
          latitude: _latitude,
          longitude: _longitude,
        ),
        _weatherService.fetchPrediction(
          latitude: _latitude,
          longitude: _longitude,
        ),
        _weatherService.fetchPersonalizedAdvice(
          latitude: _latitude,
          longitude: _longitude,
          selectedProfiles: _selectedProfiles,
        ),
      ]);

      if (!mounted) return;
      setState(() {
        _weather = results[0] as WeatherModel;
        _airQuality = results[1] as AirQualityModel;
        _prediction = results[2] as PredictionModel;
        _advice = results[3] as List<AdviceModel>;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = 'Could not load weather. Pull down to retry.';
        _isLoading = false;
      });
    }
  }

  Future<void> _handleSearchPressed() async {
    final result = await Navigator.of(context).push<GeocodeResult>(
      MaterialPageRoute(builder: (context) => const SearchCityScreen()),
    );

    if (result != null) {
      setState(() {
        _cityName = result.name;
        _latitude = result.latitude;
        _longitude = result.longitude;
      });

      await _storageService.saveSelectedCity(
        cityName: result.name,
        latitude: result.latitude,
        longitude: result.longitude,
      );

      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('WeatherWise'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: _handleSearchPressed,
            tooltip: 'Search City',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () async {
              await Navigator.of(context).push(
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
              _initializeCityAndLoadData();
            },
            tooltip: 'Settings',
          ),
        ],
      ),
      body: RefreshIndicator(onRefresh: _loadData, child: _buildBody()),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null) {
      return LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.cloud_off,
                        size: 48,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _errorMessage!,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      );
    }

    final weather = _weather!;
    final airQuality = _airQuality!;
    final prediction = _prediction!;

    final adviceText = _advice.isEmpty
        ? 'Select a profile in Settings to see personalized advice.'
        : _advice.map((a) => a.advice).join('\n\n');

    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LocationHeader(cityName: _cityName, greeting: 'Good Morning'),
          const SizedBox(height: 16),
          WeatherCard(
            temperature: '${weather.temperature.round()}°C',
            condition: weather.conditionLabel,
            humidity: '${weather.humidity.round()}%',
            windSpeed: '${weather.windSpeed} km/h',
            icon: getWeatherIcon(weather.iconKey),
          ),
          const SizedBox(height: 16),
          AiPredictionCard(predictionText: prediction.toDisplayText()),
          const SizedBox(height: 16),
          PersonalizedAdviceCard(adviceText: adviceText),
          const SizedBox(height: 16),
          AirQualityCard(
            aqiValue: '${airQuality.usAqi}',
            aqiLabel: airQuality.aqiLabel,
          ),
          const SizedBox(height: 16),
          AlertCard(
            alerts: weather.alerts.map((alert) => alert.headline).toList(),
          ),
          const SizedBox(height: 16),
          AstronomyCard(
            sunrise: TimeOfDay.fromDateTime(weather.sunrise).format(context),
            sunset: TimeOfDay.fromDateTime(weather.sunset).format(context),
            moonrise: '—',
            moonset: '—',
          ),
        ],
      ),
    );
  }
}
