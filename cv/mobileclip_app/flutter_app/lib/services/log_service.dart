import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:intl/intl.dart';

/// 日誌等級
enum LogLevel {
  debug,
  info,
  warning,
  error,
}

/// 日誌服務
///
/// 提供應用程式的日誌記錄功能：
/// 1. 支援多種日誌等級（Debug, Info, Warning, Error）
/// 2. Debug 模式下輸出到 console
/// 3. Release 模式下寫入檔案
/// 4. 自動清理舊日誌檔案
class LogService {
  static final LogService _instance = LogService._internal();
  factory LogService() => _instance;
  LogService._internal();

  File? _logFile;
  bool _isInitialized = false;
  final DateFormat _dateFormatter = DateFormat('yyyy-MM-dd HH:mm:ss');

  /// 最大日誌檔案大小（5MB）
  static const int _maxLogSize = 5 * 1024 * 1024;

  /// 日誌保留天數
  static const int _logRetentionDays = 7;

  /// 初始化日誌服務
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      if (!kDebugMode) {
        // Release 模式下，建立日誌檔案
        final directory = await getApplicationDocumentsDirectory();
        final logDir = Directory('${directory.path}/logs');

        if (!await logDir.exists()) {
          await logDir.create(recursive: true);
        }

        final now = DateTime.now();
        final fileName = 'app_${DateFormat('yyyy-MM-dd').format(now)}.log';
        _logFile = File('${logDir.path}/$fileName');

        // 清理舊日誌
        await _cleanOldLogs(logDir);
      }

      _isInitialized = true;
      info('LogService 初始化完成');
    } catch (e) {
      // 初始化失敗時，只能用 print
      if (kDebugMode) {
        print('LogService 初始化失敗: $e');
      }
    }
  }

  /// 清理舊日誌檔案
  Future<void> _cleanOldLogs(Directory logDir) async {
    try {
      final now = DateTime.now();
      final files = await logDir.list().toList();

      for (final file in files) {
        if (file is File) {
          final stat = await file.stat();
          final age = now.difference(stat.modified).inDays;

          if (age > _logRetentionDays) {
            await file.delete();
            if (kDebugMode) {
              print('已刪除舊日誌: ${file.path}');
            }
          }
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('清理舊日誌失敗: $e');
      }
    }
  }

  /// 檢查並輪轉日誌檔案
  Future<void> _checkLogRotation() async {
    if (_logFile == null) return;

    try {
      if (await _logFile!.exists()) {
        final size = await _logFile!.length();

        if (size > _maxLogSize) {
          final timestamp = DateFormat('HHmmss').format(DateTime.now());
          final newPath = '${_logFile!.path}.$timestamp.old';
          await _logFile!.rename(newPath);

          // 重新建立新檔案
          _logFile = File(_logFile!.path);
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('日誌輪轉失敗: $e');
      }
    }
  }

  /// 寫入日誌
  Future<void> _write(LogLevel level, String message, [Object? error, StackTrace? stackTrace]) async {
    final timestamp = _dateFormatter.format(DateTime.now());
    final levelStr = level.toString().split('.').last.toUpperCase().padRight(7);
    final logMessage = '[$timestamp] $levelStr: $message';

    // Debug 模式：輸出到 console
    if (kDebugMode) {
      print(logMessage);
      if (error != null) {
        print('  Error: $error');
      }
      if (stackTrace != null) {
        print('  StackTrace: $stackTrace');
      }
    }

    // Release 模式：寫入檔案
    if (!kDebugMode && _logFile != null) {
      try {
        await _checkLogRotation();

        final buffer = StringBuffer(logMessage);
        buffer.writeln();

        if (error != null) {
          buffer.writeln('  Error: $error');
        }
        if (stackTrace != null) {
          buffer.writeln('  StackTrace: $stackTrace');
        }

        await _logFile!.writeAsString(
          buffer.toString(),
          mode: FileMode.append,
        );
      } catch (e) {
        // 寫入失敗時，至少在 Debug 模式輸出
        if (kDebugMode) {
          print('寫入日誌檔案失敗: $e');
        }
      }
    }
  }

  /// Debug 等級日誌
  void debug(String message) {
    _write(LogLevel.debug, message);
  }

  /// Info 等級日誌
  void info(String message) {
    _write(LogLevel.info, message);
  }

  /// Warning 等級日誌
  void warning(String message, [Object? error]) {
    _write(LogLevel.warning, message, error);
  }

  /// Error 等級日誌
  void error(String message, [Object? error, StackTrace? stackTrace]) {
    _write(LogLevel.error, message, error, stackTrace);
  }

  /// 取得今日日誌檔案路徑
  String? get logFilePath => _logFile?.path;

  /// 讀取今日日誌內容
  Future<String?> readTodayLog() async {
    if (_logFile == null || !await _logFile!.exists()) {
      return null;
    }

    try {
      return await _logFile!.readAsString();
    } catch (e) {
      error('讀取日誌檔案失敗', e);
      return null;
    }
  }

  /// 清除所有日誌
  Future<void> clearAllLogs() async {
    try {
      if (_logFile != null) {
        final directory = await getApplicationDocumentsDirectory();
        final logDir = Directory('${directory.path}/logs');

        if (await logDir.exists()) {
          await logDir.delete(recursive: true);
          info('已清除所有日誌');
        }
      }
    } catch (e) {
      error('清除日誌失敗', e);
    }
  }
}

/// 全域日誌實例
final log = LogService();
