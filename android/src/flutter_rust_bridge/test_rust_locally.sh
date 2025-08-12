#!/bin/bash

echo "🦀 本地 Rust FFI 測試"
echo "==================="

# 建置 Rust 函式庫
echo "📦 建置 Rust 函式庫..."
cargo build --release

# 建立簡單的 C 測試程式
cat > /tmp/test_rust_ffi.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <string.h>

// 函數指標定義
typedef int (*add_numbers_func)(int, int);
typedef char* (*get_system_info_func)();
typedef char* (*process_message_func)(const char*);
typedef void (*free_string_func)(char*);

int main() {
    printf("[BitoPro Test] 載入 Rust 動態函式庫...\n");
    
    // 載入動態函式庫
    void* handle = dlopen("/home/shihyu/rust_to_fluuter/target/release/librust_flutter_bridge.so", RTLD_LAZY);
    if (!handle) {
        printf("❌ 無法載入函式庫: %s\n", dlerror());
        return 1;
    }
    
    // 載入函數
    add_numbers_func add_numbers = (add_numbers_func)dlsym(handle, "rust_add_numbers");
    get_system_info_func get_system_info = (get_system_info_func)dlsym(handle, "rust_get_system_info");
    process_message_func process_message = (process_message_func)dlsym(handle, "rust_process_message");
    free_string_func free_string = (free_string_func)dlsym(handle, "rust_free_string");
    
    if (!add_numbers || !get_system_info || !process_message || !free_string) {
        printf("❌ 無法載入函數: %s\n", dlerror());
        dlclose(handle);
        return 1;
    }
    
    printf("✅ 函式庫載入成功！\n\n");
    
    // 測試數字加法
    printf("🔢 測試數字加法...\n");
    int result = add_numbers(123, 456);
    printf("   123 + 456 = %d\n", result);
    if (result == 579) {
        printf("   ✅ 加法測試通過！\n\n");
    } else {
        printf("   ❌ 加法測試失敗！\n\n");
    }
    
    // 測試系統資訊
    printf("ℹ️  測試系統資訊...\n");
    char* sys_info = get_system_info();
    if (sys_info) {
        printf("   %s\n", sys_info);
        free_string(sys_info);
        printf("   ✅ 系統資訊測試通過！\n\n");
    } else {
        printf("   ❌ 系統資訊測試失敗！\n\n");
    }
    
    // 測試訊息處理
    printf("📨 測試訊息處理...\n");
    const char* json_msg = "{\"id\": 42, \"content\": \"BitoPro 測試訊息\", \"timestamp\": 1234567890}";
    printf("   發送: %s\n", json_msg);
    char* response = process_message(json_msg);
    if (response) {
        printf("   回應: %s\n", response);
        free_string(response);
        printf("   ✅ 訊息處理測試通過！\n\n");
    } else {
        printf("   ❌ 訊息處理測試失敗！\n\n");
    }
    
    printf("🎉 所有測試完成！\n");
    
    dlclose(handle);
    return 0;
}
EOF

# 編譯並執行測試
echo "🔨 編譯測試程式..."
gcc -o /tmp/test_rust_ffi /tmp/test_rust_ffi.c -ldl

if [ $? -eq 0 ]; then
    echo "✅ 編譯成功！"
    echo ""
    echo "🧪 執行測試..."
    echo "================="
    /tmp/test_rust_ffi
    echo ""
else
    echo "❌ 編譯失敗！"
    exit 1
fi

# 清理
rm -f /tmp/test_rust_ffi /tmp/test_rust_ffi.c