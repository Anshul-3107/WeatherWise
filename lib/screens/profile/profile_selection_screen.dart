import 'package:flutter/material.dart';
import 'package:weatherwise/screens/location/location_permission_screen.dart';
import 'package:weatherwise/services/storage_service.dart';

class ProfileSelectionScreen extends StatefulWidget {
  final bool isInitialSetup;

  const ProfileSelectionScreen({
    super.key,
    this.isInitialSetup = false,
  });

  @override
  State<ProfileSelectionScreen> createState() =>
      _ProfileSelectionScreenState();
}

class _ProfileSelectionScreenState extends State<ProfileSelectionScreen> {
  final List<_ProfileOption> _profiles = const [
    _ProfileOption(id: 'pilot', label: 'Pilot', icon: Icons.flight),
    _ProfileOption(id: 'farmer', label: 'Farmer', icon: Icons.agriculture),
    _ProfileOption(id: 'traveler', label: 'Traveler', icon: Icons.luggage),
    _ProfileOption(id: 'cyclist', label: 'Cyclist', icon: Icons.pedal_bike),
    _ProfileOption(id: 'student', label: 'Student', icon: Icons.school),
  ];

  final Set<String> _selectedIds = {};
  final StorageService _storageService = StorageService();
  bool _isSaving = false;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadExistingSelection();
  }

  Future<void> _loadExistingSelection() async {
    final saved = await _storageService.getSelectedProfiles();
    setState(() {
      _selectedIds.addAll(saved);
      _isLoading = false;
    });
  }

  void _toggleProfile(String id, bool? checked) {
    setState(() {
      if (checked == true) {
        _selectedIds.add(id);
      } else {
        _selectedIds.remove(id);
      }
    });
  }

  Future<void> _handleSave() async {
    setState(() => _isSaving = true);

    await _storageService.saveSelectedProfiles(_selectedIds.toList());

    if (!mounted) return;

    if (widget.isInitialSetup) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => const LocationPermissionScreen(),
        ),
      );
    } else {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Select Profiles')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Choose the profiles that match your needs. '
              'You can select more than one.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: _profiles.length,
                itemBuilder: (context, index) {
                  final profile = _profiles[index];
                  final isSelected = _selectedIds.contains(profile.id);

                  return CheckboxListTile(
                    value: isSelected,
                    onChanged: (checked) =>
                        _toggleProfile(profile.id, checked),
                    title: Text(profile.label),
                    secondary: Icon(profile.icon),
                    controlAffinity: ListTileControlAffinity.trailing,
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: (_selectedIds.isEmpty || _isSaving)
                    ? null
                    : _handleSave,
                child: _isSaving
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Save'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProfileOption {
  final String id;
  final String label;
  final IconData icon;

  const _ProfileOption({
    required this.id,
    required this.label,
    required this.icon,
  });
}