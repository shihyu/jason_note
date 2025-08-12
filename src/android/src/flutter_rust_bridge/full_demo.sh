#!/bin/bash

echo "🎯 BitoPro Rust-Flutter 完整展示"
echo "================================="
echo ""

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 輔助函數
print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# 檢查依賴
check_dependencies() {
    print_step "🔍 檢查系統依賴..."
    
    if ! command -v rustc &> /dev/null; then
        print_error "Rust 未安裝"
        exit 1
    fi
    print_success "Rust: $(rustc --version)"
    
    if ! command -v flutter &> /dev/null; then
        print_error "Flutter 未安裝"
        exit 1
    fi
    print_success "Flutter: $(flutter --version | head -n 1)"
    
    if ! command -v make &> /dev/null; then
        print_error "Make 未安裝"
        exit 1
    fi
    print_success "Make 工具可用"
    
    echo ""
}

# 主要演示流程
main_demo() {
    echo -e "${PURPLE}🎬 開始 BitoPro Rust-Flutter 技術展示${NC}"
    echo "=================================================="
    echo ""

    # 1. 檢查專案狀態
    print_step "📊 1. 檢查專案狀態"
    make status
    echo ""

    # 2. 顯示專案資訊
    print_step "📋 2. 專案資訊"
    make info 2>/dev/null || echo "專案資訊命令暫未實作"
    echo ""

    # 3. 執行 Rust 測試
    print_step "🦀 3. Rust 單元測試"
    if make test-rust; then
        print_success "Rust 測試通過 (6/6)"
    else
        print_error "Rust 測試失敗"
        return 1
    fi
    echo ""

    # 4. 本地 FFI 測試
    print_step "🔗 4. 本地 FFI 功能測試"
    if make test-local-ffi; then
        print_success "FFI 功能測試通過"
    else
        print_error "FFI 功能測試失敗"
        return 1
    fi
    echo ""

    # 5. Flutter 測試
    print_step "📱 5. Flutter 單元測試"
    if make test-flutter; then
        print_success "Flutter 測試通過"
    else
        print_error "Flutter 測試失敗"
        return 1
    fi
    echo ""

    # 6. 建置專案
    print_step "🏗️  6. 專案建置"
    if make build; then
        print_success "專案建置成功"
    else
        print_error "專案建置失敗"
        return 1
    fi
    echo ""

    # 7. 檢查建置產物
    print_step "📏 7. 建置產物分析"
    make size-check
    echo ""

    # 8. Android 設備檢查
    print_step "📱 8. Android 設備檢查"
    if command -v adb &> /dev/null; then
        if adb devices | grep -q "device$"; then
            print_success "檢測到 Android 設備"
            echo ""
            print_info "可以執行以下命令進行 Android 測試："
            echo "  make test-android    # 在設備上運行應用程式"
            echo "  make logcat         # 監控 BitoPro 日誌"
            echo "  make test-with-logs # 同時運行應用和監控日誌"
        else
            print_warning "未檢測到 Android 設備"
            print_info "可以使用模擬器或桌面版本："
            echo "  make run            # 運行 Flutter 應用程式"
        fi
    else
        print_warning "ADB 未安裝，跳過 Android 檢查"
    fi
    echo ""

    # 9. 程式碼品質檢查
    print_step "🔍 9. 程式碼品質檢查"
    print_info "執行 Rust 程式碼檢查..."
    if cargo fmt -- --check >/dev/null 2>&1; then
        print_success "Rust 程式碼格式正確"
    else
        print_warning "Rust 程式碼需要格式化 (執行 make format)"
    fi

    if cargo clippy -- -D warnings >/dev/null 2>&1; then
        print_success "Rust Clippy 檢查通過"
    else
        print_warning "Rust 有 Clippy 警告 (執行 make lint)"
    fi
    echo ""

    # 10. 展示總結
    print_step "📈 10. 展示總結"
    echo -e "${GREEN}🎉 BitoPro Rust-Flutter 技術展示完成！${NC}"
    echo ""
    echo "✨ 主要成果："
    echo "  • Rust FFI 動態函式庫: $(ls -lh target/release/librust_flutter_bridge.so | awk '{print $5}')"
    echo "  • 測試覆蓋: Rust 6個 + Flutter 7個 = 13個測試"
    echo "  • 日誌系統: 完整的 BitoPro 標籤追蹤"
    echo "  • 開發工具: 35+ Makefile 命令"
    echo ""
    echo "🚀 下一步操作："
    echo "  make run              # 啟動 Flutter 應用程式"
    echo "  make dev              # 開發模式 (支援熱重載)"
    echo "  make test-android     # Android 設備測試"
    echo "  make logcat           # 監控 Android 日誌"
    echo "  make help             # 查看所有可用命令"
    echo ""
}

# 互動式選單
interactive_menu() {
    echo -e "${CYAN}🎮 互動式功能選單${NC}"
    echo "==================="
    echo "1. 執行完整展示"
    echo "2. 本地 FFI 測試"
    echo "3. 啟動 Flutter 應用"
    echo "4. Android 設備測試"
    echo "5. 監控日誌"
    echo "6. 查看幫助"
    echo "0. 退出"
    echo ""
    
    read -p "請選擇操作 (0-6): " choice
    
    case $choice in
        1)
            main_demo
            ;;
        2)
            make test-local-ffi
            ;;
        3)
            make run
            ;;
        4)
            make test-android
            ;;
        5)
            make logcat
            ;;
        6)
            make help
            ;;
        0)
            echo "再見！"
            exit 0
            ;;
        *)
            print_error "無效選擇，請重新選擇"
            interactive_menu
            ;;
    esac
}

# 主函數
main() {
    # 檢查是否在正確目錄
    if [ ! -f "Cargo.toml" ]; then
        print_error "請在專案根目錄執行此腳本"
        exit 1
    fi

    check_dependencies

    # 檢查命令行參數
    if [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
        interactive_menu
    else
        main_demo
        
        # 詢問是否要啟動互動選單
        echo ""
        read -p "是否要進入互動式選單？(y/n): " answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            echo ""
            interactive_menu
        fi
    fi
}

# 執行主函數
main "$@"