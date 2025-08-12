# Rust-Flutter Bridge Project Makefile
# ==================================

# Variables
RUST_TARGET_DIR = target
FLUTTER_APP_DIR = flutter_app
RUST_LIB_NAME = librust_flutter_bridge.so
RUST_LIB_PATH = $(RUST_TARGET_DIR)/release/$(RUST_LIB_NAME)
ANDROID_JNI_DIR = $(FLUTTER_APP_DIR)/android/app/src/main/jniLibs

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
PURPLE = \033[0;35m
CYAN = \033[0;36m
NC = \033[0m # No Color

.PHONY: help build test clean install run dev check lint format docker

# Default target
help: ## 顯示幫助信息
	@echo "${BLUE}Rust-Flutter Bridge Project${NC}"
	@echo "${BLUE}=============================${NC}"
	@echo ""
	@echo "${YELLOW}Available targets:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}'
	@echo ""

build: build-rust copy-libs ## 建置完整專案 (Rust + 複製函式庫)
	@echo "${GREEN}✅ Project build completed!${NC}"

build-rust: ## 建置 Rust 函式庫 (release 模式)
	@echo "${BLUE}🦀 Building Rust library...${NC}"
	cargo build --release
	@echo "${GREEN}✅ Rust library built successfully${NC}"

build-debug: ## 建置 Rust 函式庫 (debug 模式)
	@echo "${BLUE}🦀 Building Rust library (debug)...${NC}"
	cargo build
	@echo "${GREEN}✅ Rust debug library built successfully${NC}"

copy-libs: build-rust ## 複製 Rust 函式庫到 Flutter 專案
	@echo "${BLUE}📦 Copying libraries to Flutter project...${NC}"
	@mkdir -p $(ANDROID_JNI_DIR)/x86_64
	@mkdir -p $(ANDROID_JNI_DIR)/arm64-v8a
	@mkdir -p $(ANDROID_JNI_DIR)/armeabi-v7a
	cp $(RUST_LIB_PATH) $(FLUTTER_APP_DIR)/
	cp $(RUST_LIB_PATH) $(ANDROID_JNI_DIR)/x86_64/
	@echo "${GREEN}✅ Libraries copied successfully${NC}"

test: test-rust test-flutter ## 執行所有測試
	@echo "${GREEN}🎉 All tests completed!${NC}"

test-rust: ## 執行 Rust 測試
	@echo "${BLUE}🦀 Running Rust tests...${NC}"
	cargo test
	@echo "${GREEN}✅ Rust tests passed${NC}"

test-flutter: flutter-deps ## 執行 Flutter 測試
	@echo "${BLUE}📱 Running Flutter tests...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter test test/widget_test.dart test/rust_bridge_unit_test.dart
	@echo "${GREEN}✅ Flutter tests passed${NC}"

test-integration: flutter-deps ## 執行 Flutter 整合測試 (需要 FFI)
	@echo "${BLUE}🔗 Running Flutter integration tests...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter test test/integration_test.dart
	@echo "${GREEN}✅ Integration tests passed${NC}"

flutter-deps: ## 安裝 Flutter 依賴
	@echo "${BLUE}📦 Installing Flutter dependencies...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter pub get
	@echo "${GREEN}✅ Flutter dependencies installed${NC}"

clean: ## 清理建置文件
	@echo "${YELLOW}🧹 Cleaning project...${NC}"
	cargo clean
	cd $(FLUTTER_APP_DIR) && flutter clean
	rm -f $(FLUTTER_APP_DIR)/$(RUST_LIB_NAME)
	rm -rf $(ANDROID_JNI_DIR)
	@echo "${GREEN}✅ Project cleaned${NC}"

install: build flutter-deps copy-libs ## 完整安裝 (建置 + 複製函式庫 + Flutter 依賴)
	@echo "${GREEN}🎉 Installation completed!${NC}"

run: build copy-libs flutter-deps ## 建置並執行 Flutter 應用程式
	@echo "${BLUE}🚀 Running Flutter app...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter run

run-release: build copy-libs flutter-deps ## 建置並執行 Flutter 應用程式 (release 模式)
	@echo "${BLUE}🚀 Running Flutter app (release)...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter run --release

dev: build-debug copy-libs flutter-deps ## 開發模式 (debug 建置 + hot reload)
	@echo "${BLUE}🔥 Starting development mode...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter run --hot

check: ## 執行程式碼檢查
	@echo "${BLUE}🔍 Running code checks...${NC}"
	cargo check
	cargo clippy -- -D warnings
	cd $(FLUTTER_APP_DIR) && flutter analyze
	@echo "${GREEN}✅ Code checks passed${NC}"

lint: ## 執行程式碼 linting
	@echo "${BLUE}🔍 Running linters...${NC}"
	cargo clippy
	cd $(FLUTTER_APP_DIR) && flutter analyze
	@echo "${GREEN}✅ Linting completed${NC}"

format: ## 格式化程式碼
	@echo "${BLUE}✨ Formatting code...${NC}"
	cargo fmt
	cd $(FLUTTER_APP_DIR) && dart format .
	@echo "${GREEN}✅ Code formatted${NC}"

benchmark: build copy-libs flutter-deps ## 執行效能基準測試
	@echo "${BLUE}⚡ Running benchmark tests...${NC}"
	cargo test --release -- --nocapture test_memory_management
	cd $(FLUTTER_APP_DIR) && flutter test test/rust_bridge_unit_test.dart --plain-name="should handle benchmark calculation logic"
	@echo "${GREEN}✅ Benchmark tests completed${NC}"

size-check: build ## 檢查建置產物大小
	@echo "${BLUE}📏 Checking build sizes...${NC}"
	@echo "${CYAN}Rust library size:${NC}"
	ls -lh $(RUST_LIB_PATH)
	@echo "${CYAN}Debug library size:${NC}"
	ls -lh $(RUST_TARGET_DIR)/debug/$(RUST_LIB_NAME) 2>/dev/null || echo "Debug library not found"
	@echo "${GREEN}✅ Size check completed${NC}"

security-audit: ## 執行安全性審計
	@echo "${BLUE}🔒 Running security audit...${NC}"
	cargo audit
	@echo "${GREEN}✅ Security audit completed${NC}"

docs: ## 產生文件
	@echo "${BLUE}📚 Generating documentation...${NC}"
	cargo doc --open
	@echo "${GREEN}✅ Documentation generated${NC}"

# Android specific targets
android-build: build copy-libs flutter-deps ## 建置 Android APK
	@echo "${BLUE}📱 Building Android APK...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter build apk
	@echo "${GREEN}✅ Android APK built successfully${NC}"

android-release: build copy-libs flutter-deps ## 建置 Android release APK
	@echo "${BLUE}📱 Building Android release APK...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter build apk --release
	@echo "${GREEN}✅ Android release APK built successfully${NC}"

# Cross-compilation targets
build-android-arm64: ## 交叉編譯 ARM64 Android
	@echo "${BLUE}🤖 Cross-compiling for Android ARM64...${NC}"
	cargo build --release --target aarch64-linux-android
	@mkdir -p $(ANDROID_JNI_DIR)/arm64-v8a
	cp target/aarch64-linux-android/release/$(RUST_LIB_NAME) $(ANDROID_JNI_DIR)/arm64-v8a/
	@echo "${GREEN}✅ ARM64 Android library built${NC}"

build-android-arm: ## 交叉編譯 ARM Android
	@echo "${BLUE}🤖 Cross-compiling for Android ARM...${NC}"
	cargo build --release --target armv7-linux-androideabi  
	@mkdir -p $(ANDROID_JNI_DIR)/armeabi-v7a
	cp target/armv7-linux-androideabi/release/$(RUST_LIB_NAME) $(ANDROID_JNI_DIR)/armeabi-v7a/
	@echo "${GREEN}✅ ARM Android library built${NC}"

# Docker targets
docker-build: ## 建置 Docker 映像
	@echo "${BLUE}🐳 Building Docker image...${NC}"
	docker build -t rust-flutter-bridge .
	@echo "${GREEN}✅ Docker image built${NC}"

docker-test: ## 在 Docker 中執行測試
	@echo "${BLUE}🐳 Running tests in Docker...${NC}"
	docker run --rm rust-flutter-bridge make test-rust
	@echo "${GREEN}✅ Docker tests completed${NC}"

# CI/CD targets
ci: check test ## CI 管道 (檢查 + 測試)
	@echo "${GREEN}🎉 CI pipeline completed successfully!${NC}"

cd: build android-build ## CD 管道 (建置 + Android)
	@echo "${GREEN}🚀 CD pipeline completed successfully!${NC}"

# Development utilities
watch-rust: ## 監控 Rust 程式碼變更並重新建置
	@echo "${BLUE}👀 Watching Rust code changes...${NC}"
	cargo watch -x "build --release" -x "test"

watch-flutter: flutter-deps ## 監控 Flutter 程式碼變更並重新測試
	@echo "${BLUE}👀 Watching Flutter code changes...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter test --watch

profile: ## 效能分析
	@echo "${BLUE}📊 Running performance profiling...${NC}"
	cargo build --release
	time cargo test --release test_memory_management -- --nocapture
	@echo "${GREEN}✅ Profiling completed${NC}"

# Information targets
info: ## 顯示專案資訊
	@echo "${BLUE}Project Information${NC}"
	@echo "${BLUE}===================${NC}"
	@echo "${CYAN}Rust version:${NC} $$(rustc --version)"
	@echo "${CYAN}Cargo version:${NC} $$(cargo --version)"
	@echo "${CYAN}Flutter version:${NC} $$(cd $(FLUTTER_APP_DIR) && flutter --version | head -n 1)"
	@echo "${CYAN}Project structure:${NC}"
	@tree -L 2 -I 'target|.git' .

status: ## 顯示建置狀態
	@echo "${BLUE}Build Status${NC}"
	@echo "${BLUE}============${NC}"
	@echo "${CYAN}Rust library exists:${NC} $$([ -f $(RUST_LIB_PATH) ] && echo '✅ Yes' || echo '❌ No')"
	@echo "${CYAN}Flutter library copied:${NC} $$([ -f $(FLUTTER_APP_DIR)/$(RUST_LIB_NAME) ] && echo '✅ Yes' || echo '❌ No')"
	@echo "${CYAN}Flutter deps installed:${NC} $$([ -d $(FLUTTER_APP_DIR)/.dart_tool ] && echo '✅ Yes' || echo '❌ No')"

# Quick commands
quick-test: test-rust test-flutter ## 快速測試 (跳過整合測試)
	@echo "${GREEN}⚡ Quick tests completed!${NC}"

quick-build: build-rust copy-libs ## 快速建置 (跳過 Flutter 依賴)
	@echo "${GREEN}⚡ Quick build completed!${NC}"

# All-in-one targets
all: clean install test ## 完整流程 (清理 + 安裝 + 測試)
	@echo "${GREEN}🎉 Complete workflow finished!${NC}"

demo: build copy-libs flutter-deps ## 執行展示 (建置 + 執行)
	@echo "${BLUE}🎭 Starting demo...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter run --dart-define=DEMO_MODE=true

logcat: ## 監控 BitoPro logcat 日誌
	@echo "${BLUE}🔍 Starting BitoPro logcat monitor...${NC}"
	./logcat_bitopro.sh

test-android: build copy-libs flutter-deps ## 在 Android 設備上測試
	@echo "${BLUE}📱 Testing on Android device...${NC}"
	cd $(FLUTTER_APP_DIR) && flutter run --debug

logcat-all: ## 顯示所有 Android 日誌
	@echo "${BLUE}📜 Showing all Android logs...${NC}"
	adb logcat -v time

test-local-ffi: build ## 本地測試 Rust FFI 功能
	@echo "${BLUE}🦀 Testing Rust FFI locally...${NC}"
	./test_rust_locally.sh

test-with-logs: build copy-libs flutter-deps ## 執行應用程式並同時監控日誌
	@echo "${BLUE}🚀 Testing app with log monitoring...${NC}"
	./test_with_logs.sh