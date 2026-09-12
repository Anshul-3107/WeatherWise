import 'package:flutter/material.dart';

/// Slim top-bar header — city name with location pin, rendered
/// directly on the gradient (white text, no card background).
class LocationHeader extends StatelessWidget {
  final String cityName;
  final String greeting;

  const LocationHeader({
    super.key,
    required this.cityName,
    required this.greeting,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(Icons.location_on, size: 18, color: Colors.white70),
        const SizedBox(width: 4),
        Text(
          cityName,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
        ),
      ],
    );
  }
}
