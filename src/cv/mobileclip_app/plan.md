# MobileCLIP 商品識別系統 - 離線 Flutter App

## 專案目標
開發一個**完全離線**的 Flutter 應用，讓使用者能夠：
1. **註冊商品**: 拍照並輸入商品資訊（名稱、描述、價格等），儲存在手機本地
2. **即時辨識**: 開啟相機對準物品，即時顯示是否為已註冊的商品及其資訊
3. **本地運算**: 所有圖片、資料、模型推論都在手機端，無需網路連線

## 技術架構

### 核心技術
- **前端**: Flutter (iOS/Android)
- **模型**: MobileCLIP-S2 (TFLite 或 ONNX Runtime Mobile)
- **資料庫**: SQLite (sqflite package) - 商品資訊
- **圖片儲存**: 手機本地檔案系統 (path_provider)
- **向量儲存**: SQLite BLOB 或 Hive (輕量鍵值存儲)
- **相似度計算**: Dart 原生實作 cosine similarity

### 系統流程
```
[商品註冊流程]
拍照 → 裁切/壓縮 → MobileCLIP 特徵提取 (512維向量)
     → 儲存圖片到本地 → 儲存商品資訊+向量到 SQLite

[即時辨識流程]
Camera frame → 裁切/縮放 → MobileCLIP 特徵提取
     → 與所有已註冊商品向量計算相似度 → 取 Top-1 (相似度>閾值)
     → 疊加顯示在相機畫面上
```

### 為何不需要後端？
✅ 模型輕量 (MobileCLIP-S2 ~15MB TFLite)
✅ 推論速度快 (手機端 20-100ms)
✅ 商品數量有限 (100-1000個)，向量檢索可用純 Dart 實作
✅ 使用者資料隱私更好（不上傳雲端）

## 專案配置
- **模型檔案**: `flutter_app/assets/models/mobileclip_s2.tflite`
- **資料庫路徑**: 手機本地 `app_documents/products.db`
- **圖片儲存路徑**: 手機本地 `app_documents/product_images/`
- **特徵向量維度**: 512 (MobileCLIP-S2)
- **即時辨識頻率**: 每 500ms 處理一幀（可調整）
- **相似度閾值**: 0.7 (低於此值視為「未識別」)

## 預期產出

### 目錄結構
```
app/
├── plan.md                          # 本檔案
├── Makefile                         # 標準建置工具
├── model_conversion/                # 模型轉換工具
│   ├── convert_to_tflite.py        # PyTorch → TFLite 轉換腳本
│   ├── convert_to_onnx.py          # PyTorch → ONNX 轉換腳本
│   ├── test_tflite_model.py        # TFLite 模型測試
│   └── requirements.txt             # Python 依賴
├── flutter_app/                     # Flutter 專案
│   ├── pubspec.yaml                 # Flutter 依賴
│   ├── assets/
│   │   ├── models/
│   │   │   └── mobileclip_s2.tflite  # 轉換後的模型
│   │   └── images/                  # UI 素材
│   ├── lib/
│   │   ├── main.dart                # App 入口
│   │   ├── screens/
│   │   │   ├── home_screen.dart     # 主畫面 (Tab 切換)
│   │   │   ├── register_screen.dart # 商品註冊畫面
│   │   │   ├── search_screen.dart   # 即時辨識畫面
│   │   │   └── product_list_screen.dart # 商品列表
│   │   ├── services/
│   │   │   ├── mobileclip_service.dart  # TFLite 模型推論
│   │   │   ├── database_service.dart    # SQLite CRUD
│   │   │   ├── vector_service.dart      # 向量檢索與相似度計算
│   │   │   └── camera_service.dart      # 相機控制
│   │   ├── models/
│   │   │   ├── product_model.dart       # 商品資料模型
│   │   │   └── search_result_model.dart # 搜尋結果模型
│   │   ├── widgets/
│   │   │   ├── camera_preview_widget.dart # 相機預覽
│   │   │   ├── product_card.dart          # 商品卡片
│   │   │   └── search_overlay.dart        # 辨識結果疊加層
│   │   └── utils/
│   │       ├── image_utils.dart         # 圖片處理工具
│   │       └── vector_math.dart         # 向量計算 (cosine similarity)
│   └── test/
│       ├── services/
│       │   ├── mobileclip_service_test.dart
│       │   ├── database_service_test.dart
│       │   └── vector_service_test.dart
│       └── utils/
│           └── vector_math_test.dart
└── tests/                           # 整合測試
    ├── test_model_conversion.py     # 模型轉換驗證
    └── test_inference_accuracy.py   # 推論準確度測試
```

## Makefile 規範

### 必備目標
```makefile
.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make install         - 安裝所有依賴 (Python + Flutter)"
	@echo "  make download-model  - 下載 MobileCLIP-S2 PyTorch 模型"
	@echo "  make convert-model   - 轉換模型為 TFLite 格式"
	@echo "  make test-model      - 測試 TFLite 模型推論"
	@echo "  make build           - 建置 Flutter app (APK)"
	@echo "  make run             - 啟動 Flutter app (開發模式)"
	@echo "  make test            - 執行所有測試"
	@echo "  make clean           - 清理建置產物和臨時檔案"

.PHONY: install
install:  ## 安裝所有依賴
	@echo "安裝 Python 依賴 (模型轉換工具)..."
	pip install -r model_conversion/requirements.txt
	@echo "安裝 Flutter 依賴..."
	cd flutter_app && flutter pub get
	@echo "✅ 依賴安裝完成"

.PHONY: download-model
download-model:  ## 下載 MobileCLIP-S2 模型
	@mkdir -p ../ml-mobileclip/checkpoints
	@if [ ! -f ../ml-mobileclip/checkpoints/mobileclip_s2.pt ]; then \
		echo "下載 MobileCLIP-S2 PyTorch 模型..."; \
		wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s2.pt \
		     -P ../ml-mobileclip/checkpoints; \
		echo "✅ 模型下載完成"; \
	else \
		echo "✅ 模型已存在"; \
	fi

.PHONY: convert-model
convert-model: download-model  ## 轉換模型為 TFLite
	@echo "轉換 PyTorch 模型為 TFLite..."
	@mkdir -p flutter_app/assets/models
	cd model_conversion && python convert_to_tflite.py
	@echo "✅ 模型轉換完成: flutter_app/assets/models/mobileclip_s2.tflite"

.PHONY: test-model
test-model:  ## 測試 TFLite 模型
	@echo "測試 TFLite 模型推論..."
	cd model_conversion && python test_tflite_model.py
	@echo "✅ 模型測試通過"

.PHONY: build
build:  ## 建置 Flutter app
	@echo "建置 Android APK..."
	cd flutter_app && flutter build apk --release
	@echo "✅ APK 已生成: flutter_app/build/app/outputs/flutter-apk/app-release.apk"

.PHONY: run
run:  ## 啟動 Flutter app (開發模式)
	cd flutter_app && flutter run

.PHONY: test
test:  ## 執行所有測試
	@echo "執行 Python 測試..."
	cd tests && python -m pytest -v
	@echo "執行 Flutter 測試..."
	cd flutter_app && flutter test
	@echo "✅ 所有測試通過"

.PHONY: clean
clean:  ## 清理建置產物
	@echo "清理 Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "清理 Flutter build..."
	cd flutter_app && flutter clean
	@echo "清理測試產生的檔案..."
	rm -rf tests/*.log tests/tmp_* model_conversion/*.log
	@echo "✅ 清理完成"
```

## Build/Debug/Test 指令

### 初始化環境
```bash
# 1. 安裝依賴
make install

# 2. 下載並轉換模型
make download-model
make convert-model

# 3. 測試模型
make test-model
```

### 開發流程
```bash
# 啟動 Flutter app (連接手機或模擬器)
make run

# 或指定設備
flutter devices
cd flutter_app && flutter run -d <device-id>
```

### 測試流程
```bash
# 執行所有測試
make test

# 單獨測試 Flutter
cd flutter_app && flutter test

# 單獨測試模型轉換
cd tests && python -m pytest test_model_conversion.py -v
```

### 建置發布版本
```bash
# Android APK
make build

# iOS (需要 macOS + Xcode)
cd flutter_app && flutter build ios --release
```

## 驗收標準

### 功能需求
- [ ] 使用者可以拍攝商品照片並輸入資訊（名稱、描述、價格）
- [ ] 商品圖片和資料儲存在手機本地
- [ ] 使用者可以查看已註冊的所有商品
- [ ] 使用者可以開啟相機進行即時辨識
- [ ] 相機畫面即時顯示辨識結果（商品名稱、相似度、縮圖）
- [ ] 相似度高於閾值才顯示，否則顯示「未識別」
- [ ] 支援至少 100 個商品的快速檢索 (< 500ms)
- [ ] 完全離線運作，無需網路連線

### 效能需求
- [ ] 模型載入時間 < 2 秒（App 啟動時）
- [ ] 手機端推論時間 < 100ms (中階手機 CPU)
- [ ] 向量檢索時間 < 50ms (100 商品規模)
- [ ] 相機畫面更新流暢 (>= 15 FPS)
- [ ] App 啟動到可用 < 3 秒

### 測試覆蓋
- [ ] TFLite 模型推論測試（準確度驗證）
- [ ] SQLite CRUD 操作測試
- [ ] 向量相似度計算測試
- [ ] 圖片儲存與讀取測試
- [ ] Flutter Widget 測試（UI 元件）
- [ ] 整合測試（端到端流程）

## 子任務拆解

### Phase 1: 模型轉換與驗證 (最優先)
1. [ ] 建立 Python 環境與依賴
2. [ ] 實作 PyTorch → TFLite 轉換腳本
3. [ ] 驗證轉換後模型的準確度（與原始 PyTorch 比對）
4. [ ] 實作 TFLite 推論測試腳本
5. [ ] 撰寫轉換測試 (test_model_conversion.py)

### Phase 2: Flutter 基礎建設
6. [ ] 建立 Flutter 專案結構
7. [ ] 整合 TFLite 套件 (tflite_flutter)
8. [ ] 實作 MobileCLIPService (模型推論封裝)
9. [ ] 實作 DatabaseService (SQLite CRUD)
10. [ ] 實作 VectorService (相似度計算與檢索)
11. [ ] 撰寫 Service 層測試

### Phase 3: UI 與相機整合
12. [ ] 實作商品註冊畫面 (拍照 + 表單輸入)
13. [ ] 實作商品列表畫面 (瀏覽已註冊商品)
14. [ ] 實作即時辨識畫面 (相機預覽 + 結果疊加)
15. [ ] 整合相機服務 (camera package)
16. [ ] 實作圖片處理工具 (裁切、壓縮、轉換)
17. [ ] 撰寫 Widget 測試

### Phase 4: 整合與優化
18. [ ] 端到端整合測試
19. [ ] 效能優化（推論快取、向量檢索優化）
20. [ ] UI/UX 調整（載入動畫、錯誤處理、相機權限）
21. [ ] 建置發布版本與實機測試
22. [ ] 撰寫使用文件

## 資料庫 Schema

### products 表
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL,
    image_path TEXT NOT NULL,         -- 本地圖片路徑
    feature_vector BLOB NOT NULL,     -- 512維向量 (序列化為 bytes)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_name ON products(name);
```

### 向量儲存格式
```dart
// Dart List<double> → Float32List → Uint8List (BLOB)
List<double> vector = [0.123, 0.456, ...]; // 512 維
Float32List float32 = Float32List.fromList(vector);
Uint8List bytes = float32.buffer.asUint8List();
// 儲存到 SQLite BLOB 欄位
```

## Flutter 依賴套件

### pubspec.yaml
```yaml
dependencies:
  flutter:
    sdk: flutter

  # 模型推論
  tflite_flutter: ^0.10.0

  # 資料庫
  sqflite: ^2.3.0
  path_provider: ^2.1.0

  # 相機
  camera: ^0.10.5
  image_picker: ^1.0.0

  # 圖片處理
  image: ^4.1.0

  # UI
  permission_handler: ^11.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  mockito: ^5.4.0
```

## 技術細節

### 1. 模型轉換 (PyTorch → TFLite)
```python
import torch
import mobileclip
from ai_edge_torch import convert

# 載入 PyTorch 模型
model, _, preprocess = mobileclip.create_model_and_transforms(
    'mobileclip_s2',
    pretrained='../ml-mobileclip/checkpoints/mobileclip_s2.pt'
)
model.eval()

# 提取 image encoder (只需要視覺部分)
image_encoder = model.visual

# 轉換為 TFLite
sample_input = torch.randn(1, 3, 256, 256)
edge_model = convert(
    image_encoder,
    (sample_input,)
)
edge_model.export('flutter_app/assets/models/mobileclip_s2.tflite')
```

### 2. Flutter TFLite 推論
```dart
class MobileCLIPService {
  late Interpreter _interpreter;

  Future<void> loadModel() async {
    _interpreter = await Interpreter.fromAsset(
      'assets/models/mobileclip_s2.tflite'
    );
  }

  List<double> extractFeatures(Uint8List imageBytes) {
    // 預處理圖片 (resize to 256x256, normalize)
    final input = preprocessImage(imageBytes);

    // 推論
    var output = List.filled(1 * 512, 0.0).reshape([1, 512]);
    _interpreter.run(input, output);

    // L2 normalize
    final features = normalizeVector(output[0]);
    return features;
  }
}
```

### 3. 向量相似度計算
```dart
class VectorService {
  double cosineSimilarity(List<double> a, List<double> b) {
    double dotProduct = 0.0;
    for (int i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
    }
    // 假設向量已 normalized，則 ||a|| = ||b|| = 1
    return dotProduct;
  }

  Future<SearchResult?> findMostSimilar(
    List<double> queryVector,
    double threshold
  ) async {
    final products = await databaseService.getAllProducts();

    double maxSimilarity = threshold;
    Product? bestMatch;

    for (var product in products) {
      final similarity = cosineSimilarity(
        queryVector,
        product.featureVector
      );

      if (similarity > maxSimilarity) {
        maxSimilarity = similarity;
        bestMatch = product;
      }
    }

    return bestMatch != null
      ? SearchResult(product: bestMatch, similarity: maxSimilarity)
      : null;
  }
}
```

### 4. 即時相機辨識
```dart
class SearchScreen extends StatefulWidget {
  @override
  _SearchScreenState createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  late CameraController _cameraController;
  Timer? _processingTimer;
  SearchResult? _currentResult;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
    _startProcessing();
  }

  void _startProcessing() {
    _processingTimer = Timer.periodic(
      Duration(milliseconds: 500),
      (timer) async {
        if (_isProcessing) return;

        _isProcessing = true;
        try {
          // 抓取當前幀
          final image = await _cameraController.takePicture();
          final bytes = await image.readAsBytes();

          // 推論
          final features = await mobileCLIPService.extractFeatures(bytes);

          // 檢索
          final result = await vectorService.findMostSimilar(
            features,
            0.7  // 閾值
          );

          setState(() => _currentResult = result);
        } finally {
          _isProcessing = false;
        }
      }
    );
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        CameraPreview(_cameraController),
        if (_currentResult != null)
          SearchOverlay(result: _currentResult!),
      ],
    );
  }
}
```

## 風險與限制

### 技術風險
1. **模型轉換挑戰**: PyTorch → TFLite 可能遇到算子不支援問題
   - **應對**: 使用 ONNX 作為中介格式，或改用 ONNX Runtime Mobile

2. **手機端效能**: 中低階手機推論可能較慢
   - **應對**: 降低處理頻率（1秒處理一次）、使用量化模型（INT8）

3. **記憶體限制**: 大量商品向量可能佔用過多記憶體
   - **應對**: 限制商品數量上限（如 500 個）、使用分頁載入

### 已知限制
1. **商品數量**: 建議 < 500 個（純 Dart 向量檢索的實際限制）
2. **推論延遲**: 中階手機約 50-150ms，低階可能 > 200ms
3. **相機權限**: 需要使用者授權相機與儲存權限
4. **離線限制**: 無法同步到雲端，換手機需重新註冊

### 擴展性考量
- 若商品數量 > 1000，考慮使用 FAISS 的 C++ 編譯版本透過 FFI 調用
- 若需要雲端同步，可增加選配的 Firebase 備份功能

## 技術參考
- [MobileCLIP GitHub](https://github.com/apple/ml-mobileclip)
- [TFLite Flutter Plugin](https://pub.dev/packages/tflite_flutter)
- [ONNX Runtime Flutter](https://pub.dev/packages/onnxruntime)
- [Flutter Camera Plugin](https://pub.dev/packages/camera)
- [SQLite Flutter (sqflite)](https://pub.dev/packages/sqflite)

## 開發注意事項
1. **TDD 原則**: 所有核心邏輯（向量計算、模型推論）必須先寫測試
2. **測試檔案位置**: 統一放在 `tests/` 和 `flutter_app/test/` 目錄
3. **臨時檔案清理**: 測試結束後刪除 `tests/tmp_*` 等檔案
4. **Plan 更新**: 發現需求變更時提出討論，不自行修改 plan.md
5. **分段執行**: 一次完成一個子任務，停下來總結與確認
6. **模型驗證**: 轉換後的 TFLite 模型必須與原始 PyTorch 模型輸出進行比對

---

**建立日期**: 2025-11-01
**最後更新**: 2025-11-01
**版本**: v2.0 (離線版)
