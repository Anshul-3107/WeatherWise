import 'package:flutter/material.dart';

/// Alert section — no outer card chrome, but uses a colored left border
/// strip as a visual warning accent. Renders inline inside the detail sheet.
class AlertCard extends StatelessWidget {
  final List<String> alerts;

  const AlertCard({super.key, required this.alerts});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (alerts.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.only(left: 12, top: 4, bottom: 4),
      decoration: BoxDecoration(
        border: Border(
          left: BorderSide(
            color: theme.colorScheme.error,
            width: 4,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.warning_amber_rounded,
                size: 22,
                color: theme.colorScheme.error,
              ),
              const SizedBox(width: 8),
              Text(
                'Weather Alerts',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...alerts.map(
            (alert) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Text(
                '• $alert',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
