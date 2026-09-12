import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:weatherwise/main.dart';

void main() {
  testWidgets('WeatherWiseApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: WeatherWiseApp(),
      ),
    );
    expect(find.byType(WeatherWiseApp), findsOneWidget);
  });
}
