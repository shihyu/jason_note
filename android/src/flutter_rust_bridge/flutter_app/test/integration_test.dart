import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/rust_bridge.dart';

void main() {
  group('Rust-Flutter Integration Tests', () {
    late RustBridge rustBridge;

    setUpAll(() {
      rustBridge = RustBridge();
    });

    group('Bidirectional Communication', () {
      test('should handle complex data flow from Flutter to Rust and back', () async {
        final messages = [
          {
            'id': 1,
            'content': 'First message',
            'timestamp': DateTime.now().millisecondsSinceEpoch,
          },
          {
            'id': 2,
            'content': 'Second message with special chars: 測試',
            'timestamp': DateTime.now().millisecondsSinceEpoch + 1000,
          },
          {
            'id': 3,
            'content': 'Third message with emojis: 🚀🔥⭐',
            'timestamp': DateTime.now().millisecondsSinceEpoch + 2000,
          },
        ];

        final results = <Map<String, dynamic>>[];
        
        for (final message in messages) {
          final result = await rustBridge.processMessage(message);
          results.add(result);
        }

        for (int i = 0; i < results.length; i++) {
          expect(results[i]['success'], isTrue);
          expect(results[i]['data'], contains('Processed: ${messages[i]['content']}'));
          expect(results[i]['error'], isNull);
        }
      });

      test('should handle concurrent requests without corruption', () async {
        final futures = <Future<Map<String, dynamic>>>[];
        
        for (int i = 0; i < 50; i++) {
          final message = {
            'id': i,
            'content': 'Concurrent message $i',
            'timestamp': DateTime.now().millisecondsSinceEpoch + i,
          };
          futures.add(rustBridge.processMessage(message));
        }

        final results = await Future.wait(futures);

        for (int i = 0; i < results.length; i++) {
          expect(results[i]['success'], isTrue);
          expect(results[i]['data'], contains('Concurrent message $i'));
        }
      });
    });

    group('Memory Management', () {
      test('should not leak memory during intensive operations', () async {
        for (int batch = 0; batch < 10; batch++) {
          final batchFutures = <Future>[];
          
          for (int i = 0; i < 100; i++) {
            final addFuture = rustBridge.addNumbers(i, i + 1);
            final messageFuture = rustBridge.processMessage({
              'id': batch * 100 + i,
              'content': 'Batch $batch Message $i',
              'timestamp': DateTime.now().millisecondsSinceEpoch,
            });
            
            batchFutures.addAll([addFuture, messageFuture]);
          }
          
          await Future.wait(batchFutures);
        }
        
        expect(true, isTrue);
      });
    });

    group('Error Handling', () {
      test('should gracefully handle various error conditions', () async {
        final invalidMessages = <Map<String, dynamic>>[
          {},
          {'id': 'invalid'},
          {'content': null},
          {'timestamp': 'invalid'},
          {
            'id': 1,
            'content': 'valid',
          },
        ];

        for (final invalidMessage in invalidMessages) {
          final result = await rustBridge.processMessage(invalidMessage);
          
          if (invalidMessage.containsKey('content') && 
              invalidMessage.containsKey('id') &&
              invalidMessage['id'] is int &&
              invalidMessage['content'] is String) {
            expect(result['success'], isFalse);
            expect(result['error'], contains('missing field'));
          } else {
            expect(result['success'], isFalse);
            expect(result['error'], isNotNull);
          }
        }
      });
    });

    group('Performance', () {
      test('should meet performance requirements', () async {
        final stopwatch = Stopwatch()..start();
        
        const iterations = 1000;
        var totalSum = 0;
        
        for (int i = 0; i < iterations; i++) {
          totalSum += await rustBridge.addNumbers(i, i + 1);
        }
        
        stopwatch.stop();
        
        expect(totalSum, equals(iterations * (iterations - 1) + iterations));
        
        final avgTimePerCall = stopwatch.elapsedMicroseconds / iterations;
        print('Average time per call: ${avgTimePerCall.toStringAsFixed(2)} μs');
        
        expect(avgTimePerCall, lessThan(1000));
      });

      test('should handle large message processing efficiently', () async {
        final largeContent = 'x' * 10000;
        
        final stopwatch = Stopwatch()..start();
        
        final result = await rustBridge.processMessage({
          'id': 999,
          'content': largeContent,
          'timestamp': DateTime.now().millisecondsSinceEpoch,
        });
        
        stopwatch.stop();
        
        expect(result['success'], isTrue);
        expect(result['data'], contains('Processed: $largeContent'));
        expect(stopwatch.elapsedMilliseconds, lessThan(100));
      });
    });

    group('Data Integrity', () {
      test('should preserve Unicode characters correctly', () async {
        final unicodeMessages = [
          'Hello 世界',
          '🌍🌎🌏',
          'Ñiño résumé café',
          'العربية',
          'русский',
          '日本語',
          '한국어',
        ];

        for (final content in unicodeMessages) {
          final result = await rustBridge.processMessage({
            'id': unicodeMessages.indexOf(content),
            'content': content,
            'timestamp': DateTime.now().millisecondsSinceEpoch,
          });

          expect(result['success'], isTrue);
          expect(result['data'], contains('Processed: $content'));
        }
      });

      test('should handle large numbers correctly', () async {
        final testCases = [
          [0, 0, 0],
          [1, 1, 2],
          [-1, 1, 0],
          [1000000, 1000000, 2000000],
          [-1000000, 2000000, 1000000],
          [2147483647, 0, 2147483647],
          [-2147483648, 0, -2147483648],
        ];

        for (final testCase in testCases) {
          final result = await rustBridge.addNumbers(testCase[0], testCase[1]);
          expect(result, equals(testCase[2]), 
                 reason: '${testCase[0]} + ${testCase[1]} should equal ${testCase[2]}');
        }
      });
    });

    group('System Integration', () {
      test('should return valid system information', () async {
        final systemInfo = await rustBridge.getSystemInfo();
        
        expect(systemInfo, isNotEmpty);
        expect(systemInfo, contains('Rust Version'));
        expect(systemInfo, matches(RegExp(r'OS: \w+')));
        expect(systemInfo, matches(RegExp(r'Arch: \w+')));
      });
    });
  });
}