.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make install         - 安裝所有依賴 (Python + Flutter)"
	@echo "  make download-model  - 下載 MobileCLIP-S2 PyTorch 模型"
	@echo "  make convert-model   - 轉換模型為 ONNX 格式"
	@echo "  make verify-model    - 驗證 ONNX 模型準確度"
	@echo "  make test            - 執行所有測試"
	@echo "  make build           - 建置 Flutter app (APK)"
	@echo "  make run             - 啟動 Flutter app (開發模式)"
	@echo "  make clean           - 清理建置產物和臨時檔案 (保留模型)"
	@echo "  make clean-all       - 清理所有檔案 (包含模型)"

.PHONY: install
install:  ## 安裝所有依賴
	@echo "安裝 Python 依賴 (模型轉換工具)..."
	pip install -r model_conversion/requirements.txt
	@echo "✅ Python 依賴安裝完成"
	@echo ""
	@echo "檢查 Flutter 是否安裝..."
	@if command -v flutter >/dev/null 2>&1; then \
		echo "Flutter 已安裝，版本:"; \
		flutter --version | head -1; \
		cd flutter_app && flutter pub get; \
		echo "✅ Flutter 依賴安裝完成"; \
	else \
		echo "⚠️  Flutter 未安裝，請先安裝 Flutter SDK"; \
		echo "   參考: https://flutter.dev/docs/get-started/install"; \
	fi

.PHONY: download-model
download-model:  ## 下載 MobileCLIP-S2 模型
	@mkdir -p ml-mobileclip/checkpoints
	@if [ ! -f ml-mobileclip/checkpoints/mobileclip_s2.pt ]; then \
		echo "下載 MobileCLIP-S2 PyTorch 模型..."; \
		wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s2.pt \
		     -P ml-mobileclip/checkpoints; \
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

.PHONY: verify-model
verify-model:  ## 驗證 ONNX 模型
	@echo "驗證 ONNX 模型準確度..."
	cd model_conversion && python verify_model_accuracy.py
	@echo "✅ 模型驗證完成"

.PHONY: test
test:  ## 執行所有測試
	@echo "執行模型轉換測試..."
	cd tests && python -m pytest test_model_conversion.py -v
	@echo ""
	@if [ -d flutter_app ]; then \
		echo "執行 Flutter 測試..."; \
		cd flutter_app && flutter test; \
	else \
		echo "⚠️  Flutter app 尚未建立"; \
	fi
	@echo "✅ 所有測試完成"

.PHONY: build
build:  ## 建置 Flutter app
	@if [ ! -d flutter_app ]; then \
		echo "❌ Flutter app 目錄不存在"; \
		echo "   請先完成 Phase 2: Flutter 基礎建設"; \
		exit 1; \
	fi
	@if [ ! -f flutter_app/assets/models/mobileclip_s2.onnx ]; then \
		echo "⚠️  模型檔案不存在,嘗試下載和轉換..."; \
		if $(MAKE) download-model && $(MAKE) convert-model; then \
			echo "✅ 模型下載和轉換成功"; \
		else \
			echo "⚠️  模型下載/轉換失敗,建立 placeholder..."; \
			mkdir -p flutter_app/assets/models; \
			touch flutter_app/assets/models/mobileclip_s2.onnx; \
			echo "   注意:這是空檔案,App 無法正常運作"; \
			echo "   請執行 'make install' 安裝依賴後再執行 'make convert-model'"; \
		fi; \
	fi
	@echo "建置 Android APK..."
	cd flutter_app && flutter build apk --release
	@echo "✅ APK 已生成: flutter_app/build/app/outputs/flutter-apk/app-release.apk"

.PHONY: run
run:  ## 啟動 Flutter app (開發模式)
	@if [ ! -d flutter_app ]; then \
		echo "❌ Flutter app 目錄不存在"; \
		echo "   請先完成 Phase 2: Flutter 基礎建設"; \
		exit 1; \
	fi
	cd flutter_app && flutter run

.PHONY: clean
clean:  ## 清理建置產物 (保留模型檔案)
	@echo "清理 Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "清理 Flutter build..."
	if [ -d flutter_app ]; then cd flutter_app && flutter clean; fi
	@echo "清理測試和 log 檔案..."
	rm -rf tests/*.log tests/tmp_* model_conversion/*.log
	find flutter_app -maxdepth 1 -name "*.log" -delete 2>/dev/null || true
	@echo "清理備份檔案..."
	find . -name "*.bak" -delete 2>/dev/null || true
	@echo "✅ 清理完成 (模型檔案已保留)"

.PHONY: clean-all
clean-all: clean  ## 清理所有檔案 (包含模型)
	@echo "清理模型檔案..."
	rm -f flutter_app/assets/models/mobileclip_s2.onnx
	@echo "✅ 完全清理完成"
