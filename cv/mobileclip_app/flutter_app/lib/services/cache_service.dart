import 'dart:typed_data';
import 'dart:collection';
import 'log_service.dart';

/// 快取服務
///
/// 提供記憶體快取功能，減少重複的檔案讀取與計算
class CacheService {
  static final CacheService _instance = CacheService._internal();
  factory CacheService() => _instance;
  CacheService._internal();

  /// 圖片快取 (LRU Cache)
  final LinkedHashMap<String, Uint8List> _imageCache = LinkedHashMap();

  /// 特徵向量快取
  final Map<String, List<double>> _featureCache = {};

  /// 最大快取大小（圖片數量）
  static const int _maxImageCacheSize = 50;

  /// 最大快取大小（位元組）- 50MB
  static const int _maxImageCacheSizeBytes = 50 * 1024 * 1024;

  /// 當前快取大小（位元組）
  int _currentImageCacheSize = 0;

  /// 圖片快取統計
  int _imageHits = 0;
  int _imageMisses = 0;

  /// 取得圖片快取
  Uint8List? getImage(String path) {
    if (_imageCache.containsKey(path)) {
      // 更新 LRU - 移到最後
      final image = _imageCache.remove(path)!;
      _imageCache[path] = image;
      _imageHits++;
      log.debug('圖片快取命中: $path');
      return image;
    }
    _imageMisses++;
    return null;
  }

  /// 儲存圖片到快取
  void putImage(String path, Uint8List imageBytes) {
    final imageSize = imageBytes.length;

    // 檢查是否超過單一圖片大小限制（5MB）
    if (imageSize > 5 * 1024 * 1024) {
      log.warning('圖片過大，不快取: $path (${imageSize ~/ 1024}KB)');
      return;
    }

    // 如果已存在，先移除舊的
    if (_imageCache.containsKey(path)) {
      _currentImageCacheSize -= _imageCache[path]!.length;
      _imageCache.remove(path);
    }

    // 檢查快取空間，必要時移除最舊的項目
    while (_imageCache.length >= _maxImageCacheSize ||
        _currentImageCacheSize + imageSize > _maxImageCacheSizeBytes) {
      if (_imageCache.isEmpty) break;

      final firstKey = _imageCache.keys.first;
      final removed = _imageCache.remove(firstKey)!;
      _currentImageCacheSize -= removed.length;
      log.debug('快取空間不足，移除: $firstKey');
    }

    // 新增到快取
    _imageCache[path] = imageBytes;
    _currentImageCacheSize += imageSize;
    log.debug('圖片已快取: $path (${imageSize ~/ 1024}KB, 總計: ${_currentImageCacheSize ~/ 1024}KB)');
  }

  /// 移除圖片快取
  void removeImage(String path) {
    if (_imageCache.containsKey(path)) {
      _currentImageCacheSize -= _imageCache[path]!.length;
      _imageCache.remove(path);
      log.debug('已移除圖片快取: $path');
    }
  }

  /// 取得特徵向量快取
  List<double>? getFeatures(String imageId) {
    if (_featureCache.containsKey(imageId)) {
      log.debug('特徵向量快取命中: $imageId');
      return _featureCache[imageId];
    }
    return null;
  }

  /// 儲存特徵向量到快取
  void putFeatures(String imageId, List<double> features) {
    _featureCache[imageId] = features;
    log.debug('特徵向量已快取: $imageId');
  }

  /// 移除特徵向量快取
  void removeFeatures(String imageId) {
    _featureCache.remove(imageId);
    log.debug('已移除特徵向量快取: $imageId');
  }

  /// 清除所有快取
  void clearAll() {
    final imageCount = _imageCache.length;
    final featureCount = _featureCache.length;
    final totalSize = _currentImageCacheSize;

    _imageCache.clear();
    _featureCache.clear();
    _currentImageCacheSize = 0;
    _imageHits = 0;
    _imageMisses = 0;

    log.info('已清除所有快取 (圖片: $imageCount, 特徵: $featureCount, 大小: ${totalSize ~/ 1024}KB)');
  }

  /// 清除圖片快取
  void clearImageCache() {
    final count = _imageCache.length;
    final size = _currentImageCacheSize;

    _imageCache.clear();
    _currentImageCacheSize = 0;
    _imageHits = 0;
    _imageMisses = 0;

    log.info('已清除圖片快取 ($count 張, ${size ~/ 1024}KB)');
  }

  /// 清除特徵向量快取
  void clearFeatureCache() {
    final count = _featureCache.length;
    _featureCache.clear();
    log.info('已清除特徵向量快取 ($count 個)');
  }

  /// 取得快取統計資訊
  Map<String, dynamic> getStats() {
    final hitRate = _imageHits + _imageMisses > 0
        ? (_imageHits / (_imageHits + _imageMisses) * 100).toStringAsFixed(2)
        : '0.00';

    return {
      'imageCount': _imageCache.length,
      'featureCount': _featureCache.length,
      'totalSizeKB': _currentImageCacheSize ~/ 1024,
      'maxSizeKB': _maxImageCacheSizeBytes ~/ 1024,
      'imageHits': _imageHits,
      'imageMisses': _imageMisses,
      'hitRate': '$hitRate%',
    };
  }

  /// 顯示快取統計
  void printStats() {
    final stats = getStats();
    log.info('快取統計: $stats');
  }
}

/// 全域快取實例
final cache = CacheService();
