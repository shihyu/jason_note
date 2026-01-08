# Low Latency C++ Project Makefile
#
# 此 Makefile 提供統一的介面來管理各章節的建置與清理。
# 每個章節目錄下通常包含 scripts/build.sh，此 Makefile 僅作為 wrapper。

.DEFAULT_GOAL := help

# 定義所有可用的章節
CHAPTERS := Chapter3 Chapter4 Chapter6 Chapter7 Chapter8 Chapter9 Chapter10 Chapter11 Chapter12

.PHONY: help
help:  ## 顯示說明訊息
	@echo "Low Latency C++ Project 管理工具"
	@echo ""
	@echo "可用指令："
	@echo "  make view-docs       - 在瀏覽器中開啟繁體中文導讀文件"
	@echo "  make build-all       - 建置所有章節的程式碼"
	@echo "  make clean-all       - 清理所有章節的建置產物"
	@echo ""
	@echo "  make build-ch3       - 僅建置 Chapter 3 (編譯器優化範例)"
	@echo "  make build-ch4       - 僅建置 Chapter 4 (低延遲元件庫)"
	@echo "  make build-chX       - 建置特定章節 (X 為章節號)"
	@echo ""
	@echo "  make clean-chX       - 清理特定章節"
	@echo ""
	@echo "使用範例："
	@echo "  make build-ch8"
	@echo "  make view-docs"

.PHONY: view-docs
view-docs:  ## 開啟繁體中文文件目錄
	@echo "開啟文件目錄..."
	@xdg-open docs/總覽.md 2>/dev/null || open docs/總覽.md || echo "請手動開啟 docs/總覽.md"

# 動態生成建置規則
define BUILD_RULE
.PHONY: build-$(1)
build-$(1):
	@echo "==> Building $(1)..."
	@if [ -f $(1)/scripts/build.sh ]; then \
		cd $(1)/scripts && ./build.sh; \
	elif [ -f $(1)/build.sh ]; then \
		cd $(1) && ./build.sh; \
	else \
		echo "Skipping $(1): No build script found."; \
	fi
endef

# 動態生成清理規則
define CLEAN_RULE
.PHONY: clean-$(1)
clean-$(1):
	@echo "==> Cleaning $(1)..."
	@rm -rf $(1)/cmake-build-debug $(1)/build
	@find $(1) -name "CMakeCache.txt" -delete
	@find $(1) -name "cmake_install.cmake" -delete
	@find $(1) -name "Makefile" -delete
	@find $(1) -name "CMakeFiles" -type d -exec rm -rf {} +
	@find $(1) -name "*.log" -delete
endef

# 應用規則到所有章節 (轉換為小寫 chX)
$(foreach chap,$(CHAPTERS),$(eval $(call BUILD_RULE,$(chap))))
$(foreach chap,$(CHAPTERS),$(eval $(call CLEAN_RULE,$(chap))))

# 為了方便使用，建立 alias (例如 build-Chapter8 -> build-ch8 的映射如果需要，這裡直接用原始目錄名)
# 這裡我們使用簡單的映射：build-ch3 -> build-Chapter3
.PHONY: build-ch3 build-ch4 build-ch6 build-ch7 build-ch8 build-ch9 build-ch10 build-ch11 build-ch12
build-ch3: build-Chapter3
build-ch4: build-Chapter4
build-ch6: build-Chapter6
build-ch7: build-Chapter7
build-ch8: build-Chapter8
build-ch9: build-Chapter9
build-ch10: build-Chapter10
build-ch11: build-Chapter11
build-ch12: build-Chapter12

.PHONY: clean-ch3 clean-ch4 clean-ch6 clean-ch7 clean-ch8 clean-ch9 clean-ch10 clean-ch11 clean-ch12
clean-ch3: clean-Chapter3
clean-ch4: clean-Chapter4
clean-ch6: clean-Chapter6
clean-ch7: clean-Chapter7
clean-ch8: clean-Chapter8
clean-ch9: clean-Chapter9
clean-ch10: clean-Chapter10
clean-ch11: clean-Chapter11
clean-ch12: clean-Chapter12

.PHONY: build-all
build-all: $(foreach chap,$(CHAPTERS),build-$(chap))  ## 建置所有章節

.PHONY: clean-all
clean-all: $(foreach chap,$(CHAPTERS),clean-$(chap))  ## 清理所有章節
