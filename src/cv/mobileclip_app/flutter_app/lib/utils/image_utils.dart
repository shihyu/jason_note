import 'dart:io';
import 'dart:typed_data';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import '../services/log_service.dart';
import '../services/cache_service.dart';

/// 圖片處理工具函式
///
/// 提供圖片載入、儲存、轉換等功能
class ImageUtils {
  /// 從檔案路徑載入圖片
  ///
  /// [imagePath]: 圖片檔案路徑
  ///
  /// Returns: 圖片的 Uint8List bytes
  static Future<Uint8List?> loadImageBytes(String imagePath) async {
    try {
      // 先嘗試從快取讀取
      final cached = cache.getImage(imagePath);
      if (cached != null) {
        return cached;
      }

      // 快取未命中，從檔案讀取
      final file = File(imagePath);
      if (!await file.exists()) {
        log.error('❌ 圖片檔案不存在: $imagePath');
        return null;
      }

      final imageBytes = await file.readAsBytes();

      // 加入快取
      cache.putImage(imagePath, imageBytes);

      return imageBytes;
    } catch (e) {
      log.error('❌ 載入圖片失敗', e);
      return null;
    }
  }

  /// 儲存圖片到應用程式目錄
  ///
  /// [imageBytes]: 圖片的 bytes
  /// [filename]: 檔案名稱（不含路徑）
  ///
  /// Returns: 儲存後的完整路徑
  static Future<String> saveImage(Uint8List imageBytes, String filename) async {
    try {
      // 取得應用程式文件目錄
      final directory = await getApplicationDocumentsDirectory();
      final imagesDir = Directory(path.join(directory.path, 'images'));

      // 建立 images 目錄（如果不存在）
      if (!await imagesDir.exists()) {
        await imagesDir.create(recursive: true);
      }

      // 儲存圖片
      final filePath = path.join(imagesDir.path, filename);
      final file = File(filePath);
      await file.writeAsBytes(imageBytes);

      // 加入快取
      cache.putImage(filePath, imageBytes);

      log.info('✅ 圖片已儲存: $filePath');
      return filePath;
    } catch (e) {
      log.error('❌ 儲存圖片失敗', e);
      rethrow;
    }
  }

  /// 產生唯一的圖片檔名
  ///
  /// [prefix]: 檔名前綴，預設 'product'
  /// [extension]: 副檔名，預設 'jpg'
  ///
  /// Returns: 唯一檔名，格式為 'prefix_timestamp.extension'
  static String generateUniqueFilename({
    String prefix = 'product',
    String extension = 'jpg',
  }) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return '${prefix}_$timestamp.$extension';
  }

  /// Resize 圖片
  ///
  /// [imageBytes]: 原始圖片 bytes
  /// [width]: 目標寬度
  /// [height]: 目標高度
  ///
  /// Returns: Resize 後的圖片 bytes
  static Uint8List? resizeImage(
    Uint8List imageBytes,
    int width,
    int height,
  ) {
    try {
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        log.error('❌ 無法解碼圖片');
        return null;
      }

      final resized = img.copyResize(
        image,
        width: width,
        height: height,
        interpolation: img.Interpolation.linear,
      );

      return Uint8List.fromList(img.encodeJpg(resized));
    } catch (e) {
      log.error('❌ Resize 圖片失敗: $e');
      return null;
    }
  }

  /// 壓縮圖片（降低檔案大小）
  ///
  /// [imageBytes]: 原始圖片 bytes
  /// [quality]: 壓縮品質 (0-100)，預設 85
  ///
  /// Returns: 壓縮後的圖片 bytes
  static Uint8List? compressImage(
    Uint8List imageBytes, {
    int quality = 85,
  }) {
    try {
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        log.error('❌ 無法解碼圖片');
        return null;
      }

      return Uint8List.fromList(img.encodeJpg(image, quality: quality));
    } catch (e) {
      log.error('❌ 壓縮圖片失敗: $e');
      return null;
    }
  }

  /// 裁切圖片為正方形（中心裁切）
  ///
  /// [imageBytes]: 原始圖片 bytes
  ///
  /// Returns: 裁切後的正方形圖片 bytes
  static Uint8List? cropSquare(Uint8List imageBytes) {
    try {
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        log.error('❌ 無法解碼圖片');
        return null;
      }

      final size = image.width < image.height ? image.width : image.height;
      final x = (image.width - size) ~/ 2;
      final y = (image.height - size) ~/ 2;

      final cropped = img.copyCrop(
        image,
        x: x,
        y: y,
        width: size,
        height: size,
      );

      return Uint8List.fromList(img.encodeJpg(cropped));
    } catch (e) {
      log.error('❌ 裁切圖片失敗: $e');
      return null;
    }
  }

  /// 轉換圖片為 RGB 格式
  ///
  /// [imageBytes]: 原始圖片 bytes
  ///
  /// Returns: RGB 格式的圖片 bytes
  static Uint8List? convertToRGB(Uint8List imageBytes) {
    try {
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        log.error('❌ 無法解碼圖片');
        return null;
      }

      // 確保圖片為 RGB 格式
      final rgb = img.Image.from(image);
      return Uint8List.fromList(img.encodeJpg(rgb));
    } catch (e) {
      log.error('❌ 轉換圖片格式失敗: $e');
      return null;
    }
  }

  /// 取得圖片尺寸
  ///
  /// [imageBytes]: 圖片 bytes
  ///
  /// Returns: (width, height)，失敗時回傳 null
  static (int, int)? getImageSize(Uint8List imageBytes) {
    try {
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        return null;
      }

      return (image.width, image.height);
    } catch (e) {
      log.error('❌ 取得圖片尺寸失敗: $e');
      return null;
    }
  }

  /// 刪除圖片檔案
  ///
  /// [imagePath]: 圖片檔案路徑
  ///
  /// Returns: 刪除是否成功
  static Future<bool> deleteImage(String imagePath) async {
    try {
      final file = File(imagePath);
      if (await file.exists()) {
        await file.delete();

        // 從快取中移除
        cache.removeImage(imagePath);

        log.info('✅ 圖片已刪除: $imagePath');
        return true;
      } else {
        log.warning('⚠️  圖片檔案不存在: $imagePath');
        return false;
      }
    } catch (e) {
      log.error('❌ 刪除圖片失敗', e);
      return false;
    }
  }

  /// 檢查圖片檔案是否存在
  ///
  /// [imagePath]: 圖片檔案路徑
  ///
  /// Returns: 檔案是否存在
  static Future<bool> imageExists(String imagePath) async {
    try {
      final file = File(imagePath);
      return await file.exists();
    } catch (e) {
      return false;
    }
  }

  /// 取得應用程式圖片目錄
  ///
  /// Returns: 圖片目錄路徑
  static Future<String> getImagesDirectory() async {
    final directory = await getApplicationDocumentsDirectory();
    final imagesDir = Directory(path.join(directory.path, 'images'));

    if (!await imagesDir.exists()) {
      await imagesDir.create(recursive: true);
    }

    return imagesDir.path;
  }

  /// 清理所有圖片（謹慎使用！）
  ///
  /// Returns: 刪除的圖片數量
  static Future<int> clearAllImages() async {
    try {
      final imagesDir = await getImagesDirectory();
      final directory = Directory(imagesDir);

      int count = 0;
      if (await directory.exists()) {
        await for (final entity in directory.list()) {
          if (entity is File) {
            await entity.delete();
            count++;
          }
        }
      }

      log.error('✅ 已清理 $count 張圖片');
      return count;
    } catch (e) {
      log.error('❌ 清理圖片失敗: $e');
      return 0;
    }
  }
}
