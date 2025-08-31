# Android APK .so 檔案路徑查詢指南

## 目錄
- [APK 安裝後 .so 檔案的位置](#apk-安裝後-so-檔案的位置)
- [查詢方法](#查詢方法)
- [權限問題處理](#權限問題處理)
- [實際案例](#實際案例)
- [實用腳本](#實用腳本)

## APK 安裝後 .so 檔案的位置

### 主要路徑結構
```bash
# 標準路徑格式
/data/app/[package_name]-[random_string]/lib/[arch]/

# 實際範例
/data/app/com.example.app-1A2B3C4D5E6F7G8H/lib/arm64/
/data/app/com.example.app-1A2B3C4D5E6F7G8H/lib/arm/
```

### 依據 CPU 架構分類

#### 64 位元架構
```bash
/data/app/[package_name]-*/lib/arm64/        # ARM 64-bit
/data/app/[package_name]-*/lib/arm64-v8a/    # ARMv8-A
```

#### 32 位元架構
```bash
/data/app/[package_name]-*/lib/arm/          # ARM 32-bit
/data/app/[package_name]-*/lib/armeabi-v7a/  # ARMv7
```

#### x86 架構
```bash
/data/app/[package_name]-*/lib/x86/          # Intel x86
/data/app/[package_name]-*/lib/x86_64/       # Intel x86-64
```

### 其他可能位置

#### 系統應用程式
```bash
/system/app/[app_name]/lib/[arch]/
/system/priv-app/[app_name]/lib/[arch]/
```

#### Vendor/ODM 應用程式
```bash
/vendor/app/[app_name]/lib/[arch]/
/odm/app/[app_name]/lib/[arch]/
```

## 查詢方法

### 方法 1：使用 PM 命令
```bash
# 找到應用程式的基本路徑
adb shell pm path com.example.app
# 輸出: package:/data/app/com.example.app-xxxxx/base.apk

# 提取路徑並查看 lib 目錄
adb shell ls -la /data/app/com.example.app-*/lib/
```

### 方法 2：使用 Dumpsys
```bash
# 查看 native library 路徑
adb shell dumpsys package com.example.app | grep -A 5 "nativeLibraryPath"

# 查看 CPU ABI 資訊
adb shell dumpsys package com.example.app | grep -E "primaryCpuAbi|nativeLibraryPath"
```

### 方法 3：直接搜尋 .so 檔案
```bash
# 搜尋特定應用的 .so 檔案
adb shell find /data/app -name "*.so" | grep com.example.app

# 搜尋特定的 .so 檔案
adb shell find /data -name "libnative.so" 2>/dev/null
```

### 方法 4：從 APK 檔案提取
```bash
# 拉取 APK 到本地
adb pull [apk_path] app.apk

# 查看 APK 內的 .so 檔案
unzip -l app.apk | grep "\.so$"

# 解壓 lib 目錄
unzip app.apk "lib/*"
```

## 權限問題處理

### 問題：Permission denied
當執行 `ls /data` 時遇到權限錯誤：
```bash
ls: .: Permission denied
```

### 解決方案

#### 1. 使用 run-as（不需要 root）
```bash
# 進入應用程式沙盒
adb shell run-as com.example.app

# 查看應用檔案
ls -la
cd /data/data/com.example.app
```

#### 2. 使用不需要 root 的命令
```bash
# 取得 APK 路徑
adb shell pm path com.example.app

# 使用 dumpsys
adb shell dumpsys package com.example.app | grep -E "path|lib|abi"

# 查看應用程式資訊
adb shell pm dump com.example.app | grep -A 10 "nativeLibrary"
```

#### 3. 可直接存取的目錄
```bash
# 外部儲存空間
adb shell ls /sdcard/
adb shell ls /storage/emulated/0/

# 系統目錄（部分可讀）
adb shell ls /system/lib/
adb shell ls /system/lib64/
```

#### 4. Root 設備
```bash
# 切換到 root
adb root

# 或在 shell 中
adb shell
su

# 現在可以存取 /data
ls /data/app/
```

## 實際案例

### 案例：com.nonpolynomial.intiface_central

#### 1. 取得 Package 路徑
```bash
adb shell pm path com.nonpolynomial.intiface_central
```

輸出：
```
package:/data/app/~~hfhY-MZu68IvQToRMdCNmQ==/com.nonpolynomial.intiface_central-fxpbD5fI51_9doDpAWttpQ==/base.apk
```

#### 2. 查詢 Native Library 資訊
```bash
# 查看 native library 路徑和 ABI
adb shell dumpsys package com.nonpolynomial.intiface_central | grep -E "nativeLibraryPath|primaryCpuAbi|secondaryCpuAbi|Libraries"
```

#### 3. 預期的 .so 檔案位置
```bash
# ARM 64-bit
/data/app/~~hfhY-MZu68IvQToRMdCNmQ==/com.nonpolynomial.intiface_central-fxpbD5fI51_9doDpAWttpQ==/lib/arm64-v8a/

# ARM 32-bit
/data/app/~~hfhY-MZu68IvQToRMdCNmQ==/com.nonpolynomial.intiface_central-fxpbD5fI51_9doDpAWttpQ==/lib/armeabi-v7a/

# x86_64
/data/app/~~hfhY-MZu68IvQToRMdCNmQ==/com.nonpolynomial.intiface_central-fxpbD5fI51_9doDpAWttpQ==/lib/x86_64/
```

#### 4. 從 APK 提取查看
```bash
# 拉取 APK
adb pull /data/app/~~hfhY-MZu68IvQToRMdCNmQ==/com.nonpolynomial.intiface_central-fxpbD5fI51_9doDpAWttpQ==/base.apk

# 查看內部的 .so 檔案
unzip -l base.apk | grep "lib.*\.so$"
```

## 實用腳本

### 查詢 .so 檔案腳本
```bash
#!/bin/bash
# find_so.sh - 查詢 APK 的 .so 檔案

PACKAGE=$1

if [ -z "$PACKAGE" ]; then
    echo "Usage: $0 <package_name>"
    exit 1
fi

echo "=== Package Info for $PACKAGE ==="

# 取得 APK 路徑
APK_PATH=$(adb shell pm path $PACKAGE | cut -d: -f2 | tr -d '\r')
echo "APK Path: $APK_PATH"

# 取得 native library 資訊
echo -e "\n=== Native Library Info ==="
adb shell dumpsys package $PACKAGE | grep -E "nativeLibraryPath|primaryCpuAbi|secondaryCpuAbi"

# 嘗試解壓 APK 查看 .so 檔案
echo -e "\n=== Extracting APK to check .so files ==="
adb pull $APK_PATH /tmp/${PACKAGE}.apk 2>/dev/null
if [ -f /tmp/${PACKAGE}.apk ]; then
    unzip -l /tmp/${PACKAGE}.apk | grep "\.so$"
    rm /tmp/${PACKAGE}.apk
fi
```

### 一鍵查詢命令
```bash
# 執行這個命令組合來取得所有資訊
adb shell "
pkg='com.example.app'
echo '=== APK 路徑 ==='
pm path \$pkg

echo '=== Native Library 路徑 ==='
base_path=\$(pm path \$pkg | cut -d: -f2 | sed 's/base.apk//')
ls -la \${base_path}lib/ 2>/dev/null || echo '需要 root 權限查看'

echo '=== CPU ABI ==='
dumpsys package \$pkg | grep -E 'primaryCpuAbi|secondaryCpuAbi'
"
```

### 查看執行中程序載入的 .so
```bash
# 查看執行中程序載入的 .so
adb shell "
pid=\$(pidof com.example.app)
if [ -n \"\$pid\" ]; then
    cat /proc/\$pid/maps | grep '\.so'
fi
"

# 使用 lsof
adb shell lsof | grep com.example.app | grep "\.so"
```

## 在應用程式內取得路徑

### Java/Kotlin 程式碼
```java
// 取得 native library 目錄
String nativeLibraryDir = getApplicationInfo().nativeLibraryDir;
Log.d("TAG", "Native libs: " + nativeLibraryDir);

// 列出所有 .so 檔案
File libDir = new File(nativeLibraryDir);
File[] soFiles = libDir.listFiles((dir, name) -> name.endsWith(".so"));
for (File soFile : soFiles) {
    Log.d("TAG", "Found .so: " + soFile.getAbsolutePath());
}
```

## 注意事項

1. **權限限制**：大部分 `/data/app` 目錄需要 root 權限才能直接存取
2. **架構相容性**：不同裝置可能使用不同的 CPU 架構，.so 檔案會在對應的架構目錄下
3. **安全性**：生產環境的 APK 通常會對 .so 檔案進行加密或混淆
4. **Split APK**：使用 App Bundle 的應用可能會有多個 APK 檔案，.so 可能分散在不同的 split APK 中

## 疑難排解

### 找不到 .so 檔案
1. 確認 APK 是否包含 native code：
   ```bash
   aapt dump badging app.apk | grep native-code
   ```

2. 檢查是否為 Split APK：
   ```bash
   adb shell pm path com.example.app
   # 可能會顯示多個 APK 路徑
   ```

3. 確認應用程式的 ABI：
   ```bash
   adb shell getprop ro.product.cpu.abi
   adb shell getprop ro.product.cpu.abilist
   ```

### 權限不足
如果沒有 root 權限，建議：
1. 使用 `pm` 和 `dumpsys` 命令獲取資訊
2. 直接從 APK 檔案提取和分析
3. 使用 `run-as` 命令（僅限 debuggable 應用）
4. 使用模擬器或已 root 的測試裝置

## 參考資源

- [Android Developer - APK 結構](https://developer.android.com/topic/performance/reduce-apk-size)
- [Android NDK 文檔](https://developer.android.com/ndk)
- [ADB 命令參考](https://developer.android.com/studio/command-line/adb)