import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:io';
import '../services/database_service.dart';
import '../services/mobileclip_service.dart';
import '../services/vector_service.dart';
import 'product_detail_screen.dart';

/// 相機搜尋畫面 - 即時偵測並顯示最相似的商品
class CameraSearchScreen extends StatefulWidget {
  const CameraSearchScreen({super.key});

  @override
  State<CameraSearchScreen> createState() => _CameraSearchScreenState();
}

class _CameraSearchScreenState extends State<CameraSearchScreen> {
  final DatabaseService _databaseService = DatabaseService();
  final MobileCLIPService _clipService = MobileCLIPService();
  late final VectorService _vectorService;

  CameraController? _cameraController;
  List<CameraDescription>? _cameras;
  bool _isInitialized = false;
  bool _isProcessing = false;

  ProductMatch? _currentMatch;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _vectorService = VectorService(_databaseService);
    _initializeCamera();
    _initializeServices();
  }

  /// 初始化相機
  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();

      if (_cameras == null || _cameras!.isEmpty) {
        setState(() => _errorMessage = '找不到相機');
        return;
      }

      _cameraController = CameraController(
        _cameras!.first,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _cameraController!.initialize();

      if (mounted) {
        setState(() => _isInitialized = true);
      }
    } catch (e) {
      setState(() => _errorMessage = '相機初始化失敗: $e');
    }
  }

  /// 初始化服務
  Future<void> _initializeServices() async {
    try {
      await _clipService.initialize();
    } catch (e) {
      setState(() => _errorMessage = '模型初始化失敗: $e');
    }
  }

  /// 拍照並搜尋
  Future<void> _captureAndSearch() async {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    if (_isProcessing) return;

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      // 1. 拍照
      final image = await _cameraController!.takePicture();
      final imageBytes = await image.readAsBytes();

      // 2. 提取特徵向量
      final featureVector = await _clipService.extractFeatures(imageBytes);

      // 3. 搜尋最相似的商品
      final match = await _vectorService.findMostSimilarProduct(
        queryVector: featureVector,
        threshold: 0.5, // 相似度閾值 50%
      );

      setState(() {
        _currentMatch = match;
        _isProcessing = false;

        if (match == null) {
          _errorMessage = '找不到相似的商品\n(相似度低於 50%)';
        }
      });
    } catch (e) {
      setState(() {
        _isProcessing = false;
        _errorMessage = '搜尋失敗: $e';
      });
    }
  }

  /// 前往商品詳情
  void _navigateToProductDetail() {
    if (_currentMatch == null) return;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            ProductDetailScreen(product: _currentMatch!.product),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('相機搜尋'),
      ),
      body: !_isInitialized
          ? _buildLoadingState()
          : Column(
              children: [
                // 相機預覽
                Expanded(
                  flex: 3,
                  child: _buildCameraPreview(),
                ),

                // 搜尋結果
                Expanded(
                  flex: 2,
                  child: _buildSearchResult(),
                ),
              ],
            ),
      floatingActionButton: _isInitialized
          ? FloatingActionButton.extended(
              onPressed: _isProcessing ? null : _captureAndSearch,
              icon: _isProcessing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.search),
              label: Text(_isProcessing ? '搜尋中...' : '拍照搜尋'),
            )
          : null,
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }

  /// 建立載入狀態
  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (_errorMessage != null) ...[
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, color: Colors.red),
            ),
          ] else ...[
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            const Text('正在初始化相機...'),
          ],
        ],
      ),
    );
  }

  /// 建立相機預覽
  Widget _buildCameraPreview() {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return Container(
        color: Colors.black,
        child: const Center(child: CircularProgressIndicator()),
      );
    }

    return Stack(
      fit: StackFit.expand,
      children: [
        CameraPreview(_cameraController!),

        // 掃描框
        Center(
          child: Container(
            width: 250,
            height: 250,
            decoration: BoxDecoration(
              border: Border.all(
                color: Colors.white,
                width: 3,
              ),
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),

        // 提示文字
        const Positioned(
          bottom: 20,
          left: 0,
          right: 0,
          child: Text(
            '將商品放在框內，然後點擊搜尋',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              shadows: [
                Shadow(
                  color: Colors.black,
                  blurRadius: 4,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  /// 建立搜尋結果
  Widget _buildSearchResult() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: _errorMessage != null
          ? _buildErrorState()
          : _currentMatch == null
              ? _buildEmptyState()
              : _buildMatchResult(),
    );
  }

  /// 建立錯誤狀態
  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 12),
          Text(
            _errorMessage!,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 14, color: Colors.red),
          ),
        ],
      ),
    );
  }

  /// 建立空狀態
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.search, size: 48, color: Colors.grey[400]),
          const SizedBox(height: 12),
          Text(
            '點擊下方按鈕開始搜尋',
            style: TextStyle(fontSize: 16, color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }

  /// 建立匹配結果
  Widget _buildMatchResult() {
    final product = _currentMatch!.product;
    final similarity = _currentMatch!.similarity;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 標題
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '找到相似商品',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: _getSimilarityColor(similarity),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                '${(similarity * 100).toStringAsFixed(1)}%',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // 商品卡片
        Expanded(
          child: InkWell(
            onTap: _navigateToProductDetail,
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: Row(
                children: [
                  // 商品圖片
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.file(
                      File(product.imagePath),
                      width: 80,
                      height: 80,
                      fit: BoxFit.cover,
                    ),
                  ),
                  const SizedBox(width: 12),

                  // 商品資訊
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          product.name,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (product.description != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            product.description!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                        if (product.price != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            'NT\$ ${product.price!.toStringAsFixed(0)}',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),

                  // 箭頭圖示
                  const Icon(Icons.arrow_forward_ios, size: 20),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// 根據相似度取得顏色
  Color _getSimilarityColor(double similarity) {
    if (similarity >= 0.8) return Colors.green;
    if (similarity >= 0.6) return Colors.orange;
    return Colors.red;
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    // 不要釋放 MobileCLIP Service，因為它是 Singleton
    // _clipService.dispose();
    _databaseService.close();
    super.dispose();
  }
}
