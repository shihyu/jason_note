# MobileCLIP 以圖找圖測試專案

## 專案簡介

本專案使用 MobileCLIP 模型測試以圖找圖功能，並驗證在不同圖像變化下的辨識準確度。

## 測試項目

### 圖像變化測試
- **旋轉**: 15°, 30°, 45°, 90°
- **亮度調整**: ±30%, ±50%
- **模糊效果**: Gaussian blur (kernel 3, 5, 7)
- **裁切**: 中心裁切 70%, 80%, 90%
- **縮放**: 50%, 75%, 125%, 150%
- **組合變化**: 旋轉 + 亮度 + 縮放

### 模型比較
- **MobileCLIP-S0**: 最快
- **MobileCLIP-S1**: 平衡
- **MobileCLIP-S2**: 最準確

## 快速開始

### 1. 安裝依賴
```bash
make setup
```

### 2. 安裝 MobileCLIP
```bash
make install-mc
```

### 3. 下載測試圖片
```bash
make download
```

### 4. 執行測試
```bash
make test
```

### 5. 執行以圖找圖
```bash
make run
```

### 6. 清理
```bash
make clean
```

## 專案結構

```
mobileclip_test/
├── src/
│   ├── image_search.py        # 圖像搜尋核心功能
│   ├── image_augmentation.py  # 圖像增強
│   ├── download_images.py     # 下載測試圖片
│   └── utils.py               # 工具函數
├── tests/
│   ├── test_image_search.py   # 測試以圖找圖
│   ├── test_augmentation.py   # 測試圖像增強
│   └── fixtures/              # 測試資料
│       ├── database/          # 圖片資料庫 (20張)
│       └── queries/           # 查詢圖片 (變化版本)
├── results/
│   ├── logs/                  # 執行日誌
│   └── reports/               # 測試報告
├── requirements.txt           # Python 依賴
├── Makefile                   # 建置指令
└── README.md                  # 專案說明
```

## 測試資料

### 圖片資料庫 (20張)
- 人物: 5 張
- 動物: 5 張
- 風景: 5 張
- 物品: 5 張

## 驗收標準

### 準確度 (S1 模型)
- 原始圖片: > 95%
- 小角度旋轉 (±15°): > 90%
- 中等角度旋轉 (±30°): > 80%
- 亮度變化 (±30%): > 85%
- 模糊效果 (kernel 3): > 80%
- 裁切 (80%): > 85%
- 縮放 (75%-125%): > 90%
- 組合變化: > 70%

### 效能 (CPU)
- S0 單張特徵提取: < 50ms
- S1 單張特徵提取: < 100ms
- S2 單張特徵提取: < 150ms

## 輸出報告

測試完成後會在 `results/reports/` 產生:
- 準確度統計報告
- 模型比較報告
- 效能分析圖表

## 技術細節

### 使用的模型
- MobileCLIP-S0 (~10MB)
- MobileCLIP-S1 (~20MB)
- MobileCLIP-S2 (~40MB)

### 相似度計算
- 使用 Cosine Similarity
- 閾值: 0.85

## 參考資源

- [MobileCLIP GitHub](https://github.com/apple/ml-mobileclip)
- [MobileCLIP Paper](https://arxiv.org/abs/2311.17049)
