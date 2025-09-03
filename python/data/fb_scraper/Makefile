# Facebook 爬蟲 Makefile
# 使用方法: make <target>

# 變數設定
PYTHON = python3
PIP = pip3
VENV_DIR = venv
SCRIPT = fb_scraper.py
REQUIREMENTS = requirements.txt

# 預設目標
.DEFAULT_GOAL := help

# 顯示幫助訊息
help:
	@echo "Facebook 爬蟲 Makefile 使用說明"
	@echo "================================="
	@echo "make setup     - 完整環境設置（建議首次使用）"
	@echo "make venv      - 建立虛擬環境"
	@echo "make install   - 安裝套件依賴"
	@echo "make run       - 執行爬蟲程式"
	@echo "make clean     - 清理輸出檔案"
	@echo "make reset     - 重置環境（刪除虛擬環境）"
	@echo "make check     - 檢查環境狀態"
	@echo "make help      - 顯示此幫助訊息"

# 完整環境設置
setup: venv install
	@echo "✅ 環境設置完成！"
	@echo "🚀 執行 'make run' 開始爬取資料"

# 建立虛擬環境
venv:
	@echo "🔧 建立虛擬環境..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "✅ 虛擬環境建立完成"

# 安裝套件依賴
install: $(REQUIREMENTS)
	@echo "📦 安裝套件依賴..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r $(REQUIREMENTS); \
	else \
		echo "❌ 虛擬環境不存在，請先執行 'make venv'"; \
		exit 1; \
	fi
	@echo "✅ 套件安裝完成"

# 執行爬蟲程式
run: $(SCRIPT)
	@echo "🚀 開始執行 Facebook 爬蟲..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && $(PYTHON) $(SCRIPT); \
	else \
		echo "❌ 虛擬環境不存在，請先執行 'make setup'"; \
		exit 1; \
	fi

# 檢查環境狀態
check:
	@echo "🔍 檢查環境狀態..."
	@echo "Python 版本:"
	@$(PYTHON) --version
	@echo "虛擬環境:"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "✅ 虛擬環境存在"; \
	else \
		echo "❌ 虛擬環境不存在"; \
	fi
	@echo "必要檔案:"
	@if [ -f "$(SCRIPT)" ]; then \
		echo "✅ $(SCRIPT) 存在"; \
	else \
		echo "❌ $(SCRIPT) 不存在"; \
	fi
	@if [ -f "$(REQUIREMENTS)" ]; then \
		echo "✅ $(REQUIREMENTS) 存在"; \
	else \
		echo "❌ $(REQUIREMENTS) 不存在"; \
	fi

# 清理輸出檔案
clean:
	@echo "🧹 清理輸出檔案..."
	@rm -f facebook_data.json
	@rm -f *.pyc
	@rm -rf __pycache__
	@echo "✅ 清理完成"

# 重置環境
reset: clean
	@echo "🔄 重置環境..."
	@rm -rf $(VENV_DIR)
	@echo "✅ 環境重置完成"

# 快速重建環境
rebuild: reset setup
	@echo "✅ 環境重建完成"

# 查看爬取結果
show-result:
	@if [ -f "facebook_data.json" ]; then \
		echo "📊 Facebook 資料爬取結果:"; \
		$(PYTHON) -c "import json; data=json.load(open('facebook_data.json')); print(f'用戶: {data[\"profile\"][0]}'); print(f'貼文數: {len(data[\"data\"])}')"; \
	else \
		echo "❌ 找不到 facebook_data.json，請先執行 'make run'"; \
	fi

# 安裝額外套件（如果需要）
install-extra:
	@echo "📦 安裝額外套件..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && $(PIP) install pandas openpyxl matplotlib; \
	else \
		echo "❌ 虛擬環境不存在，請先執行 'make setup'"; \
	fi

# 更新套件
update:
	@echo "🔄 更新套件..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade -r $(REQUIREMENTS); \
	else \
		echo "❌ 虛擬環境不存在，請先執行 'make setup'"; \
	fi

# 偵錯模式執行
debug: $(SCRIPT)
	@echo "🐛 偵錯模式執行..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && $(PYTHON) -u $(SCRIPT); \
	else \
		echo "❌ 虛擬環境不存在，請先執行 'make setup'"; \
	fi

# 防止檔案名稱衝突
.PHONY: help setup venv install run check clean reset rebuild show-result install-extra update debug
