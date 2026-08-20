import 'package:flutter/material.dart';

IconData getWeatherIcon(String iconKey) {
  switch (iconKey) {
    case 'clear':
      return Icons.wb_sunny;
    case 'partly_cloudy':
      return Icons.wb_cloudy;
    case 'cloudy':
      return Icons.cloud;
    case 'fog':
      return Icons.foggy;
    case 'drizzle':
      return Icons.grain;
    case 'rain':
      return Icons.water_drop;
    case 'rain_showers':
      return Icons.beach_access;
    case 'snow':
    case 'snow_showers':
      return Icons.ac_unit;
    case 'thunderstorm':
      return Icons.thunderstorm;
    default:
      return Icons.wb_sunny;
  }
}