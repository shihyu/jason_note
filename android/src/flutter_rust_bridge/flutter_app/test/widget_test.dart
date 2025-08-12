// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_app/main.dart';

void main() {
  testWidgets('BitoPro Rust-Flutter Test App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();

    expect(find.text('BitoPro Rust-Flutter 測試'), findsOneWidget);
    expect(find.text('雙向溝通測試'), findsOneWidget);
    expect(find.text('測試數字加法'), findsOneWidget);
    expect(find.text('測試訊息處理'), findsOneWidget);
    expect(find.text('測試系統資訊'), findsOneWidget);
    expect(find.text('執行所有測試'), findsOneWidget);
    expect(find.text('狀態'), findsOneWidget);
    expect(find.text('最新結果'), findsOneWidget);
  });
}
