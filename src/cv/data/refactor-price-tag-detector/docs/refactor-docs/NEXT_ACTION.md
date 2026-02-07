# 下一步行動方案

**時間**: 2026-02-07 22:55
**當前狀態**: 子任務 8 等待完整驗證

---

## 🎯 建議的執行方案（方案 C + A）

### 第一步：在背景啟動完整驗證

```bash
cd /home/shihyu/refactor-price-tag-detector

# 使用 nohup 在背景執行（推薦）
nohup uv run python scripts/verify_accuracy.py > accuracy_full_report.txt 2>&1 &

# 記錄 PID
echo $! > accuracy_verify.pid

# 查看進度（隨時可以執行）
tail -f accuracy_full_report.txt

# 或查看最後 20 行
tail -20 accuracy_full_report.txt
```

**預估時間**: 30-40 分鐘

---

### 第二步：同時繼續子任務 9-12（不等待驗證完成）

#### 子任務 9：執行核心測試

```bash
# 執行所有核心測試（不包括 test_accuracy.py）
uv run pytest tests/test_detector.py tests/test_color_filter.py tests/test_ocr_engine.py -v

# 如果測試失敗，修正後重新執行
```

**驗收標準**：
- [ ] 所有核心測試通過
- [ ] 無錯誤或警告

---

#### 子任務 10：完善 README.md

目前的 `README.md` 已經有基礎框架，需要：
1. 填入實際的準確度數據（待完整驗證完成後更新）
2. 確認安裝步驟正確
3. 確認使用範例正確

**驗收標準**：
- [ ] README.md 內容完整
- [ ] 使用說明清晰
- [ ] 準確度數據已填入（暫時使用原始專案的數據）

---

#### 子任務 11：清理和驗證

```bash
# 清理臨時檔案
make clean

# 檢查專案大小
du -sh .
du -sh data/

# 驗證專案結構
tree -L 2 -I '.venv|__pycache__|.pytest_cache'

# 最終測試
make build
make test
```

**驗收標準**：
- [ ] 專案大小 ≤ 1.5GB
- [ ] 無臨時檔案殘留
- [ ] 專案結構清晰

---

#### 子任務 12：文件和交接

1. 檢查 `plan.md` 是否需要更新
2. 確認所有驗收標準
3. 等待背景驗證完成
4. 生成最終測試報告

**驗收標準**：
- [ ] 所有驗收標準達成
- [ ] 完整驗證通過（≥ 98.4%）
- [ ] 文件完整

---

### 第三步：檢查背景驗證結果

```bash
# 檢查驗證是否完成
ps aux | grep verify_accuracy

# 查看最終結果
tail -100 accuracy_full_report.txt

# 或查看完整報告
cat accuracy_full_report.txt
```

**預期結果**：
- Video1: ≥ 100.0%
- Video2: ≥ 96.9%
- Video3: ≥ 98.2%
- 總體: ≥ 98.4%

---

## 📋 快速執行腳本

複製以下腳本到終端機執行：

```bash
#!/bin/bash
cd /home/shihyu/refactor-price-tag-detector

echo "=== 步驟 1: 啟動背景驗證 ==="
nohup uv run python scripts/verify_accuracy.py > accuracy_full_report.txt 2>&1 &
VERIFY_PID=$!
echo $VERIFY_PID > accuracy_verify.pid
echo "✓ 背景驗證已啟動 (PID: $VERIFY_PID)"
echo ""

sleep 5

echo "=== 步驟 2: 執行核心測試 ==="
uv run pytest tests/test_detector.py tests/test_color_filter.py tests/test_ocr_engine.py -v
if [ $? -eq 0 ]; then
    echo "✓ 核心測試通過"
else
    echo "✗ 核心測試失敗，請檢查"
    exit 1
fi
echo ""

echo "=== 步驟 3: 清理專案 ==="
make clean
echo "✓ 清理完成"
echo ""

echo "=== 步驟 4: 檢查專案大小 ==="
echo "專案總大小:"
du -sh .
echo ""
echo "資料目錄大小:"
du -sh data/
echo ""

echo "=== 步驟 5: 檢查背景驗證進度 ==="
if ps -p $VERIFY_PID > /dev/null; then
    echo "⏳ 驗證仍在進行中..."
    echo "查看進度: tail -f accuracy_full_report.txt"
else
    echo "✓ 驗證已完成"
    echo ""
    echo "=== 驗證結果 ==="
    tail -50 accuracy_full_report.txt
fi
```

---

## ⚠️ 注意事項

1. **不要中斷背景驗證**：讓它在背景完整執行
2. **可以同時進行其他子任務**：不需要等待驗證完成
3. **最終交付前確認驗證結果**：確保準確度達標

---

## 🎉 完成後的檢查清單

- [ ] 背景驗證完成且結果達標（≥ 98.4%）
- [ ] 所有核心測試通過
- [ ] README.md 完善
- [ ] 專案已清理，大小 ≤ 1.5GB
- [ ] 所有文件完整
- [ ] 專案可以直接使用

---

**最後更新**: 2026-02-07 22:55
