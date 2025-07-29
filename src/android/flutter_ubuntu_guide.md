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

## 6. 安裝 Android 開發環境（僅 SDK）

### 6.1 安裝 Android SDK Command Line Tools
```bash
# 創建 Android SDK 目錄
mkdir -p ~/Android/Sdk
cd ~/Android/Sdk

# 下載 Command Line Tools（最新版本）
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip

# 解壓縮到正確位置
unzip commandlinetools-linux-*_latest.zip
mkdir -p cmdline-tools/latest
mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true

# 清理下載檔案
rm commandlinetools-linux-*_latest.zip
```

### 6.2 設定 Android SDK 環境變數
```bash
echo 'export ANDROID_HOME="$HOME/Android/Sdk"' >> ~/.bashrc
echo 'export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"' >> ~/.bashrc
echo 'export PATH="$PATH:$ANDROID_HOME/platform-tools"' >> ~/.bashrc
echo 'export PATH="$PATH:$ANDROID_HOME/emulator"' >> ~/.bashrc
source ~/.bashrc
```

### 6.3 安裝必要的 SDK 組件
```bash
# 更新 SDK 管理器
sdkmanager --update

# 安裝基本組件
sdkmanager "platform-tools" "build-tools;34.0.0" "platforms;android-34"

# 安裝額外推薦組件
sdkmanager "build-tools;33.0.0" "platforms;android-33"
sdkmanager "extras;android;m2repository" "extras;google;m2repository"

# 如果需要模擬器
sdkmanager "emulator" "system-images;android-34;google_apis;x86_64"
```

### 6.4 驗證 Android SDK 安裝
```bash
# 檢查安裝的組件
sdkmanager --list_installed

# 檢查 ADB 工具
adb version
```

### 6.5 接受 Android 授權
```bash
flutter doctor --android-licenses
```
全部輸入 `y` 同意授權。

### 6.6 創建 Android 虛擬裝置（可選）
```bash
# 創建 AVD
avdmanager create avd -n "flutter_emulator" -k "system-images;android-34;google_apis;x86_64"

# 啟動模擬器
emulator -avd flutter_emulator
```

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

# 如果缺少特定 Android SDK 組件
sdkmanager --list  # 查看可用組件
sdkmanager "組件名稱"  # 安裝特定組件

# 檢查 Flutter 與 Android SDK 的整合狀態
flutter doctor -v
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

# 給予 Android SDK 工具執行權限
chmod +x ~/Android/Sdk/cmdline-tools/latest/bin/*
```

## 14. Android SDK 管理指令

### 查看和管理 SDK 組件
```bash
# 列出所有可用組件
sdkmanager --list

# 列出已安裝組件
sdkmanager --list_installed

# 更新所有已安裝組件
sdkmanager --update

# 安裝特定組件
sdkmanager "platforms;android-33" "build-tools;33.0.0"

# 解除安裝組件
sdkmanager --uninstall "組件名稱"
```

### 管理 Android 虛擬裝置
```bash
# 列出可用的系統映像
sdkmanager --list | grep system-images

# 列出已創建的 AVD
avdmanager list avd

# 刪除 AVD
avdmanager delete avd -n "AVD名稱"
```

## 15. 效能最佳化建議

### 開發階段
- 使用 `flutter run --hot-reload` 進行快速開發
- 使用 `flutter run --profile` 測試效能

### Release 階段
- 啟用程式碼混淆：`flutter build apk --obfuscate --split-debug-info=build/debug-info`
- 針對不同 CPU 架構建置：`flutter build apk --split-per-abi`

## 16. 驗證完整設定
最後執行完整驗證：
```bash
flutter doctor -v
```
確保所有項目都是綠色勾勾！

預期看到的輸出應該包含：
- ✅ Flutter (安裝正確)
- ✅ Android toolchain (Android SDK 可用)
- ✅ Chrome (Web 開發)
- ✅ Linux toolchain (Desktop 開發)

---

**注意事項**：
- 這種方式比安裝完整 Android Studio 輕量很多，僅安裝開發必需的工具
- iOS 開發仍需 macOS 環境進行最終建置和測試
- Linux desktop 支援需要 Flutter 3.0+
- Web 版本建議使用現代瀏覽器（Chrome、Firefox、Safari、Edge）
- 如果後續需要 Android Studio 的 IDE 功能，可以單獨安裝，它會自動偵測現有的 SDK
