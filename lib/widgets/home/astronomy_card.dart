import 'package:flutter/material.dart';

/// Astronomy section — no outer card chrome, renders inline
/// inside the detail sheet with onSurface colors.
class AstronomyCard extends StatelessWidget {
  final String sunrise;
  final String sunset;
  final String moonrise;
  final String moonset;

  const AstronomyCard({
    super.key,
    required this.sunrise,
    required this.sunset,
    required this.moonrise,
    required this.moonset,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.brightness_4,
              size: 22,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(width: 8),
            Text(
              'Astronomy',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurface,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        _AstronomyRow(
          icon: Icons.wb_sunny_outlined,
          label: 'Sunrise',
          value: sunrise,
        ),
        _AstronomyRow(
          icon: Icons.wb_twilight,
          label: 'Sunset',
          value: sunset,
        ),
        _AstronomyRow(
          icon: Icons.nightlight_outlined,
          label: 'Moonrise',
          value: moonrise,
        ),
        _AstronomyRow(
          icon: Icons.nights_stay_outlined,
          label: 'Moonset',
          value: moonset,
        ),
      ],
    );
  }
}

class _AstronomyRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _AstronomyRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, size: 18, color: theme.colorScheme.onSurfaceVariant),
              const SizedBox(width: 8),
              Text(
                label,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: theme.colorScheme.onSurface,
            ),
          ),
        ],
      ),
    );
  }
}
