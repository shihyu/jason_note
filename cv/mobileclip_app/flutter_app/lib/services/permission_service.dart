import 'dart:io';
import 'package:permission_handler/permission_handler.dart';
import 'package:device_info_plus/device_info_plus.dart';

/// 權限處理服務
///
/// 統一管理應用程式所需的權限請求
class PermissionService {
  /// 請求相機權限
  static Future<bool> requestCameraPermission() async {
    final status = await Permission.camera.status;

    if (status.isGranted) {
      return true;
    }

    if (status.isDenied) {
      final result = await Permission.camera.request();
      return result.isGranted;
    }

    if (status.isPermanentlyDenied) {
      await openAppSettings();
      return false;
    }

    return false;
  }

  /// 請求儲存空間權限（Android）
  static Future<bool> requestStoragePermission() async {
    // Android 13+ 不需要儲存權限
    if (await _isAndroid13OrHigher()) {
      return true;
    }

    final status = await Permission.storage.status;

    if (status.isGranted) {
      return true;
    }

    if (status.isDenied) {
      final result = await Permission.storage.request();
      return result.isGranted;
    }

    if (status.isPermanentlyDenied) {
      await openAppSettings();
      return false;
    }

    return false;
  }

  /// 請求照片權限（iOS 和 Android 13+）
  static Future<bool> requestPhotosPermission() async {
    final status = await Permission.photos.status;

    if (status.isGranted || status.isLimited) {
      return true;
    }

    if (status.isDenied) {
      final result = await Permission.photos.request();
      return result.isGranted || result.isLimited;
    }

    if (status.isPermanentlyDenied) {
      await openAppSettings();
      return false;
    }

    return false;
  }

  /// 檢查並請求所有必要權限
  static Future<bool> requestAllPermissions() async {
    final cameraGranted = await requestCameraPermission();
    if (!cameraGranted) return false;

    // 根據平台請求對應的儲存權限
    if (await _isAndroid13OrHigher()) {
      final photosGranted = await requestPhotosPermission();
      return photosGranted;
    } else {
      final storageGranted = await requestStoragePermission();
      return storageGranted;
    }
  }

  /// 檢查是否為 Android 13 或更高版本
  static Future<bool> _isAndroid13OrHigher() async {
    if (!Platform.isAndroid) return false;

    try {
      final deviceInfo = DeviceInfoPlugin();
      final androidInfo = await deviceInfo.androidInfo;
      // Android 13 = API level 33
      return androidInfo.version.sdkInt >= 33;
    } catch (e) {
      // 出錯時假設為舊版
      return false;
    }
  }

  /// 檢查相機權限狀態
  static Future<bool> isCameraPermissionGranted() async {
    final status = await Permission.camera.status;
    return status.isGranted;
  }

  /// 檢查儲存權限狀態
  static Future<bool> isStoragePermissionGranted() async {
    if (await _isAndroid13OrHigher()) {
      final status = await Permission.photos.status;
      return status.isGranted || status.isLimited;
    } else {
      final status = await Permission.storage.status;
      return status.isGranted;
    }
  }
}
