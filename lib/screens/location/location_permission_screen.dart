import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:weatherwise/screens/home/home_screen.dart';
import 'package:weatherwise/services/storage_service.dart';

class LocationPermissionScreen extends StatefulWidget {
  const LocationPermissionScreen({super.key});

  @override
  State<LocationPermissionScreen> createState() =>
      _LocationPermissionScreenState();
}

class _LocationPermissionScreenState extends State<LocationPermissionScreen> {
  final StorageService _storageService = StorageService();
  bool _isRequesting = false;
  String? _errorText;

  Future<void> _requestLocationAndContinue() async {
    setState(() {
      _isRequesting = true;
      _errorText = null;
    });

    try {
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _isRequesting = false;
          _errorText =
              'Location services are turned off. Please enable them in device settings.';
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();

      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        _continueWithoutLocation();
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.medium,
        ),
      );

      await _storageService.saveSelectedCity(
        cityName: 'Current Location',
        latitude: position.latitude,
        longitude: position.longitude,
      );

      _goToHome();
    } catch (e) {
      setState(() {
        _isRequesting = false;
        _errorText = 'Could not get your location. You can search manually instead.';
      });
    }
  }

  void _continueWithoutLocation() {
    _goToHome();
  }

  void _goToHome() {
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (context) => const HomeScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Icon(
                Icons.location_on,
                size: 64,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(height: 24),
              Text(
                'Enable Location',
                textAlign: TextAlign.center,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Allow WeatherWise to access your location to show weather for where you are.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              if (_errorText != null) ...[
                const SizedBox(height: 16),
                Text(
                  _errorText!,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.error,
                  ),
                ),
              ],
              const SizedBox(height: 32),
              FilledButton(
                onPressed: _isRequesting ? null : _requestLocationAndContinue,
                child: _isRequesting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Allow Location Access'),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: _isRequesting ? null : _continueWithoutLocation,
                child: const Text('Search Manually Instead'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}