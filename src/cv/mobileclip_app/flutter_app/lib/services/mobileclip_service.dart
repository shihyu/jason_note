import 'dart:math' as math;
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:flutter_onnxruntime/flutter_onnxruntime.dart';
import 'package:image/image.dart' as img;
import 'log_service.dart';

/// MobileCLIP Service - 負責 ONNX 模型載入與推論
///
/// 功能：
/// 1. 載入 MobileCLIP-S2 ONNX 模型 (使用 flutter_onnxruntime 1.5.2，支援 IR version 10)
/// 2. 預處理圖片（resize to 256x256, normalize）
/// 3. 執行推論並回傳 512 維特徵向量
class MobileCLIPService {
  static const String _modelPath = 'assets/models/mobileclip_s2.onnx';
  static const int _inputSize = 256;  // MobileCLIP-S2 使用 256x256 輸入
  static const int _featureDim = 512;

  // Singleton 實作
  static final MobileCLIPService _instance = MobileCLIPService._internal();
  factory MobileCLIPService() => _instance;
  MobileCLIPService._internal();

  OnnxRuntime? _ort;
  OrtSession? _session;
  bool _isInitialized = false;

  /// 是否已初始化
  bool get isInitialized => _isInitialized;

  /// 初始化模型
  ///
  /// 必須在使用前呼叫此方法載入模型
  Future<void> initialize() async {
    if (_isInitialized) {
      log.info('MobileCLIP Service 已經初始化');
      return;
    }

    try {
      log.info('載入 MobileCLIP-S2 ONNX 模型...');

      // 建立 ONNX Runtime 實例
      _ort = OnnxRuntime();

      // 從 assets 載入模型
      _session = await _ort!.createSessionFromAsset(_modelPath);

      _isInitialized = true;
      log.info('✅ MobileCLIP Service 初始化成功 (使用 ONNX Runtime 1.22.0)');
    } catch (e, stackTrace) {
      log.error('❌ MobileCLIP Service 初始化失敗: $e');
      log.debug('Stack trace: $stackTrace');
      rethrow;
    }
  }

  /// 釋放資源
  Future<void> dispose() async {
    await _session?.close();
    _session = null;
    _ort = null;
    _isInitialized = false;
    log.info('MobileCLIP Service 已釋放');
  }

  /// 從圖片提取特徵向量
  ///
  /// [imageBytes] 圖片的二進位資料
  /// 回傳 512 維的特徵向量，已經過 L2 normalization
  Future<List<double>> extractFeatures(Uint8List imageBytes) async {
    if (!_isInitialized) {
      throw StateError('MobileCLIP Service 尚未初始化，請先呼叫 initialize()');
    }

    OrtValue? inputOrt;
    Map<String, OrtValue>? outputs;

    try {
      // 1. 解碼圖片
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        throw Exception('無法解碼圖片');
      }

      // 2. 預處理圖片
      final input = _preprocessImage(image);

      // 3. 準備輸入數據
      inputOrt = await OrtValue.fromList(
        input,
        [1, 3, _inputSize, _inputSize],
      );

      // 4. 執行推論
      final inputs = {'input': inputOrt};
      outputs = await _session!.run(inputs);

      // 5. 取得輸出 (output name is typically 'output' or check with getOutputInfo)
      final outputName = _session!.outputNames.first;
      final outputData = await outputs[outputName]!.asFlattenedList();

      // 6. L2 normalize
      final features = _normalizeVector(outputData.cast<double>());

      return features;
    } catch (e, stackTrace) {
      log.error('特徵提取失敗: $e');
      log.debug('Stack trace: $stackTrace');
      rethrow;
    } finally {
      // 釋放張量
      await inputOrt?.dispose();
      if (outputs != null) {
        for (var output in outputs.values) {
          await output.dispose();
        }
      }
    }
  }

  /// 預處理圖片
  ///
  /// 1. Resize to 256x256
  /// 2. 轉換為 RGB
  /// 3. Normalize to [0, 1]
  /// 4. 轉換為 CHW 格式 (Channels, Height, Width)
  List<double> _preprocessImage(img.Image image) {
    // Resize to target size
    final resized = img.copyResize(
      image,
      width: _inputSize,
      height: _inputSize,
      interpolation: img.Interpolation.linear,
    );

    // Convert to RGB if needed
    final rgb = resized.convert(numChannels: 3);

    // Prepare input tensor: [1, 3, 256, 256]
    final input = <double>[];

    // Convert HWC (Height, Width, Channels) to CHW (Channels, Height, Width)
    // and normalize to [0, 1]
    for (int c = 0; c < 3; c++) {
      for (int y = 0; y < _inputSize; y++) {
        for (int x = 0; x < _inputSize; x++) {
          final pixel = rgb.getPixel(x, y);
          double value;

          if (c == 0) {
            // Red channel
            value = pixel.r / 255.0;
          } else if (c == 1) {
            // Green channel
            value = pixel.g / 255.0;
          } else {
            // Blue channel
            value = pixel.b / 255.0;
          }

          input.add(value);
        }
      }
    }

    return input;
  }

  /// L2 Normalization
  ///
  /// 將向量標準化，使其 L2 norm 為 1
  /// 這樣在計算 cosine similarity 時只需要做 dot product
  List<double> _normalizeVector(List<double> vector) {
    // Calculate L2 norm (magnitude)
    double sumSquares = 0.0;
    for (var value in vector) {
      sumSquares += value * value;
    }
    final norm = math.sqrt(sumSquares);

    // Normalize
    if (norm > 0) {
      return vector.map((v) => v / norm).toList();
    }

    return vector;
  }

  /// 批次提取特徵（用於優化多張圖片的處理）
  Future<List<List<double>>> extractFeaturesBatch(
    List<Uint8List> imageBytesList,
  ) async {
    final features = <List<double>>[];

    for (final imageBytes in imageBytesList) {
      final feature = await extractFeatures(imageBytes);
      features.add(feature);
    }

    return features;
  }
}
