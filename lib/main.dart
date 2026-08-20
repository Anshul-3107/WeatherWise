import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:weatherwise/core/theme/theme_provider.dart';
import 'package:weatherwise/screens/home/home_screen.dart';
import 'package:weatherwise/screens/profile/profile_selection_screen.dart';
import 'package:weatherwise/services/storage_service.dart';

void main() {
  runApp(const ProviderScope(child: WeatherWiseApp()));
}

class WeatherWiseApp extends ConsumerWidget {
  const WeatherWiseApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'WeatherWise',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
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
