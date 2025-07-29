# Ubuntu 24.04 安裝 Flutter ＆ 建立 Web/Android/iOS 編譯範例

## 1. 安裝必要套件
```bash
sudo apt update
sudo apt upgrade
sudo apt install curl git unzip xz-utils zip libglu1-mesa clang cmake ninja-build pkg-config libgtk-3-dev
```

## 2. 安裝 Java Development Kit (JDK)
Flutter Android 開發需要 JDK 17 或更高版本：
```bash
sudo apt install openjdk-17-jdk
java -version  # 驗證安裝
```

## 3. 下載並安裝 Flutter
### 方法一：直接下載穩定版本
```bash
cd ~/
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.3-stable.tar.xz
tar xf flutter_linux_3.24.3-stable.tar.xz
```

### 方法二：Git clone（開發版本）
```bash
cd ~/
git clone https://github.com/flutter/flutter.git -b stable
```

## 4. 設定環境變數
### 臨時設定
```bash
export PATH="$HOME/flutter/bin:$PATH"
```

### 永久設定
```bash
echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 5. 驗證基本安裝
```bash
flutter doctor
```

## 6. 安裝 Android 開發環境

### 6.1 下載並安裝 Android Studio
```bash
# 下載 Android Studio
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.3.1.18/android-studio-2023.3.1.18-linux.tar.gz

# 解壓縮
tar -xzf android-studio-*.tar.gz -C ~/

# 啟動安裝程式
~/android-studio/bin/studio.sh
```

### 6.2 Android Studio 安裝步驟
1. 選擇 "Standard" 安裝類型
2. 確保安裝以下組件：
   - Android SDK
   - Android SDK Platform-Tools
   - Android SDK Build-Tools
   - Android Emulator
   - Android SDK Command-line Tools

### 6.3 設定 Android SDK 環境變數
```bash
echo 'export ANDROID_HOME="$HOME/Android/Sdk"' >> ~/.bashrc
echo 'export PATH="$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 6.4 接受 Android 授權
```bash
flutter doctor --android-licenses
```
全部輸入 `y` 同意授權。

## 7. iOS 開發環境（Linux 限制說明）

### 7.1 在 Linux 上的 iOS 開發限制
- ✅ **可以做的**：編寫 iOS 程式碼、檢查語法、管理專案
- ❌ **無法做的**：編譯 iOS app、執行 iOS 模擬器、發布到 App Store

### 7.2 iOS 驗證替代方案（無需 iPhone）
如果你想驗證 iOS 程式碼但沒有實體裝置：

```bash
# 建立專案時確保包含 iOS 平台
flutter create --platforms=web,android,ios my_app

# 檢查 iOS 專案結構
ls -la my_app/ios/

# 驗證 iOS 設定檔
flutter analyze
```

### 7.3 使用線上 iOS 編譯服務
- **CodeMagic**：提供雲端 macOS 環境
- **GitHub Actions**：使用 macOS runner
- **Bitrise**：支援 Flutter iOS 建構

## 8. 建立多平台 Flutter 專案
```bash
flutter create --platforms=web,android,ios my_demo_app
cd my_demo_app
```

## 9. 驗證所有平台支援
```bash
flutter devices
```
預期輸出應包含：
- Chrome (web)
- Android 裝置或模擬器
- Linux (desktop) - Flutter 3.0+ 支援

## 10. 執行範例

### Web 版本
```bash
flutter run -d chrome
# 或指定埠號
flutter run -d web-server --web-port=8080
```

### Android 版本
```bash
# 列出可用裝置
flutter devices

# 在特定裝置上執行
flutter run -d [device-id]

# 或直接執行（會自動選擇裝置）
flutter run
```

### Linux Desktop 版本
```bash
flutter run -d linux
```

## 11. 建立 Release 版本

### Web
```bash
flutter build web
# 輸出在 build/web/ 目錄
```

### Android APK
```bash
flutter build apk --release
# 輸出在 build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (推薦用於 Play Store)
```bash
flutter build appbundle --release
```

### Linux Desktop
```bash
flutter build linux --release
```

## 12. 範例程式碼

### `lib/main.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter 多平台 Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  String get platformInfo {
    if (kIsWeb) {
      return 'Web 平台';
    } else if (Platform.isAndroid) {
      return 'Android 平台';
    } else if (Platform.isIOS) {
      return 'iOS 平台';
    } else if (Platform.isLinux) {
      return 'Linux 平台';
    } else if (Platform.isWindows) {
      return 'Windows 平台';
    } else if (Platform.isMacOS) {
      return 'macOS 平台';
    } else {
      return '未知平台';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flutter 多平台測試'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.flutter_dash,
              size: 100,
              color: Colors.blue,
            ),
            const SizedBox(height: 20),
            Text(
              '你好，Flutter！',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 10),
            Text(
              '當前運行在：$platformInfo',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('在 $platformInfo 上點擊成功！'),
                    duration: const Duration(seconds: 2),
                  ),
                );
              },
              child: const Text('測試按鈕'),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        tooltip: '增加',
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

## 13. 常見問題處理

### Android 相關
```bash
# 如果 Android 裝置未偵測到
adb devices
sudo usermod -aG plugdev $USER  # 加入用戶組
# 重新登入或重啟

# 如果缺少 Android SDK
flutter doctor  # 查看詳細錯誤訊息
```

### Web 相關
```bash
# 如果 Web 支援未啟用
flutter config --enable-web

# 清除快取重新建置
flutter clean
flutter pub get
```

### 權限問題
```bash
# 給予 Flutter 執行權限
chmod +x ~/flutter/bin/flutter
```

## 14. 效能最佳化建議

### 開發階段
- 使用 `flutter run --hot-reload` 進行快速開發
- 使用 `flutter run --profile` 測試效能

### Release 階段
- 啟用程式碼混淆：`flutter build apk --obfuscate --split-debug-info=build/debug-info`
- 針對不同 CPU 架構建置：`flutter build apk --split-per-abi`

## 15. 驗證完整設定
最後執行完整驗證：
```bash
flutter doctor -v
```
確保所有項目都是綠色勾勾！

---

**注意事項**：
- iOS 開發仍需 macOS 環境進行最終建置和測試
- Linux desktop 支援需要 Flutter 3.0+
- Web 版本建議使用現代瀏覽器（Chrome、Firefox、Safari、Edge）