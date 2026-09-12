import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:weatherwise/core/theme/sky_gradient.dart';
import 'package:weatherwise/core/utils/weather_icon_mapper.dart';
import 'package:weatherwise/models/advice_model.dart';
import 'package:weatherwise/models/air_quality_model.dart';
import 'package:weatherwise/models/prediction_model.dart';
import 'package:weatherwise/models/weather_model.dart';
import 'package:weatherwise/screens/search/search_city_screen.dart';
import 'package:weatherwise/screens/settings/settings_screen.dart';
import 'package:weatherwise/services/storage_service.dart';
import 'package:weatherwise/services/weather_services.dart';
import 'package:weatherwise/widgets/home/ai_prediction_card.dart';
import 'package:weatherwise/widgets/home/alert_card.dart';
import 'package:weatherwise/widgets/home/astronomy_card.dart';
import 'package:weatherwise/widgets/home/personalized_advice_card.dart';
import 'package:weatherwise/widgets/home/weather_card.dart';

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
    _selectedProfiles = savedProfiles;

    if (savedCity != null) {
      _cityName = savedCity['cityName'] as String;
      _latitude = savedCity['latitude'] as double;
      _longitude = savedCity['longitude'] as double;
      await _loadData();
    } else {
      await _getCurrentLocation();
    }
  }

  Future<void> _getCurrentLocation() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        _loadDefaultLocation();
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          _loadDefaultLocation();
          return;
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        _loadDefaultLocation();
        return;
      } 

      final position = await Geolocator.getCurrentPosition();
      
      try {
        final geocodeResult = await _weatherService.reverseGeocode(
          position.latitude,
          position.longitude,
        );
        _cityName = geocodeResult.name;
        _latitude = geocodeResult.latitude;
        _longitude = geocodeResult.longitude;
      } catch (e) {
        _cityName = 'Current Location';
        _latitude = position.latitude;
        _longitude = position.longitude;
      }
      
      await _storageService.saveSelectedCity(
        cityName: _cityName,
        latitude: _latitude,
        longitude: _longitude,
      );

      await _loadData();
    } catch (e) {
      _loadDefaultLocation();
    }
  }

  void _loadDefaultLocation() {
    _cityName = 'Patna';
    _latitude = 25.5941;
    _longitude = 85.1376;
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final weather = await _weatherService.fetchCurrentWeather(
        cityName: _cityName,
        latitude: _latitude,
        longitude: _longitude,
      );

      final aqiFuture = _weatherService.fetchAirQuality(
        cityName: _cityName,
        latitude: _latitude,
        longitude: _longitude,
      ).then<AirQualityModel?>((v) => v).catchError((_) => null);

      final predFuture = _weatherService.fetchPrediction(
        latitude: _latitude,
        longitude: _longitude,
      ).then<PredictionModel?>((v) => v).catchError((_) => null);

      final advFuture = _weatherService.fetchPersonalizedAdvice(
        latitude: _latitude,
        longitude: _longitude,
        selectedProfiles: _selectedProfiles,
      ).then<List<AdviceModel>>((v) => v).catchError((_) => <AdviceModel>[]);

      final extras = await Future.wait([aqiFuture, predFuture, advFuture]);

      if (!mounted) return;
      setState(() {
        _weather = weather;
        _airQuality = extras[0] as AirQualityModel?;
        _prediction = extras[1] as PredictionModel?;
        _advice = extras[2] as List<AdviceModel>;
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
      backgroundColor: Colors.transparent,
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: Colors.white,
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    // Determine gradient — use weather data if available, else clear-day fallback
    final gradientColors = _weather != null
        ? skyGradientFor(iconKey: _weather!.iconKey, isDay: _weather!.isDay)
        : skyGradientFor(iconKey: 'clear', isDay: true);

    if (_isLoading) {
      return Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradientColors,
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: const Center(child: CircularProgressIndicator(color: Colors.white)),
      );
    }

    if (_errorMessage != null) {
      return Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradientColors,
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: LayoutBuilder(
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
                        const Icon(
                          Icons.cloud_off,
                          size: 48,
                          color: Colors.white70,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _errorMessage!,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.white,
                              ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      );
    }

    final weather = _weather!;
    final airQuality = _airQuality!;
    final prediction = _prediction!;

    final adviceText = _advice.isEmpty
        ? 'Select a profile in Settings to see personalized advice.'
        : _advice.map((a) => a.advice).join('\n\n');

    return Stack(
      children: [
        // Layer 1: full-screen gradient background
        Positioned.fill(
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: skyGradientFor(
                  iconKey: weather.iconKey,
                  isDay: weather.isDay,
                ),
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),
        ),
        // Layer 2: scrollable content
        CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            // Top bar
            SliverToBoxAdapter(child: _buildTopBar()),
            // Hero section
            SliverToBoxAdapter(child: _buildHeroSection(weather)),
            // Detail sheet
            SliverToBoxAdapter(
              child: _buildDetailSheet(
                weather: weather,
                airQuality: airQuality,
                prediction: prediction,
                adviceText: adviceText,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTopBar() {
    return SafeArea(
      bottom: false,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          children: [
            const Icon(Icons.location_on, size: 18, color: Colors.white70),
            const SizedBox(width: 4),
            Expanded(
              child: Text(
                _cityName,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                      color: Colors.white,
                    ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.search, color: Colors.white),
              onPressed: _handleSearchPressed,
              tooltip: 'Search City',
            ),
            IconButton(
              icon: const Icon(Icons.settings, color: Colors.white),
              onPressed: () async {
                await Navigator.of(context).push(
                  MaterialPageRoute(
                      builder: (context) => const SettingsScreen()),
                );
                _initializeCityAndLoadData();
              },
              tooltip: 'Settings',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroSection(WeatherModel weather) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 24),
      child: WeatherCard(
        temperature: '${weather.temperature.round()}°C',
        condition: weather.conditionLabel,
        humidity: '${weather.humidity.round()}%',
        windSpeed: '${weather.windSpeed} km/h',
        icon: getWeatherIcon(weather.iconKey),
      ),
    );
  }

  Widget _buildDetailSheet({
    required WeatherModel weather,
    required AirQualityModel airQuality,
    required PredictionModel prediction,
    required String adviceText,
  }) {
    final theme = Theme.of(context);

    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(28),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 28, 20, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag indicator
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Stats grid (2x2)
            _buildStatsGrid(weather, airQuality, theme),

            _sectionDivider(theme),

            // AI Prediction
            AiPredictionCard(predictionText: prediction.toDisplayText()),

            _sectionDivider(theme),

            // Personalized Advice
            PersonalizedAdviceCard(adviceText: adviceText),

            _sectionDivider(theme),

            // Alerts
            AlertCard(
              alerts:
                  weather.alerts.map((alert) => alert.headline).toList(),
            ),
            // Only add divider after alerts if there are alerts
            if (weather.alerts.isNotEmpty) _sectionDivider(theme),

            // Astronomy
            AstronomyCard(
              sunrise:
                  TimeOfDay.fromDateTime(weather.sunrise).format(context),
              sunset:
                  TimeOfDay.fromDateTime(weather.sunset).format(context),
              moonrise: weather.moonrise != null
                  ? TimeOfDay.fromDateTime(weather.moonrise!).format(context)
                  : '—',
              moonset: weather.moonset != null
                  ? TimeOfDay.fromDateTime(weather.moonset!).format(context)
                  : '—',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsGrid(
    WeatherModel weather,
    AirQualityModel airQuality,
    ThemeData theme,
  ) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _StatTile(
                icon: Icons.water_drop,
                value: '${weather.humidity.round()}%',
                label: 'Humidity',
                theme: theme,
              ),
            ),
            Expanded(
              child: _StatTile(
                icon: Icons.air,
                value: '${weather.windSpeed} km/h',
                label: 'Wind',
                theme: theme,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _StatTile(
                icon: Icons.eco,
                value: '${airQuality.usAqi}',
                label: 'AQI',
                theme: theme,
              ),
            ),
            Expanded(
              child: _StatTile(
                icon: Icons.thermostat,
                value: '${weather.apparentTemperature.round()}°C',
                label: 'Feels like',
                theme: theme,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _sectionDivider(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Divider(
        height: 1,
        color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
      ),
    );
  }
}

/// A single stat tile in the 2x2 grid inside the detail sheet.
class _StatTile extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final ThemeData theme;

  const _StatTile({
    required this.icon,
    required this.value,
    required this.label,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20, color: theme.colorScheme.primary),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface,
              ),
            ),
            Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
