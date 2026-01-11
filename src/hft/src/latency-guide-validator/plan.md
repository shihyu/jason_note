# 低延遲技術指南驗證專案

## 任務目標

編寫 C++ 程式驗證《低延遲技術最佳實踐指南.md》中的技術細節是否正確,並根據驗證結果修正文件內容。

## 專案結構組織

```
latency-guide-validator/
├── plan.md                 # 本檔案
├── Makefile               # 建置與測試腳本
├── src/                   # 實作程式碼
│   ├── rdtsc_test.cpp            # RDTSC 測量驗證
│   ├── lockfree_queue_test.cpp   # Lock-Free Queue 驗證
│   ├── memory_pool_test.cpp      # Memory Pool 驗證
│   ├── cache_alignment_test.cpp  # Cache Line Alignment 驗證
│   └── branch_prediction_test.cpp # 分支預測驗證
├── tests/                 # 測試檔案
│   └── validation_report.md      # 驗證報告
└── README.md              # 專案說明
```

## 驗證範圍

### 1. 延遲測量 (rdtsc_test.cpp)
- ✅ RDTSC 指令語法正確性
- ✅ CPU 週期轉換為奈秒的計算公式
- ✅ 測量的實際精度

### 2. Lock-Free Queue (lockfree_queue_test.cpp)
- ✅ SPSC Queue 實作正確性
- ✅ 宣稱的延遲數字 (< 50ns)
- ✅ Cache False Sharing 的影響
- ✅ alignas(64) 的效果

### 3. Memory Pool (memory_pool_test.cpp)
- ✅ Placement New 語法正確性
- ✅ 分配延遲數字 (< 20ns vs malloc 50-10000ns)
- ✅ O(1) 時間複雜度

### 4. Cache Alignment (cache_alignment_test.cpp)
- ✅ alignas(64) 對齊效果
- ✅ False Sharing 的效能影響
- ✅ Cache Line 大小假設 (64 bytes)

### 5. 分支預測 (branch_prediction_test.cpp)
- ✅ __builtin_expect 語法
- ✅ LIKELY/UNLIKELY 的效能影響
- ✅ 分支預測失敗的懲罰週期數

## Makefile 規範

### 必備目標

```makefile
.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 編譯所有測試程式"
	@echo "  make run     - 執行所有驗證測試"
	@echo "  make test    - 執行測試並生成報告"
	@echo "  make clean   - 清理建置產物"
	@echo ""
	@echo "單獨執行："
	@echo "  make rdtsc"
	@echo "  make lockfree"
	@echo "  make mempool"
	@echo "  make cache"
	@echo "  make branch"

.PHONY: build
build:  ## 編譯所有測試程式
	g++ -O3 -march=native -std=c++17 -pthread src/rdtsc_test.cpp -o bin/rdtsc_test
	g++ -O3 -march=native -std=c++17 -pthread src/lockfree_queue_test.cpp -o bin/lockfree_test
	g++ -O3 -march=native -std=c++17 -pthread src/memory_pool_test.cpp -o bin/mempool_test
	g++ -O3 -march=native -std=c++17 -pthread src/cache_alignment_test.cpp -o bin/cache_test
	g++ -O3 -march=native -std=c++17 -pthread src/branch_prediction_test.cpp -o bin/branch_test

.PHONY: run
run: build  ## 執行所有驗證測試
	@echo "=== RDTSC 測量驗證 ==="
	./bin/rdtsc_test
	@echo ""
	@echo "=== Lock-Free Queue 驗證 ==="
	./bin/lockfree_test
	@echo ""
	@echo "=== Memory Pool 驗證 ==="
	./bin/mempool_test
	@echo ""
	@echo "=== Cache Alignment 驗證 ==="
	./bin/cache_test
	@echo ""
	@echo "=== Branch Prediction 驗證 ==="
	./bin/branch_test

.PHONY: test
test: run  ## 執行測試並生成報告
	@echo ""
	@echo "生成驗證報告到 tests/validation_report.md"

.PHONY: clean
clean:  ## 清理建置產物
	rm -rf bin/
	rm -f tests/*.tmp
```

## Build/Debug/Test 指令

```bash
# 編譯
make build

# 執行所有驗證
make run

# 生成驗證報告
make test

# 清理
make clean

# 單獨執行某個測試
./bin/rdtsc_test
./bin/lockfree_test
```

## 驗收標準

### 1. 程式碼品質
- [x] 所有測試程式成功編譯
- [x] 無記憶體洩漏 (使用 valgrind 檢查)
- [x] 符合 C++17 標準

### 2. 驗證結果
- [x] 每個測試輸出清晰的 PASS/FAIL 判斷
- [x] 提供實測數據與文件宣稱的比較
- [x] 生成詳細的驗證報告 (tests/validation_report.md)

### 3. 文件修正
- [x] 根據驗證結果修正原始指南中的錯誤
- [x] 標記不可驗證的宣稱 (需要特定硬體等)
- [x] 補充實測數據

## 子任務拆解

1. **環境準備**
   - 建立專案目錄結構
   - 編寫 Makefile

2. **RDTSC 測量驗證**
   - 實作 rdtsc_test.cpp
   - 驗證 RDTSC 語法
   - 測試週期轉換公式
   - 測量實際精度

3. **Lock-Free Queue 驗證**
   - 實作完整的 SPSC Queue
   - 測試 enqueue/dequeue 延遲
   - 驗證 False Sharing 影響
   - 測試 alignas(64) 效果

4. **Memory Pool 驗證**
   - 實作 Memory Pool
   - 比較 allocate() vs malloc() 延遲
   - 驗證 Placement New 語法
   - 測試碎片化問題

5. **Cache Alignment 驗證**
   - 實作多執行緒計數器
   - 測試有/無 alignas 的效能差異
   - 驗證 Cache Line 大小

6. **分支預測驗證**
   - 實作 LIKELY/UNLIKELY 測試
   - 測量分支預測成功/失敗的週期數
   - 驗證 90% 機率的建議

7. **生成驗證報告**
   - 彙整所有測試結果
   - 對照原始文件的宣稱
   - 提出修正建議

8. **修正原始指南**
   - 根據驗證報告修正 低延遲技術最佳實踐指南.md
   - 更新不正確的數字
   - 補充實測數據

## 注意事項

### 測試環境
- 需要 x86_64 架構 (RDTSC 指令)
- 需要 Linux 環境 (pthread, CPU affinity)
- 需要 root 權限測試部分硬體調優項目 (NUMA, CPU isolation)

### 不可驗證項目
由於環境限制,以下項目僅檢查語法正確性,不做效能驗證:
- DPDK (需要特定網卡)
- Huge Pages (需要 root 權限)
- NUMA 配置 (需要多 socket 系統)
- 網卡調優 (需要實體網卡)

### TDD 流程
1. 先寫測試框架 (main + 驗證邏輯)
2. 實作被測試的資料結構
3. 執行測試,記錄結果
4. 不修改測試,直接回報結果

## 預期產出

1. **src/ 目錄**: 5 個測試程式
2. **bin/ 目錄**: 編譯後的執行檔
3. **tests/validation_report.md**: 詳細驗證報告
4. **修正後的指南**: ../低延遲技術最佳實踐指南.md
