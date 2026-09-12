import 'package:flutter/material.dart';

/// Stripped-down weather card for the hero section — renders directly
/// on the sky gradient with no container/card background.
class WeatherCard extends StatelessWidget {
  final String temperature;
  final String condition;
  final String humidity;
  final String windSpeed;
  final IconData icon;

  const WeatherCard({
    super.key,
    required this.temperature,
    required this.condition,
    required this.humidity,
    required this.windSpeed,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Icon(
          icon,
          size: 64,
          color: Colors.white,
        ),
        const SizedBox(height: 8),
        Text(
          temperature,
          style: Theme.of(context).textTheme.displayLarge?.copyWith(
                fontSize: 76,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
        ),
        Text(
          condition,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.white.withValues(alpha: 0.9),
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 20),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _HeroStat(
              icon: Icons.water_drop,
              value: humidity,
            ),
            const SizedBox(width: 32),
            _HeroStat(
              icon: Icons.air,
              value: windSpeed,
            ),
          ],
        ),
      ],
    );
  }
}

class _HeroStat extends StatelessWidget {
  final IconData icon;
  final String value;

  const _HeroStat({
    required this.icon,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          size: 18,
          color: Colors.white70,
        ),
        const SizedBox(width: 6),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.white.withValues(alpha: 0.85),
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }
}