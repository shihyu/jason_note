import 'package:flutter/material.dart';
import 'simple_test_page.dart';

void main() {
  print('[BitoPro Flutter] Starting application...');
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BitoPro Rust-Flutter Test',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const SimpleTestPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}