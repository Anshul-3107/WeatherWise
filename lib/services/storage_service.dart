import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _hasSelectedProfileKey = 'has_selected_profile';
  static const String _selectedProfilesKey = 'selected_profiles';
  static const String _cityNameKey = 'city_name';
  static const String _cityLatKey = 'city_lat';
  static const String _cityLonKey = 'city_lon';

  Future<bool> hasSelectedProfile() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_hasSelectedProfileKey) ?? false;
  }

  Future<void> saveSelectedProfiles(List<String> profileIds) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_selectedProfilesKey, profileIds);
    await prefs.setBool(_hasSelectedProfileKey, true);
  }

  Future<List<String>> getSelectedProfiles() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_selectedProfilesKey) ?? [];
  }

  Future<void> saveSelectedCity({
    required String cityName,
    required double latitude,
    required double longitude,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_cityNameKey, cityName);
    await prefs.setDouble(_cityLatKey, latitude);
    await prefs.setDouble(_cityLonKey, longitude);
  }

  Future<Map<String, dynamic>?> getSelectedCity() async {
    final prefs = await SharedPreferences.getInstance();
    final cityName = prefs.getString(_cityNameKey);
    final lat = prefs.getDouble(_cityLatKey);
    final lon = prefs.getDouble(_cityLonKey);

    if (cityName == null || lat == null || lon == null) {
      return null;
    }

    return {
      'cityName': cityName,
      'latitude': lat,
      'longitude': lon,
    };
  }
}