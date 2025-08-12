# Android Native (C/C++/Rust) 與 Flutter 整合完整指南

## 整合方案比較

| 方案 | 複雜度 | 性能 | 維護性 | 適用場景 |
|------|--------|------|--------|----------|
| **FFI 直接調用** | 🟡 中 | 🟢 最高 | 🟢 好 | 純 Dart ↔ Native |
| **Platform Channel + JNI** | 🔴 高 | 🟡 中 | 🔴 複雜 | 需要 Android 特定功能 |
| **Method Channel + NDK** | 🔴 高 | 🟢 高 | 🔴 複雜 | 複雜 Android 整合 |

---

## 方案 1: FFI 直接調用 (推薦)

### 概述
Dart FFI 直接調用編譯後的 native 動態庫，跳過 JNI 層，性能最佳。

### 架構流程
```
Flutter (Dart) → FFI → Native Library (.so) → Rust/C/C++ Code
```

### 完整實現

#### Step 1: Rust 庫 (native/src/lib.rs)
```rust
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn hello_from_rust(name: *const c_char) -> *mut c_char {
    let c_str = unsafe { CStr::from_ptr(name) };
    let name_str = c_str.to_str().unwrap_or("Unknown");
    let response = format!("Hello {}, from Rust!", name_str);
    CString::new(response).unwrap().into_raw()
}

#[no_mangle]
pub extern "C" fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}

#[no_mangle]
pub extern "C" fn free_rust_string(s: *mut c_char) {
    if !s.is_null() {
        unsafe { CString::from_raw(s) };
    }
}

// Android 日誌支援
#[cfg(target_os = "android")]
use android_logger::{Config, FilterBuilder};

#[cfg(target_os = "android")]
#[no_mangle]
pub extern "C" fn init_android_logger() {
    android_logger::init_once(
        Config::default()
            .with_min_level(log::Level::Debug)
            .with_tag("RustFFI")
            .with_filter(FilterBuilder::new().parse("debug").build())
    );
    log::info!("Rust FFI logger initialized for Android");
}
```

#### Step 2: Cargo.toml
```toml
[package]
name = "flutter_native"
version = "0.1.0"
edition = "2021"

[lib]
name = "flutter_native"
crate-type = ["cdylib"]

[dependencies]
# Android 特定
[target.'cfg(target_os = "android")'.dependencies]
android_logger = "0.13"
log = "0.4"

# 編譯優化
[profile.release]
lto = true
opt-level = 3
strip = true
```

#### Step 3: 編譯腳本 (scripts/build_android.sh)
```bash
#!/bin/bash

# 設置 Android NDK 路徑
export ANDROID_NDK_HOME="/path/to/android-ndk"
export PATH="$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin:$PATH"

# 添加 Android 目標
rustup target add aarch64-linux-android
rustup target add armv7-linux-androideabi
rustup target add x86_64-linux-android
rustup target add i686-linux-android

# 設置 linker
export CC_aarch64_linux_android=aarch64-linux-android21-clang
export CC_armv7_linux_androideabi=armv7a-linux-androideabi21-clang
export CC_x86_64_linux_android=x86_64-linux-android21-clang
export CC_i686_linux_android=i686-linux-android21-clang

# 編譯各個架構
echo "Building for Android architectures..."

cargo build --target aarch64-linux-android --release
cargo build --target armv7-linux-androideabi --release
cargo build --target x86_64-linux-android --release
cargo build --target i686-linux-android --release

# 複製到 Android jniLibs
mkdir -p ../android/app/src/main/jniLibs/arm64-v8a
mkdir -p ../android/app/src/main/jniLibs/armeabi-v7a
mkdir -p ../android/app/src/main/jniLibs/x86_64
mkdir -p ../android/app/src/main/jniLibs/x86

cp target/aarch64-linux-android/release/libflutter_native.so ../android/app/src/main/jniLibs/arm64-v8a/
cp target/armv7-linux-androideabi/release/libflutter_native.so ../android/app/src/main/jniLibs/armeabi-v7a/
cp target/x86_64-linux-android/release/libflutter_native.so ../android/app/src/main/jniLibs/x86_64/
cp target/i686-linux-android/release/libflutter_native.so ../android/app/src/main/jniLibs/x86/

echo "Android libraries copied to jniLibs"
```

#### Step 4: Flutter FFI 綁定 (lib/native_bridge.dart)
```dart
import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

// 函數簽名定義
typedef HelloFromRustNative = Pointer<Utf8> Function(Pointer<Utf8>);
typedef HelloFromRust = Pointer<Utf8> Function(Pointer<Utf8>);

typedef AddNumbersNative = Int32 Function(Int32, Int32);
typedef AddNumbers = int Function(int, int);

typedef FreeRustStringNative = Void Function(Pointer<Utf8>);
typedef FreeRustString = void Function(Pointer<Utf8>);

typedef InitAndroidLoggerNative = Void Function();
typedef InitAndroidLogger = void Function();

class NativeBridge {
  static DynamicLibrary? _lib;
  static late HelloFromRust _helloFromRust;
  static late AddNumbers _addNumbers;
  static late FreeRustString _freeRustString;
  static late InitAndroidLogger _initAndroidLogger;

  static void initialize() {
    // 加載 native 庫
    if (Platform.isAndroid) {
      _lib = DynamicLibrary.open('libflutter_native.so');
    } else if (Platform.isIOS) {
      _lib = DynamicLibrary.process();
    } else {
      throw UnsupportedError('Platform not supported');
    }

    // 綁定函數
    _helloFromRust = _lib!.lookupFunction<HelloFromRustNative, HelloFromRust>('hello_from_rust');
    _addNumbers = _lib!.lookupFunction<AddNumbersNative, AddNumbers>('add_numbers');
    _freeRustString = _lib!.lookupFunction<FreeRustStringNative, FreeRustString>('free_rust_string');
    
    // Android 特定初始化
    if (Platform.isAndroid) {
      _initAndroidLogger = _lib!.lookupFunction<InitAndroidLoggerNative, InitAndroidLogger>('init_android_logger');
      _initAndroidLogger();
    }
  }

  static String helloFromRust(String name) {
    final namePtr = name.toNativeUtf8();
    final resultPtr = _helloFromRust(namePtr);
    
    final result = resultPtr.toDartString();
    
    // 釋放記憶體
    malloc.free(namePtr);
    _freeRustString(resultPtr);
    
    return result;
  }

  static int addNumbers(int a, int b) {
    return _addNumbers(a, b);
  }
}
```

#### Step 5: Flutter 使用範例
```dart
import 'package:flutter/material.dart';
import 'native_bridge.dart';

void main() {
  NativeBridge.initialize();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Native FFI Demo',
      home: NativeDemo(),
    );
  }
}

class NativeDemo extends StatefulWidget {
  @override
  _NativeDemoState createState() => _NativeDemoState();
}

class _NativeDemoState extends State<NativeDemo> {
  String _result = 'No result';
  final _nameController = TextEditingController();
  final _num1Controller = TextEditingController();
  final _num2Controller = TextEditingController();

  void _callRustHello() {
    final name = _nameController.text.isEmpty ? 'World' : _nameController.text;
    final result = NativeBridge.helloFromRust(name);
    setState(() => _result = result);
  }

  void _callRustAdd() {
    final num1 = int.tryParse(_num1Controller.text) ?? 0;
    final num2 = int.tryParse(_num2Controller.text) ?? 0;
    final result = NativeBridge.addNumbers(num1, num2);
    setState(() => _result = 'Result: $result');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Native FFI Demo')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _nameController,
              decoration: InputDecoration(labelText: 'Name'),
            ),
            ElevatedButton(
              onPressed: _callRustHello,
              child: Text('Call Rust Hello'),
            ),
            SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _num1Controller,
                    decoration: InputDecoration(labelText: 'Number 1'),
                    keyboardType: TextInputType.number,
                  ),
                ),
                SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: _num2Controller,
                    decoration: InputDecoration(labelText: 'Number 2'),
                    keyboardType: TextInputType.number,
                  ),
                ),
              ],
            ),
            ElevatedButton(
              onPressed: _callRustAdd,
              child: Text('Add Numbers'),
            ),
            SizedBox(height: 20),
            Text('Result: $_result', style: Theme.of(context).textTheme.titleLarge),
          ],
        ),
      ),
    );
  }
}
```

---

## 方案 2: Platform Channel + JNI

### 概述
透過 Platform Channel 呼叫 Android Kotlin/Java 代碼，再透過 JNI 調用 native 庫。

### 架構流程
```
Flutter (Dart) → Platform Channel → Android (Kotlin/Java) → JNI → Native (.so) → Rust/C/C++
```

### 實現步驟

#### Step 1: Android Native 實現 (android/app/src/main/cpp/native.cpp)
```cpp
#include <jni.h>
#include <string>
#include <android/log.h>

#define LOG_TAG "NativeLib"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

// 如果要調用 Rust，需要聲明 extern C
extern "C" {
    char* hello_from_rust(const char* name);
    int add_numbers(int a, int b);
    void free_rust_string(char* s);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_myapp_NativeLib_helloFromNative(JNIEnv *env, jclass clazz, jstring name) {
    const char *nativeName = env->GetStringUTFChars(name, nullptr);
    
    // 方式1: 直接 C++ 實現
    std::string result = "Hello " + std::string(nativeName) + " from C++!";
    
    // 方式2: 調用 Rust 函數
    // char* rustResult = hello_from_rust(nativeName);
    // std::string result(rustResult);
    // free_rust_string(rustResult);
    
    env->ReleaseStringUTFChars(name, nativeName);
    return env->NewStringUTF(result.c_str());
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_myapp_NativeLib_addNumbers(JNIEnv *env, jclass clazz, jint a, jint b) {
    LOGI("Adding numbers: %d + %d", a, b);
    
    // 方式1: 直接 C++ 實現
    return a + b;
    
    // 方式2: 調用 Rust 函數
    // return add_numbers(a, b);
}
```

#### Step 2: CMake 配置 (android/app/src/main/cpp/CMakeLists.txt)
```cmake
cmake_minimum_required(VERSION 3.18.1)

project("native")

# 添加 C++ 標準
set(CMAKE_CXX_STANDARD 17)

# 查找依賴
find_library(log-lib log)

# 如果要鏈接 Rust 庫
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libflutter_native.so")
    add_library(rust_lib SHARED IMPORTED)
    set_target_properties(rust_lib PROPERTIES
        IMPORTED_LOCATION "${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libflutter_native.so"
    )
endif()

# 創建 native 庫
add_library(native SHARED native.cpp)

# 鏈接庫
target_link_libraries(native ${log-lib})

# 如果有 Rust 庫，也要鏈接
if(TARGET rust_lib)
    target_link_libraries(native rust_lib)
endif()
```

#### Step 3: Android Kotlin 包裝 (android/app/src/main/kotlin/NativeLib.kt)
```kotlin
package com.example.myapp

class NativeLib {
    companion object {
        // 載入 native 庫
        init {
            System.loadLibrary("native")
        }
        
        // JNI 方法聲明
        @JvmStatic
        external fun helloFromNative(name: String): String
        
        @JvmStatic
        external fun addNumbers(a: Int, b: Int): Int
    }
}
```

#### Step 4: MainActivity Platform Channel (android/app/src/main/kotlin/MainActivity.kt)
```kotlin
package com.example.myapp

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.example.myapp/native"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "helloFromNative" -> {
                        val name = call.argument<String>("name") ?: "World"
                        try {
                            val nativeResult = NativeLib.helloFromNative(name)
                            result.success(nativeResult)
                        } catch (e: Exception) {
                            result.error("NATIVE_ERROR", "Native call failed", e.message)
                        }
                    }
                    "addNumbers" -> {
                        val a = call.argument<Int>("a") ?: 0
                        val b = call.argument<Int>("b") ?: 0
                        try {
                            val nativeResult = NativeLib.addNumbers(a, b)
                            result.success(nativeResult)
                        } catch (e: Exception) {
                            result.error("NATIVE_ERROR", "Native call failed", e.message)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
    }
}
```

#### Step 5: Flutter Platform Channel 調用 (lib/platform_channel_bridge.dart)
```dart
import 'package:flutter/services.dart';

class PlatformChannelBridge {
  static const MethodChannel _channel = MethodChannel('com.example.myapp/native');

  static Future<String> helloFromNative(String name) async {
    try {
      final String result = await _channel.invokeMethod('helloFromNative', {
        'name': name,
      });
      return result;
    } on PlatformException catch (e) {
      throw Exception('Failed to call native: ${e.message}');
    }
  }

  static Future<int> addNumbers(int a, int b) async {
    try {
      final int result = await _channel.invokeMethod('addNumbers', {
        'a': a,
        'b': b,
      });
      return result;
    } on PlatformException catch (e) {
      throw Exception('Failed to add numbers: ${e.message}');
    }
  }
}
```

#### Step 6: 使用範例
```dart
// 使用 Platform Channel 方式
class PlatformChannelDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          children: [
            ElevatedButton(
              onPressed: () async {
                final result = await PlatformChannelBridge.helloFromNative('Flutter');
                print(result);
              },
              child: Text('Call Native via Platform Channel'),
            ),
            ElevatedButton(
              onPressed: () async {
                final result = await PlatformChannelBridge.addNumbers(5, 3);
                print('Result: $result');
              },
              child: Text('Add Numbers via Platform Channel'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 建構配置

### Android build.gradle 配置
```gradle
// android/app/build.gradle
android {
    compileSdkVersion 34
    ndkVersion "25.1.8937393"
    
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a', 'x86_64', 'x86'
        }
    }
    
    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
            version "3.18.1"
        }
    }
    
    sourceSets {
        main {
            jniLibs.srcDirs = ['src/main/jniLibs']
        }
    }
}
```

### pubspec.yaml 配置
```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  ffi: ^2.0.1

# FFI 方式需要
assets:
  - assets/

# Plugin 配置 (如果要發布為 plugin)
flutter:
  plugin:
    platforms:
      android:
        package: com.example.native_plugin
        pluginClass: NativePlugin
```

---

## 除錯和測試

### Android 日誌查看
```bash
# 查看所有日誌
adb logcat

# 只查看特定 tag
adb logcat -s "RustFFI"
adb logcat -s "NativeLib"

# 查看 Flutter 日誌
adb logcat -s "flutter"
```

### 常見問題和解決方案

#### 1. 庫找不到
```
java.lang.UnsatisfiedLinkError: dlopen failed: library "libflutter_native.so" not found
```
**解決方案：**
- 檢查 `.so` 檔案是否正確放在 `jniLibs` 對應架構資料夾
- 確認檔案名稱正確（必須以 `lib` 開頭）
- 檢查 build.gradle 中的 `abiFilters` 設定

#### 2. 符號找不到
```
java.lang.UnsatisfiedLinkError: No implementation found for native method
```
**解決方案：**
- 檢查 C/C++ 函數名稱是否與 JNI 規範一致
- 確認 `extern "C"` 聲明正確
- 使用 `nm` 或 `objdump` 檢查符號是否存在

#### 3. 記憶體洩漏
**最佳實踐：**
```dart
// 正確的記憶體管理
String callNative(String input) {
  final inputPtr = input.toNativeUtf8();
  try {
    final resultPtr = _nativeFunction(inputPtr);
    final result = resultPtr.toDartString();
    _freeString(resultPtr); // 重要！釋放 native 記憶體
    return result;
  } finally {
    malloc.free(inputPtr); // 重要！釋放 Dart 分配的記憶體
  }
}
```

---

## 效能比較

| 方案 | 調用延遲 | 記憶體使用 | 複雜度 | 維護性 |
|------|----------|------------|--------|--------|
| **FFI 直接** | ~1μs | 低 | 中 | 好 |
| **Platform Channel + JNI** | ~100μs | 中 | 高 | 複雜 |

## 總結建議

### 🥇 推薦：FFI 直接調用
- **優點**：性能最佳、相對簡單、跨平台一致
- **缺點**：需要管理記憶體、不能使用 Android 特定 API
- **適用**：純計算邏輯、跨平台庫

### 🥈 備選：Platform Channel + JNI
- **優點**：可使用完整 Android API、錯誤處理更好
- **缺點**：性能較差、複雜度高、維護困難
- **適用**：需要 Android 特定功能、複雜的系統整合

### 最佳實踐
1. **優先考慮 FFI**：除非必須使用 Android 特定功能
2. **記憶體管理**：務必正確釋放 native 分配的記憶體
3. **錯誤處理**：在所有 native 調用周圍添加異常處理
4. **測試**：在所有目標架構上進行充分測試
5. **日誌**：添加詳細的日誌以便除錯