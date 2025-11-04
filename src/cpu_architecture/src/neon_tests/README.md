# ARM NEON 測試專案

測試 ARM NEON SIMD 指令的效能與正確性，並與純 C 程式碼進行比較。

## 專案結構

```
src/
├── Makefile           # 建置系統
├── README.md          # 本文件
└── neon_tests/        # 測試程式碼
    ├── common.h       # 共用工具函數
    ├── neon_test_add.c       # 向量加法測試
    ├── neon_test_multiply.c  # 向量乘法測試
    ├── neon_test_fma.c       # FMA 測試
    ├── neon_test_compare.c   # 向量比較測試
    ├── neon_test_lookup.c    # 查表測試
    ├── neon_test_minmax.c    # 最大/最小值測試
    └── build/                # 編譯產物
        ├── arm64-v8a/        # ARM64 執行檔
        └── logs/             # 編譯日誌
```

## 快速開始

### 前置需求

1. **Android NDK** (r26d 或更新版本)
   ```bash
   export ANDROID_NDK_HOME=~/android-ndk-r26d
   ```

2. **Android 裝置** (已連接並啟用 ADB)
   ```bash
   adb devices  # 確認裝置已連線
   ```

### 使用方式

#### 1. 顯示說明
```bash
make
# 或
make help
```

#### 2. 編譯所有測試程式
```bash
make build
```

#### 3. 部署到 Android 裝置
```bash
make deploy
```

#### 4. 在裝置上執行測試
```bash
make run
```

#### 5. 完整測試流程（編譯 + 部署 + 執行）
```bash
make test
```

#### 6. 清理編譯產物
```bash
make clean
```

## 測試項目

### 1. 向量加法 (neon_test_add)
- **指令**: `vaddq_f32`
- **應用**: 基本向量運算
- **預期加速**: 2-3x

### 2. 向量乘法 (neon_test_multiply)
- **指令**: `vmulq_f32`
- **應用**: 基本向量運算
- **預期加速**: 2-3x

### 3. FMA (neon_test_fma)
- **指令**: `vfmaq_f32`
- **應用**: 深度學習、科學計算
- **預期加速**: 1.5x (vs 分開計算)

### 4. 向量比較 (neon_test_compare)
- **指令**: `vcgtq_f32`, `vcgeq_f32`, `vcleq_f32`
- **應用**: 圖像閾值處理、條件篩選
- **預期加速**: 3-4x

### 5. 查表 (neon_test_lookup)
- **指令**: `vqtbl1_u8`
- **應用**: 色盤轉換、Gamma 校正
- **預期加速**: 5-6x (16-entry 表)

### 6. 最大/最小值 (neon_test_minmax)
- **指令**: `vmaxq_f32`, `vminq_f32`, `vmaxvq_f32`
- **應用**: 陣列搜尋、Clamp 運算
- **預期加速**: 7-9x (最大值搜尋)

## 測試結果亮點

✅ **所有測試正確性 100% 通過**

🎯 **優異表現**:
- **最大值搜尋**: **8.59x 加速** ⚡
- **16-entry 查表**: **5.57x 加速** ⚡

## 編譯參數

- **優化等級**: `-O3`
- **架構**: `-march=armv8-a+simd`
- **TLS 對齊**: `-Wl,-z,max-page-size=16384` (Android 15 要求)

## 目標平台

- **裝置**: 小米 23049PCD8G
- **系統**: Android 15 (API 35)
- **CPU**: ARM64-v8a
- **特性**: NEON (asimd), FMA, dot product, int8 matrix multiply

## 注意事項

1. **編譯器自動向量化**: `-O3` 會讓純 C 程式碼也使用 NEON，導致某些測試加速比不明顯
2. **真正的 NEON 優勢**: 查表 (vtbl) 和水平歸約 (vmaxvq) 等特殊指令無法被編譯器自動優化
3. **記憶體對齊**: 使用 `memalign(16, size)` 確保 16-byte 對齊

## 參考文件

- [ARM_NEON_完整指南.md](../ARM_NEON_完整指南.md)
- [plan.md](../plan.md)

## License

本專案為教育和測試用途。
