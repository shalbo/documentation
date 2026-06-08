import 'package:flutter_test/flutter_test.dart';
import 'package:rousto/main.dart';

void main() {
  testWidgets('شاشة الترحيب تعرض نص البداية', (WidgetTester tester) async {
    await tester.pumpWidget(const RoustoApp());
    await tester.pump();

    expect(find.text('عناية ذكية بسيارتك'), findsOneWidget);
    expect(find.text('ابدأ الآن'), findsOneWidget);
  });

  testWidgets('الانتقال من الترحيب إلى الرئيسية', (WidgetTester tester) async {
    await tester.pumpWidget(const RoustoApp());
    await tester.pump();

    await tester.tap(find.text('ابدأ الآن'));
    await tester.pumpAndSettle();

    expect(find.text('الخدمات الشائعة'), findsOneWidget);
  });
}
