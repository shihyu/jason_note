.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "sherpa_onnx 工具 - 可用目標："
	@echo ""
	@echo "  make test-simple      - 測試基本 TTS 範例"
	@echo "  make test-cn          - 測試中文 TTS 工具"
	@echo "  make test-en          - 測試英文 TTS 工具"
	@echo "  make test-validation  - 執行完整驗證測試"
	@echo "  make test-all         - 執行所有測試"
	@echo "  make clean            - 清理產生的檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make test-cn          # 測試中文語音合成"
	@echo "  make test-all         # 執行所有測試"
	@echo "  make clean            # 清理測試檔案"

.PHONY: test-simple
test-simple:  ## 測試基本 TTS 範例
	@echo "正在測試基本 TTS 範例..."
	@cd ../.. && python src/sherpa_onnx/simple_tts_example.py
	@echo "✓ 基本 TTS 測試完成"

.PHONY: test-cn
test-cn:  ## 測試中文 TTS 工具
	@echo "正在測試中文 TTS 工具..."
	@cd ../.. && python src/sherpa_onnx/text_to_speech_cn.py \
		-t "本來應該從從容容遊刃有餘，現在是匆匆忙忙連滾帶爬" \
		-o test_cn_output.wav
	@echo "✓ 中文 TTS 測試完成"

.PHONY: test-en
test-en:  ## 測試英文 TTS 工具
	@echo "正在測試英文 TTS 工具..."
	@cd ../.. && python src/sherpa_onnx/text_to_speech.py \
		-t "Hello, this is a test of the English text to speech system." \
		-o test_en_output.wav
	@echo "✓ 英文 TTS 測試完成"

.PHONY: test-validation
test-validation:  ## 執行完整驗證測試
	@echo "正在執行完整驗證測試..."
	@cd ../.. && python src/sherpa_onnx/test_tts_validation.py
	@echo "✓ 完整驗證測試完成"

.PHONY: test-all
test-all: test-simple test-cn test-en test-validation  ## 執行所有測試
	@echo ""
	@echo "═══════════════════════════════════════"
	@echo "✓ 所有測試完成！"
	@echo "═══════════════════════════════════════"

.PHONY: clean
clean:  ## 清理產生的檔案
	@echo "正在清理產生的檔案..."
	@cd ../.. && rm -f test_cn_output.wav test_en_output.wav
	@cd ../.. && rm -f hello.wav welcome.wav output.wav
	@cd ../.. && rm -rf src/sherpa_onnx/__pycache__
	@echo "✓ 清理完成"
