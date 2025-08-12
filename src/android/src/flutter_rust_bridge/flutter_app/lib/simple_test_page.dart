import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'rust_bridge.dart';
import 'dart:convert';

class SimpleTestPage extends StatefulWidget {
  const SimpleTestPage({Key? key}) : super(key: key);

  @override
  _SimpleTestPageState createState() => _SimpleTestPageState();
}

class _SimpleTestPageState extends State<SimpleTestPage> {
  RustBridge? _rustBridge;
  String _status = '準備中...';
  String _lastResult = '';
  bool _isLoading = false;
  int _testCounter = 0;

  @override
  void initState() {
    super.initState();
    _initRustBridge();
  }

  Future<void> _initRustBridge() async {
    setState(() {
      _status = '正在初始化 Rust Bridge...';
    });

    try {
      _rustBridge = RustBridge();
      setState(() {
        _status = '✅ Rust Bridge 初始化成功！';
      });
      print('[BitoPro Flutter] Rust Bridge initialized successfully');
    } catch (e) {
      setState(() {
        _status = '❌ 初始化失敗: $e';
      });
      print('[BitoPro Flutter] Initialization failed: $e');
    }
  }

  Future<void> _testAddition() async {
    if (_rustBridge == null) return;
    
    setState(() {
      _isLoading = true;
      _status = '測試數字加法...';
    });

    try {
      final a = 123;
      final b = 456;
      print('[BitoPro Flutter] Calling rust_add_numbers($a, $b)');
      
      final result = await _rustBridge!.addNumbers(a, b);
      
      setState(() {
        _lastResult = '$a + $b = $result';
        _status = '✅ 數字加法測試成功！';
        _testCounter++;
      });
      print('[BitoPro Flutter] Addition test successful: $result');
    } catch (e) {
      setState(() {
        _status = '❌ 數字加法測試失敗: $e';
        _lastResult = 'Error: $e';
      });
      print('[BitoPro Flutter] Addition test failed: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _testMessage() async {
    if (_rustBridge == null) return;
    
    setState(() {
      _isLoading = true;
      _status = '測試訊息處理...';
    });

    try {
      final message = {
        'id': DateTime.now().millisecondsSinceEpoch % 10000,
        'content': 'BitoPro 測試訊息 #${_testCounter + 1} 🚀',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      
      print('[BitoPro Flutter] Sending message: ${jsonEncode(message)}');
      
      final result = await _rustBridge!.processMessage(message);
      
      setState(() {
        _lastResult = 'Response: ${jsonEncode(result)}';
        _status = result['success'] == true 
            ? '✅ 訊息處理測試成功！' 
            : '⚠️ 訊息處理有錯誤';
        _testCounter++;
      });
      print('[BitoPro Flutter] Message test result: $result');
    } catch (e) {
      setState(() {
        _status = '❌ 訊息處理測試失敗: $e';
        _lastResult = 'Error: $e';
      });
      print('[BitoPro Flutter] Message test failed: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _testSystemInfo() async {
    if (_rustBridge == null) return;
    
    setState(() {
      _isLoading = true;
      _status = '獲取系統資訊...';
    });

    try {
      print('[BitoPro Flutter] Calling rust_get_system_info()');
      
      final info = await _rustBridge!.getSystemInfo();
      
      setState(() {
        _lastResult = info;
        _status = '✅ 系統資訊獲取成功！';
        _testCounter++;
      });
      print('[BitoPro Flutter] System info: $info');
    } catch (e) {
      setState(() {
        _status = '❌ 系統資訊獲取失敗: $e';
        _lastResult = 'Error: $e';
      });
      print('[BitoPro Flutter] System info test failed: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _runAllTests() async {
    print('[BitoPro Flutter] Starting comprehensive test suite');
    await _testAddition();
    await Future.delayed(const Duration(milliseconds: 500));
    await _testMessage();
    await Future.delayed(const Duration(milliseconds: 500));
    await _testSystemInfo();
    
    setState(() {
      _status = '🎉 所有測試完成！總共執行 ${_testCounter} 個測試';
    });
    print('[BitoPro Flutter] All tests completed. Total tests: $_testCounter');
  }

  void _showLogcatInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('查看 Logcat 日誌'),
        content: const Text(
          '要查看詳細日誌，請在終端執行：\n\n'
          'adb logcat -s BitoPro\n\n'
          '或者使用 Android Studio 的 Logcat 工具過濾 "BitoPro" 標籤。'
        ),
        actions: [
          TextButton(
            onPressed: () {
              Clipboard.setData(const ClipboardData(text: 'adb logcat -s BitoPro'));
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('命令已複製到剪貼簿'))
              );
            },
            child: const Text('複製命令'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('關閉'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('BitoPro Rust-Flutter 測試'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: _showLogcatInfo,
            icon: const Icon(Icons.bug_report),
            tooltip: '查看 Logcat 說明',
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 狀態卡片
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _isLoading 
                                ? Icons.hourglass_empty 
                                : Icons.info_outline,
                            color: Colors.blue[600],
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            '狀態',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (_isLoading) ...[
                            const SizedBox(width: 8),
                            const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _status,
                        style: const TextStyle(fontSize: 16),
                      ),
                      if (_testCounter > 0) ...[
                        const SizedBox(height: 8),
                        Text(
                          '已執行測試: $_testCounter 個',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // 測試按鈕
              const Text(
                '雙向溝通測試',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              // 個別測試按鈕
              ElevatedButton.icon(
                onPressed: _rustBridge != null && !_isLoading ? _testAddition : null,
                icon: const Icon(Icons.calculate),
                label: const Text('測試數字加法'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
              
              const SizedBox(height: 8),
              
              ElevatedButton.icon(
                onPressed: _rustBridge != null && !_isLoading ? _testMessage : null,
                icon: const Icon(Icons.message),
                label: const Text('測試訊息處理'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
              
              const SizedBox(height: 8),
              
              ElevatedButton.icon(
                onPressed: _rustBridge != null && !_isLoading ? _testSystemInfo : null,
                icon: const Icon(Icons.info),
                label: const Text('測試系統資訊'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),

              const SizedBox(height: 16),

              // 綜合測試按鈕
              ElevatedButton.icon(
                onPressed: _rustBridge != null && !_isLoading ? _runAllTests : null,
                icon: const Icon(Icons.play_arrow),
                label: const Text('執行所有測試'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green[600],
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  textStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // 結果顯示
              Expanded(
                child: Card(
                  elevation: 4,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.output, color: Colors.orange[600]),
                            const SizedBox(width: 8),
                            const Text(
                              '最新結果',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const Divider(),
                        Expanded(
                          child: SingleChildScrollView(
                            child: Text(
                              _lastResult.isEmpty ? '尚無測試結果' : _lastResult,
                              style: const TextStyle(
                                fontFamily: 'monospace',
                                fontSize: 14,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}