#!/bin/bash

echo "=== Testing dlopen and Plugin System ==="
echo

# 複製動態庫
echo "1. Copying dynamic library for dlopen test..."
cp ../dynamic-lib/libdynamic.so .

# 編譯 dlopen 基本範例
echo -e "\n2. Compiling basic dlopen demo..."
gcc -o dlopen_demo dlopen_demo.c -ldl

echo -e "\n3. Running basic dlopen demo:"
./dlopen_demo

# 創建插件目錄
echo -e "\n4. Setting up plugin system..."
mkdir -p plugins

# 編譯插件
echo -e "\n5. Compiling plugins..."
gcc -fPIC -shared -fvisibility=hidden -o plugins/plugin1.so plugin1.c
gcc -fPIC -shared -fvisibility=hidden -o plugins/plugin2.so plugin2.c

echo "Plugins created:"
ls -la plugins/

# 編譯插件載入器
echo -e "\n6. Compiling plugin loader..."
gcc -o plugin_loader plugin_loader.c -ldl

# 運行插件系統
echo -e "\n7. Running plugin system:"
./plugin_loader

# 測試 dlopen flags
echo -e "\n8. Testing dlopen flags with advanced features..."
cat > dlopen_advanced.c << 'EOF'
#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>

void test_dlopen_flags() {
    void *handle;

    // RTLD_NOLOAD - 檢查庫是否已加載
    handle = dlopen("libc.so.6", RTLD_NOLOAD);
    if (handle) {
        printf("libc.so.6 is already loaded\n");
        dlclose(handle);
    }

    // Test dladdr
    Dl_info info;
    void *addr = (void *)printf;

    if (dladdr(addr, &info)) {
        printf("Function: %s\n", info.dli_sname);
        printf("Library: %s\n", info.dli_fname);
    }
}

int main() {
    test_dlopen_flags();
    return 0;
}
EOF

gcc -o dlopen_advanced dlopen_advanced.c -ldl
echo -e "\n9. Running advanced dlopen tests:"
./dlopen_advanced

# 檢查導出符號
echo -e "\n10. Checking exported symbols in plugins:"
echo "Plugin 1:"
nm -D plugins/plugin1.so | grep plugin_info
echo "Plugin 2:"
nm -D plugins/plugin2.so | grep plugin_info