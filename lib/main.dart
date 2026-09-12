import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:weatherwise/core/theme/theme_provider.dart';
import 'package:weatherwise/screens/home/home_screen.dart';
import 'package:weatherwise/screens/profile/profile_selection_screen.dart';
import 'package:weatherwise/services/storage_service.dart';

void main() {
  runApp(const ProviderScope(child: WeatherWiseApp()));
}

class WeatherWiseApp extends ConsumerWidget {
  const WeatherWiseApp({super.key});

  static const _seedColor = Color(0xFF5B9FD9);

  /// Merges Sora (display) + Inter (body/label/title) onto the default
  /// Material text theme so that all 13 styles stay populated.
  static TextTheme _buildTextTheme(TextTheme base) {
    final interTheme = GoogleFonts.interTextTheme(base);
    final soraTheme = GoogleFonts.soraTextTheme(base);

    return interTheme.copyWith(
      displayLarge: soraTheme.displayLarge,
      displayMedium: soraTheme.displayMedium,
      displaySmall: soraTheme.displaySmall,
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);

    final lightBase = ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: _seedColor,
        brightness: Brightness.light,
      ),
      useMaterial3: true,
    );

    final darkBase = ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: _seedColor,
        brightness: Brightness.dark,
      ),
      useMaterial3: true,
    );

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'WeatherWise',
      theme: lightBase.copyWith(
        textTheme: _buildTextTheme(lightBase.textTheme),
      ),
      darkTheme: darkBase.copyWith(
        textTheme: _buildTextTheme(darkBase.textTheme),
      ),
      themeMode: themeMode,
      home: const StartupRouter(),
    );
  }
}

class StartupRouter extends StatelessWidget {
  const StartupRouter({super.key});

  @override
  Widget build(BuildContext context) {
    final storageService = StorageService();

    return FutureBuilder<bool>(
      future: storageService.hasSelectedProfile(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        final hasSelected = snapshot.data ?? false;
        return hasSelected
            ? const HomeScreen()
            : const ProfileSelectionScreen(isInitialSetup: true);
      },
    );
  }
}
