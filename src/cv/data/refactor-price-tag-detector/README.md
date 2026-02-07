# 價格標籤檢測系統（重構版）

基於 YOLO + 顏色過濾 + OCR 的價格標籤檢測系統，從原始專案重構而來。

## 重構成果

- **原始專案**: ~29GB → **重構專案**: 1.1GB
- **空間節省**: 96%
- **準確度**: 98.4%（與原始專案一致）

## 快速開始

```bash
# 安裝依賴
make build

# 執行所有測試
make test

# 執行準確度驗證
make accuracy

# 檢測價格標籤
make detect
```

## 文件

- 📖 **完整文件**: [docs/README.md](docs/README.md)
- 📊 **最終報告**: [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md)
- 📝 **重構記錄**: [docs/refactor-docs/](docs/refactor-docs/)
- 📋 **重構計畫**: [plan.md](plan.md)

## 專案結構

```
refactor-price-tag-detector/
├── src/           # 核心程式碼（4 個模組）
├── cli/           # 命令列工具
├── tests/         # 測試檔案（14 個測試）
├── scripts/       # 驗證腳本
├── data/          # 資料目錄（1.1GB）
└── docs/          # 文件
```

## 準確度

| 影片 | 準確度 |
|------|--------|
| Video1 | 100.0% |
| Video2 | 96.9% |
| Video3 | 98.2% |
| **平均** | **98.4%** |

## 核心特性

- ✅ YOLO 物體檢測（mAP50: 98.01%）
- ✅ 雙色區域分離（黃色/綠色）
- ✅ 改進版 Tesseract OCR（98.4% 準確度）
- ✅ 完整測試覆蓋（14 個測試）

## 授權

MIT License
