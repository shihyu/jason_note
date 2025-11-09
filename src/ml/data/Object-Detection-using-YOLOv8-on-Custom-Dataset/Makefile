# YOLOv8 Guitar Detection Makefile

.DEFAULT_GOAL := help
.PHONY: help setup train validate inference visualize test test-comprehensive clean clean-all check-dataset

# Python interpreter
PYTHON := python3

# Directories
DATASET_DIR := Dataset/Guitar_dataset
TRAIN_DIR := runs/detect/guitar_train
TESTS_DIR := tests
INFERENCE_DIR := $(TESTS_DIR)/inference_results

# Files
REQUIREMENTS := requirements.txt
DATASET_YAML := guitar_dataset.yaml
TRAIN_SCRIPT := train.py
VALIDATE_SCRIPT := validate.py
INFERENCE_SCRIPT := inference.py
VISUALIZE_SCRIPT := visualize_comparison.py
COMPREHENSIVE_TEST := comprehensive_test.py
BASELINE_METRICS := $(TESTS_DIR)/baseline_metrics.json
MODEL_WEIGHTS := $(TRAIN_DIR)/weights/best.pt
REPORT_FILE := $(TESTS_DIR)/comparison_report.html
VALIDATION_REPORT := $(TESTS_DIR)/validation_report.json

help:  ## 顯示此說明訊息
	@echo "YOLOv8 Guitar Detection - 可用指令:"
	@echo ""
	@echo "  make setup      - 安裝依賴套件並檢查環境"
	@echo "  make train      - 訓練 YOLOv8 模型 (300 epochs)"
	@echo "  make validate   - 驗證模型並比對基準指標"
	@echo "  make inference  - 在驗證集上執行推論測試"
	@echo "  make visualize  - 生成視覺化比對報告 (HTML)"
	@echo "  make test       - 驗證資料集完整性"
	@echo "  make test-comprehensive - 綜合測試：驗證模型效果與基準一致性"
	@echo "  make clean      - 清理訓練產物和臨時檔案"
	@echo "  make clean-all  - 完全清理 (包含下載的模型)"
	@echo ""
	@echo "完整流程範例:"
	@echo "  make setup && make train && make validate && make inference && make visualize"
	@echo ""
	@echo "重新訓練:"
	@echo "  make clean && make train"
	@echo ""

setup:  ## 安裝依賴並檢查環境
	@echo "========================================="
	@echo "環境設定與依賴安裝"
	@echo "========================================="
	@echo "檢查 Python 版本..."
	@$(PYTHON) --version
	@echo ""
	@echo "安裝 Python 依賴套件..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r $(REQUIREMENTS)
	@echo ""
	@echo "驗證資料集..."
	@$(MAKE) check-dataset
	@echo ""
	@echo "========================================="
	@echo "✓ 環境設定完成!"
	@echo "========================================="

check-dataset:  ## 檢查資料集完整性
	@echo "檢查資料集結構..."
	@test -d $(DATASET_DIR) || (echo "✗ 錯誤: 找不到資料集目錄 $(DATASET_DIR)" && exit 1)
	@test -d $(DATASET_DIR)/train/images || (echo "✗ 錯誤: 找不到訓練圖片目錄" && exit 1)
	@test -d $(DATASET_DIR)/train/labels || (echo "✗ 錯誤: 找不到訓練標註目錄" && exit 1)
	@test -d $(DATASET_DIR)/val/images || (echo "✗ 錯誤: 找不到驗證圖片目錄" && exit 1)
	@test -d $(DATASET_DIR)/val/labels || (echo "✗ 錯誤: 找不到驗證標註目錄" && exit 1)
	@echo "✓ 資料集結構完整"
	@echo ""
	@echo "統計資料集檔案數量..."
	@echo "  訓練圖片: $$(find $(DATASET_DIR)/train/images -name '*.jpg' -o -name '*.JPG' | wc -l)"
	@echo "  訓練標註: $$(find $(DATASET_DIR)/train/labels -name '*.txt' | wc -l)"
	@echo "  驗證圖片: $$(find $(DATASET_DIR)/val/images -name '*.jpg' -o -name '*.JPG' | wc -l)"
	@echo "  驗證標註: $$(find $(DATASET_DIR)/val/labels -name '*.txt' | wc -l)"

train:  ## 執行訓練流程
	@echo "========================================="
	@echo "開始訓練 YOLOv8 模型"
	@echo "========================================="
	@test -f $(DATASET_YAML) || (echo "✗ 錯誤: 找不到資料集配置檔 $(DATASET_YAML)" && exit 1)
	@$(PYTHON) $(TRAIN_SCRIPT)
	@echo ""
	@if [ -f $(MODEL_WEIGHTS) ]; then \
		echo "✓ 訓練完成! 模型權重已儲存至: $(MODEL_WEIGHTS)"; \
	else \
		echo "✗ 訓練失敗: 找不到模型權重檔案"; \
		exit 1; \
	fi

validate:  ## 驗證模型並比對指標
	@echo "========================================="
	@echo "驗證訓練模型"
	@echo "========================================="
	@test -f $(MODEL_WEIGHTS) || (echo "✗ 錯誤: 找不到訓練模型 $(MODEL_WEIGHTS)" && echo "請先執行: make train" && exit 1)
	@$(PYTHON) $(VALIDATE_SCRIPT)

inference:  ## 執行推論測試
	@echo "========================================="
	@echo "執行推論測試"
	@echo "========================================="
	@test -f $(MODEL_WEIGHTS) || (echo "✗ 錯誤: 找不到訓練模型 $(MODEL_WEIGHTS)" && echo "請先執行: make train" && exit 1)
	@$(PYTHON) $(INFERENCE_SCRIPT)
	@echo ""
	@if [ -d $(INFERENCE_DIR) ]; then \
		echo "✓ 推論完成! 結果已儲存至: $(INFERENCE_DIR)"; \
	else \
		echo "✗ 推論失敗: 找不到輸出目錄"; \
		exit 1; \
	fi

visualize:  ## 生成視覺化比對報告
	@echo "========================================="
	@echo "生成視覺化比對報告"
	@echo "========================================="
	@$(PYTHON) $(VISUALIZE_SCRIPT)
	@echo ""
	@if [ -f $(REPORT_FILE) ]; then \
		echo "✓ 報告已生成: $(REPORT_FILE)"; \
		echo ""; \
		echo "開啟報告:"; \
		echo "  xdg-open $(REPORT_FILE)"; \
	else \
		echo "✗ 報告生成失敗"; \
		exit 1; \
	fi

test:  ## 執行測試 (資料集完整性驗證)
	@echo "========================================="
	@echo "執行測試"
	@echo "========================================="
	@$(MAKE) check-dataset
	@echo ""
	@echo "✓ 所有測試通過!"

test-comprehensive:  ## 綜合測試：驗證模型效果與基準一致性
	@echo "========================================="
	@echo "綜合測試：模型驗證與比對"
	@echo "========================================="
	@test -f $(MODEL_WEIGHTS) || (echo "✗ 錯誤: 找不到訓練模型 $(MODEL_WEIGHTS)" && echo "請先執行: make train" && exit 1)
	@$(PYTHON) $(COMPREHENSIVE_TEST)
	@echo ""
	@if [ -f $(VALIDATION_REPORT) ]; then \
		echo "✓ 驗證報告已生成: $(VALIDATION_REPORT)"; \
	fi

clean:  ## 清理訓練產物和臨時檔案
	@echo "清理訓練產物和臨時檔案..."
	@rm -rf runs/detect/guitar_train
	@rm -rf $(TESTS_DIR)/inference_results
	@rm -rf $(TESTS_DIR)/current_metrics.json
	@rm -rf $(TESTS_DIR)/comparison_report.html
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ 清理完成 (保留基準指標和程式碼)"

clean-all: clean  ## 完全清理 (包含基準指標和下載的模型)
	@echo "完全清理 (包含基準指標)..."
	@rm -rf runs/
	@rm -rf $(TESTS_DIR)
	@rm -f yolov8n.pt
	@echo "✓ 完全清理完成"

# 完整流程快捷指令
all: setup train validate inference visualize  ## 執行完整流程
	@echo ""
	@echo "========================================="
	@echo "✓ 完整流程執行完成!"
	@echo "========================================="
	@echo "查看報告: xdg-open $(REPORT_FILE)"
