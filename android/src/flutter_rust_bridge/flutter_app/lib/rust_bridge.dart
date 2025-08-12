import 'dart:convert';
import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

typedef RustAddNumbers = Int32 Function(Int32 a, Int32 b);
typedef RustAddNumbersDart = int Function(int a, int b);

typedef RustProcessMessage = Pointer<Utf8> Function(Pointer<Utf8> jsonStr);
typedef RustProcessMessageDart = Pointer<Utf8> Function(Pointer<Utf8> jsonStr);

typedef RustGetSystemInfo = Pointer<Utf8> Function();
typedef RustGetSystemInfoDart = Pointer<Utf8> Function();

typedef RustFreeString = Void Function(Pointer<Utf8> ptr);
typedef RustFreeStringDart = void Function(Pointer<Utf8> ptr);

class RustBridge {
  late final DynamicLibrary _lib;
  late final RustAddNumbersDart _addNumbers;
  late final RustProcessMessageDart _processMessage;
  late final RustGetSystemInfoDart _getSystemInfo;
  late final RustFreeStringDart _freeString;

  RustBridge() {
    _loadLibrary();
    _bindFunctions();
  }

  void _loadLibrary() {
    print('[BitoPro Flutter] Loading dynamic library...');
    
    if (Platform.isAndroid) {
      // Android-specific loading paths
      final androidPaths = [
        'librust_flutter_bridge.so',  // Standard Android JNI path
        '/data/local/tmp/librust_flutter_bridge.so',  // Test path
        '/home/shihyu/rust_to_fluuter/target/release/librust_flutter_bridge.so',  // Development path
      ];
      
      Exception? lastException;
      for (final path in androidPaths) {
        try {
          print('[BitoPro Flutter] Trying to load from: $path');
          _lib = DynamicLibrary.open(path);
          print('[BitoPro Flutter] Successfully loaded library from: $path');
          return;
        } catch (e) {
          print('[BitoPro Flutter] Failed to load from $path: $e');
          lastException = e as Exception;
        }
      }
      throw Exception('[BitoPro Flutter] Failed to load Android library. Last error: $lastException');
    } else if (Platform.isLinux) {
      // Linux development paths
      final linuxPaths = [
        '/home/shihyu/rust_to_fluuter/flutter_app/librust_flutter_bridge.so',
        'librust_flutter_bridge.so',
        '/home/shihyu/rust_to_fluuter/target/release/librust_flutter_bridge.so',
      ];
      
      Exception? lastException;
      for (final path in linuxPaths) {
        try {
          print('[BitoPro Flutter] Trying to load from: $path');
          _lib = DynamicLibrary.open(path);
          print('[BitoPro Flutter] Successfully loaded library from: $path');
          return;
        } catch (e) {
          print('[BitoPro Flutter] Failed to load from $path: $e');
          lastException = e as Exception;
        }
      }
      throw Exception('[BitoPro Flutter] Failed to load Linux library. Last error: $lastException');
    } else if (Platform.isIOS || Platform.isMacOS) {
      _lib = DynamicLibrary.open('librust_flutter_bridge.dylib');
    } else if (Platform.isWindows) {
      _lib = DynamicLibrary.open('rust_flutter_bridge.dll');
    } else {
      throw UnsupportedError('Unsupported platform');
    }
  }

  void _bindFunctions() {
    _addNumbers = _lib
        .lookup<NativeFunction<RustAddNumbers>>('rust_add_numbers')
        .asFunction<RustAddNumbersDart>();

    _processMessage = _lib
        .lookup<NativeFunction<RustProcessMessage>>('rust_process_message')
        .asFunction<RustProcessMessageDart>();

    _getSystemInfo = _lib
        .lookup<NativeFunction<RustGetSystemInfo>>('rust_get_system_info')
        .asFunction<RustGetSystemInfoDart>();

    _freeString = _lib
        .lookup<NativeFunction<RustFreeString>>('rust_free_string')
        .asFunction<RustFreeStringDart>();
  }

  Future<int> addNumbers(int a, int b) async {
    return _addNumbers(a, b);
  }

  Future<Map<String, dynamic>> processMessage(Map<String, dynamic> message) async {
    final jsonString = jsonEncode(message);
    final jsonPointer = jsonString.toNativeUtf8();

    try {
      final resultPointer = _processMessage(jsonPointer);
      if (resultPointer == nullptr) {
        return {
          'success': false,
          'error': 'Failed to process message in Rust',
          'data': null,
        };
      }

      final resultString = resultPointer.toDartString();
      _freeString(resultPointer);

      return jsonDecode(resultString) as Map<String, dynamic>;
    } catch (e) {
      return {
        'success': false,
        'error': 'Exception in processMessage: $e',
        'data': null,
      };
    } finally {
      malloc.free(jsonPointer);
    }
  }

  Future<String> getSystemInfo() async {
    try {
      final resultPointer = _getSystemInfo();
      if (resultPointer == nullptr) {
        return 'Failed to get system info';
      }

      final resultString = resultPointer.toDartString();
      _freeString(resultPointer);

      return resultString;
    } catch (e) {
      return 'Exception in getSystemInfo: $e';
    }
  }

  Future<Map<String, dynamic>> performBenchmark(int iterations) async {
    final stopwatch = Stopwatch()..start();
    
    int totalSum = 0;
    for (int i = 0; i < iterations; i++) {
      totalSum += await addNumbers(i, i + 1);
    }
    
    stopwatch.stop();
    
    return {
      'iterations': iterations,
      'total_sum': totalSum,
      'elapsed_ms': stopwatch.elapsedMilliseconds,
      'avg_call_time_us': (stopwatch.elapsedMicroseconds / iterations).toStringAsFixed(2),
    };
  }
}