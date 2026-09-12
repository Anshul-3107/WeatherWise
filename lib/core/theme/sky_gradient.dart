import 'dart:ui';

/// Returns a 2-color gradient (top → bottom) for the sky background
/// based on the weather icon key and day/night state.
///
/// The [iconKey] values match those used by [getWeatherIcon] in
/// `weather_icon_mapper.dart`.
List<Color> skyGradientFor({required String iconKey, required bool isDay}) {
  switch (iconKey) {
    case 'clear':
      return isDay
          ? [const Color(0xFF5B9FD9), const Color(0xFFE8F4FF)]
          : [const Color(0xFF0D1B3E), const Color(0xFF2C3E6B)];

    case 'partly_cloudy':
    case 'cloudy':
      return isDay
          ? [const Color(0xFF7A8B9E), const Color(0xFFC9D2DB)]
          : [const Color(0xFF1B2436), const Color(0xFF3A4459)];

    case 'fog':
    case 'drizzle':
    case 'rain':
    case 'rain_showers':
      return isDay
          ? [const Color(0xFF3B4A5A), const Color(0xFF6B7F91)]
          : [const Color(0xFF14202B), const Color(0xFF2E3D4A)];

    case 'thunderstorm':
      return [const Color(0xFF1A1F2E), const Color(0xFF3E3557)];

    case 'snow':
    case 'snow_showers':
      return isDay
          ? [const Color(0xFF8FA8C4), const Color(0xFFEEF2F7)]
          : [const Color(0xFF243449), const Color(0xFF4A5A70)];

    default:
      // Fallback: clear-day gradient
      return [const Color(0xFF5B9FD9), const Color(0xFFE8F4FF)];
  }
}
