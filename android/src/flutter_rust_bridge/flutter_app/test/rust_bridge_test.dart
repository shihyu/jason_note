import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/rust_bridge.dart';

void main() {
  group('RustBridge Tests', () {
    late RustBridge rustBridge;

    setUp(() {
      rustBridge = RustBridge();
    });

    test('should add two numbers correctly', () async {
      final result = await rustBridge.addNumbers(5, 3);
      expect(result, equals(8));
    });

    test('should add negative numbers correctly', () async {
      final result = await rustBridge.addNumbers(-2, 7);
      expect(result, equals(5));
    });

    test('should handle zero addition', () async {
      final result = await rustBridge.addNumbers(0, 0);
      expect(result, equals(0));
    });

    test('should process message successfully', () async {
      final message = {
        'id': 1,
        'content': 'Hello from Flutter test',
        'timestamp': 1234567890,
      };

      final result = await rustBridge.processMessage(message);
      
      expect(result['success'], isTrue);
      expect(result['data'], isNotNull);
      expect(result['data'], contains('Processed: Hello from Flutter test'));
      expect(result['error'], isNull);
    });

    test('should handle invalid message format', () async {
      final invalidMessage = {
        'invalid_field': 'test',
      };

      final result = await rustBridge.processMessage(invalidMessage);
      
      expect(result['success'], isFalse);
      expect(result['error'], isNotNull);
      expect(result['error'], contains('missing field'));
    });

    test('should get system info', () async {
      final systemInfo = await rustBridge.getSystemInfo();
      
      expect(systemInfo, isNotNull);
      expect(systemInfo, contains('Rust Version'));
      expect(systemInfo, contains('OS:'));
      expect(systemInfo, contains('Arch:'));
    });

    test('should handle multiple concurrent calls', () async {
      final futures = <Future<int>>[];
      
      for (int i = 0; i < 10; i++) {
        futures.add(rustBridge.addNumbers(i, i + 1));
      }
      
      final results = await Future.wait(futures);
      
      for (int i = 0; i < 10; i++) {
        expect(results[i], equals(i + i + 1));
      }
    });

    test('should handle large numbers', () async {
      const largeNumber = 1000000;
      final result = await rustBridge.addNumbers(largeNumber, largeNumber);
      expect(result, equals(2000000));
    });

    test('should process complex message with special characters', () async {
      final message = {
        'id': 999,
        'content': 'Test with 特殊字符 and émojis 🚀',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };

      final result = await rustBridge.processMessage(message);
      
      expect(result['success'], isTrue);
      expect(result['data'], contains('特殊字符'));
      expect(result['data'], contains('🚀'));
    });
  });
}