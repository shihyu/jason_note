import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/permission_service.dart';
import '../services/mobileclip_service.dart';
import '../services/database_service.dart';
import 'home_screen.dart';

/// 啟動畫面 - 初始化應用程式
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  String _statusMessage = '正在初始化...';
  double _progress = 0.0;
  bool _hasError = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  /// 初始化應用程式
  Future<void> _initialize() async {
    try {
      // 1. 檢查模型檔案
      await _checkModelFiles();

      // 2. 請求權限
      await _requestPermissions();

      // 3. 初始化資料庫
      await _initializeDatabase();

      // 4. 初始化模型（預先載入）
      await _initializeModel();

      // 5. 導航到主畫面
      await Future.delayed(const Duration(milliseconds: 500));
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const HomeScreen()),
        );
      }
    } catch (e) {
      setState(() {
        _hasError = true;
        _errorMessage = e.toString();
        _statusMessage = '初始化失敗';
      });
    }
  }

  /// 檢查模型檔案
  Future<void> _checkModelFiles() async {
    setState(() {
      _statusMessage = '正在檢查模型檔案...';
      _progress = 0.1;
    });

    await Future.delayed(const Duration(milliseconds: 300));

    try {
      // 嘗試載入模型檔案
      await rootBundle.load('assets/models/mobileclip_s2.onnx');

      setState(() {
        _progress = 0.25;
      });
    } catch (e) {
      throw Exception(
        '找不到模型檔案\n'
        '請確認 assets/models/mobileclip_s2.onnx 檔案存在',
      );
    }
  }

  /// 請求權限
  Future<void> _requestPermissions() async {
    setState(() {
      _statusMessage = '正在請求權限...';
      _progress = 0.35;
    });

    // 請求相機權限
    final cameraGranted = await PermissionService.requestCameraPermission();
    if (!cameraGranted) {
      throw Exception(
        '需要相機權限\n'
        '請在設定中開啟相機權限',
      );
    }

    setState(() {
      _progress = 0.5;
    });

    // 請求儲存權限
    final storageGranted = await PermissionService.requestStoragePermission();
    if (!storageGranted) {
      throw Exception(
        '需要儲存權限\n'
        '請在設定中開啟儲存權限',
      );
    }

    setState(() {
      _progress = 0.6;
    });
  }

  /// 初始化資料庫
  Future<void> _initializeDatabase() async {
    setState(() {
      _statusMessage = '正在初始化資料庫...';
      _progress = 0.7;
    });

    final databaseService = DatabaseService();
    await databaseService.database; // 觸發資料庫初始化
    await databaseService.close();

    setState(() {
      _progress = 0.8;
    });
  }

  /// 初始化模型
  Future<void> _initializeModel() async {
    setState(() {
      _statusMessage = '正在載入 AI 模型...';
      _progress = 0.85;
    });

    final clipService = MobileCLIPService();
    await clipService.initialize();
    // 不要釋放 MobileCLIP Service，因為它是 Singleton
    // clipService.dispose();

    setState(() {
      _statusMessage = '初始化完成';
      _progress = 1.0;
    });
  }

  /// 重試初始化
  void _retry() {
    setState(() {
      _hasError = false;
      _errorMessage = null;
      _statusMessage = '正在初始化...';
      _progress = 0.0;
    });
    _initialize();
  }

  /// 開啟設定
  void _openSettings() async {
    await PermissionService.requestAllPermissions();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Theme.of(context).colorScheme.primary,
              Theme.of(context).colorScheme.secondary,
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Logo 圖示
                  const Icon(
                    Icons.shopping_bag,
                    size: 100,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 24),

                  // 應用程式名稱
                  const Text(
                    'MobileCLIP',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '商品管理與搜尋',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white70,
                    ),
                  ),
                  const SizedBox(height: 60),

                  // 狀態顯示
                  if (!_hasError) ...[
                    // 進度條
                    SizedBox(
                      width: double.infinity,
                      child: LinearProgressIndicator(
                        value: _progress,
                        backgroundColor: Colors.white24,
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          Colors.white,
                        ),
                        minHeight: 6,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // 狀態訊息
                    Text(
                      _statusMessage,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ] else ...[
                    // 錯誤訊息
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Column(
                        children: [
                          const Icon(
                            Icons.error_outline,
                            size: 48,
                            color: Colors.red,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            _statusMessage,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.red,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _errorMessage ?? '',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[700],
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 20),

                          // 重試按鈕
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              TextButton.icon(
                                onPressed: _openSettings,
                                icon: const Icon(Icons.settings),
                                label: const Text('開啟設定'),
                              ),
                              const SizedBox(width: 12),
                              ElevatedButton.icon(
                                onPressed: _retry,
                                icon: const Icon(Icons.refresh),
                                label: const Text('重試'),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
