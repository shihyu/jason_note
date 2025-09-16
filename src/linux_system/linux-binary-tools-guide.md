# Linux 二進制工具完整指南

## 目錄
- [核心分析工具](#核心分析工具)
- [動態鏈接工具](#動態鏈接工具)
- [調試追蹤工具](#調試追蹤工具)
- [性能分析工具](#性能分析工具)
- [安全分析工具](#安全分析工具)
- [實戰範例](#實戰範例)

## 核心分析工具

### 1. nm - 符號表查看器
```bash
# 常用選項
nm [options] file

# 選項說明
-A  # 顯示文件名
-C  # demangle C++ 符號
-D  # 顯示動態符號
-g  # 只顯示外部符號
-n  # 按地址排序
-u  # 只顯示未定義符號
-r  # 反向排序
--size-sort  # 按大小排序

# 符號類型
# T/t - Text (代碼段)
# D/d - Data (初始化數據)
# B/b - BSS (未初始化數據)
# U   - Undefined
# W/w - Weak symbol

# 實例
nm -C program | grep "std::"  # 查看 C++ STL 符號
nm -D --size-sort /lib/x86_64-linux-gnu/libc.so.6 | tail -20
```

### 2. objdump - 目標文件反彙編器
```bash
# 核心功能
objdump -d file       # 反彙編
objdump -D file       # 反彙編所有節區
objdump -S file       # 源碼混合反彙編（需調試信息）
objdump -t file       # 符號表
objdump -T file       # 動態符號表
objdump -r file       # 重定位信息
objdump -R file       # 動態重定位
objdump -x file       # 所有 headers
objdump -h file       # 節區 headers
objdump -j .text -d file  # 只反彙編 .text 節

# Intel 語法（更易讀）
objdump -M intel -d file

# 查看特定函數
objdump -d program | sed -n '/<main>:/,/^$/p'
```

### 3. readelf - ELF 格式分析器
```bash
# ELF 結構分析
readelf -h file       # ELF header
readelf -l file       # Program headers (segments)
readelf -S file       # Section headers
readelf -s file       # 符號表
readelf -r file       # 重定位
readelf -d file       # 動態段
readelf -V file       # 版本信息
readelf -n file       # Notes
readelf -a file       # 所有信息

# 實用查詢
readelf -p .comment file    # 查看編譯器版本
readelf -p .rodata file     # 查看只讀字串
readelf -x .got.plt file    # 十六進制顯示 GOT 表
```

### 4. strings - 字串提取器
```bash
# 高級用法
strings -a file      # 掃描整個文件
strings -f file*     # 顯示文件名
strings -n 20 file   # 最小長度 20
strings -t x file    # 十六進制偏移
strings -e S file    # 7-bit byte strings (ASCII)
strings -e l file    # 16-bit littleendian
strings -e b file    # 16-bit bigendian

# 組合使用
strings file | grep -i password
strings -t x file | grep "error"
```

### 5. file - 文件類型識別
```bash
file program
file -b program      # 簡潔輸出
file -i program      # MIME 類型
file -L symlink      # 跟隨符號鏈接
file -s /dev/sda     # 特殊文件
```

### 6. size - 節區大小統計
```bash
size program
size -A program      # System V 格式
size -B program      # Berkeley 格式
size --format=SysV *.o  # 多文件比較
```

## 動態鏈接工具

### 1. ldd - 共享庫依賴查看
```bash
# 安全模式（避免執行不信任的二進制）
ldd -r file          # 檢查未解析的符號
ldd -u file          # 未使用的直接依賴
ldd -v file          # 詳細信息（包括版本）

# 替代方案（更安全）
objdump -p file | grep NEEDED
readelf -d file | grep NEEDED

# 遞歸查看所有依賴
function ldd_recursive() {
    for lib in $(ldd $1 | awk '{print $3}' | grep "^/"); do
        echo "=== $lib ==="
        ldd $lib
    done
}
```

### 2. ldconfig - 動態鏈接器配置
```bash
# 管理共享庫緩存
sudo ldconfig              # 更新緩存
sudo ldconfig -v           # 詳細輸出
ldconfig -p                # 打印緩存內容
ldconfig -p | wc -l       # 統計庫數量

# 配置文件
/etc/ld.so.conf            # 主配置
/etc/ld.so.conf.d/*.conf   # 模塊化配置
/etc/ld.so.cache           # 緩存文件

# 添加自定義路徑
echo "/opt/myapp/lib" | sudo tee /etc/ld.so.conf.d/myapp.conf
sudo ldconfig
```

### 3. LD 環境變數詳解

#### LD_LIBRARY_PATH
```bash
# 搜索優先級（從高到低）：
# 1. DT_RPATH (除非有 DT_RUNPATH)
# 2. LD_LIBRARY_PATH
# 3. DT_RUNPATH
# 4. /etc/ld.so.cache
# 5. /lib, /usr/lib

export LD_LIBRARY_PATH=/custom/lib:$LD_LIBRARY_PATH

# 查看加載過程
LD_DEBUG=libs LD_LIBRARY_PATH=/test/lib ./program
```

#### LD_PRELOAD
```bash
# Hook 機制範例
# malloc_hook.c
cat > malloc_hook.c << 'EOF'
#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>

void* malloc(size_t size) {
    static void* (*real_malloc)(size_t) = NULL;
    if (!real_malloc)
        real_malloc = dlsym(RTLD_NEXT, "malloc");
    
    void* ptr = real_malloc(size);
    fprintf(stderr, "malloc(%zu) = %p\n", size, ptr);
    return ptr;
}
EOF

gcc -shared -fPIC -o malloc_hook.so malloc_hook.c -ldl
LD_PRELOAD=./malloc_hook.so ls
```

#### LD_DEBUG 完整選項
```bash
# 所有選項
LD_DEBUG=help ./program

# 常用選項組合
LD_DEBUG=libs          # 庫搜索路徑
LD_DEBUG=files         # 文件載入
LD_DEBUG=symbols       # 符號解析
LD_DEBUG=bindings      # 符號綁定
LD_DEBUG=versions      # 版本依賴
LD_DEBUG=reloc         # 重定位處理
LD_DEBUG=statistics    # 統計信息
LD_DEBUG=all           # 所有信息

# 組合使用
LD_DEBUG=libs,symbols ./program 2>&1 | tee debug.log
```

#### 其他 LD 變數
```bash
LD_BIND_NOW=1          # 立即綁定所有符號
LD_TRACE_LOADED_OBJECTS=1  # 類似 ldd
LD_SHOW_AUXV=1         # 顯示輔助向量
LD_AUDIT=./audit.so    # 審計庫
LD_PROFILE=libc.so.6   # 性能分析
LD_PROFILE_OUTPUT=/tmp # 分析輸出目錄
```

## 調試追蹤工具

### 1. strace - 系統調用追蹤
```bash
# 高級用法
strace -e trace=file ./program     # 只追蹤文件操作
strace -e trace=network ./program  # 網絡操作
strace -e trace=memory ./program   # 內存操作
strace -e trace=process ./program  # 進程操作
strace -e trace=signal ./program   # 信號操作

# 過濾器
strace -e open,openat,close ./program
strace -e 'open*' ./program        # 通配符
strace -e '!futex' ./program       # 排除

# 輸出控制
strace -t ./program                # 時間戳
strace -tt ./program               # 微秒時間戳
strace -T ./program                # 系統調用時長
strace -c ./program                # 統計摘要
strace -C ./program                # 統計+正常輸出

# 進程控制
strace -p PID                      # 附加到進程
strace -f ./program                # 追蹤子進程
strace -ff -o trace ./program      # 分離輸出文件

# 高級過濾
strace -e inject=open:error=ENOENT ./program  # 注入錯誤
strace -e fault=malloc:error=ENOMEM:when=3 ./program
```

### 2. ltrace - 庫調用追蹤
```bash
# 進階用法
ltrace -c ./program               # 統計
ltrace -S ./program               # 同時顯示系統調用
ltrace -f ./program               # 追蹤子進程
ltrace -l /lib/libssl.so ./program  # 特定庫
ltrace -x 'malloc+free' ./program   # 特定函數

# 配置文件
~/.ltrace.conf                    # 用戶配置
/etc/ltrace.conf                  # 系統配置

# 自定義函數簽名
echo "int myfunction(string,int);" >> ~/.ltrace.conf
```

### 3. ptrace - 進程追蹤 API
```c
// ptrace 範例
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <unistd.h>

int main() {
    pid_t child = fork();
    if (child == 0) {
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        execl("/bin/ls", "ls", NULL);
    } else {
        wait(NULL);
        ptrace(PTRACE_CONT, child, NULL, NULL);
        wait(NULL);
    }
    return 0;
}
```

## 性能分析工具

### 1. perf - Linux 性能分析
```bash
# 基本使用
perf stat ./program               # 性能統計
perf record ./program              # 記錄性能數據
perf report                        # 查看報告
perf top                           # 實時分析

# 詳細分析
perf record -g ./program          # 調用圖
perf record -e cycles,instructions ./program
perf annotate                      # 註釋彙編

# 事件類型
perf list                          # 列出所有事件
perf stat -e cache-misses ./program
```

### 2. valgrind - 內存分析
```bash
# 內存洩漏檢測
valgrind --leak-check=full ./program
valgrind --leak-check=full --show-leak-kinds=all ./program

# 內存錯誤檢測
valgrind --track-origins=yes ./program

# 緩存分析
valgrind --tool=cachegrind ./program
cg_annotate cachegrind.out.*

# 調用圖生成
valgrind --tool=callgrind ./program
kcachegrind callgrind.out.*       # GUI 查看

# Heap 分析
valgrind --tool=massif ./program
ms_print massif.out.*
```

### 3. gprof - GNU 性能分析器
```bash
# 編譯時啟用
gcc -pg -o program program.c

# 運行程序生成 gmon.out
./program

# 生成報告
gprof program gmon.out > analysis.txt
gprof -b program gmon.out         # 簡潔輸出
gprof -p program gmon.out         # 平面檔案
gprof -q program gmon.out         # 調用圖
```

### 7. addr2line - 地址到源碼映射
```bash
# 基本用法
addr2line -e executable address

# 常用選項
-e file      # 指定可執行文件
-f           # 顯示函數名
-s           # 顯示簡短文件名（去掉路徑）
-C           # Demangle C++ 符號
-p           # 優雅輸出格式
-i           # 顯示內聯函數
-a           # 顯示地址
-j section   # 指定節區

# 實例用法
# 1. 單個地址查詢
addr2line -e program 0x400534

# 2. 多個地址查詢
addr2line -e program 0x400534 0x400550 0x400570

# 3. 從管道接收地址
echo "0x400534" | addr2line -e program

# 4. 顯示函數名和源碼位置
addr2line -fe program 0x400534

# 5. C++ 符號 demangle
addr2line -Cfe program 0x400534

# 6. 優雅格式輸出
addr2line -pfe program 0x400534

# 實戰範例：解析段錯誤
# 從 dmesg 或 coredump 獲取地址
dmesg | grep segfault
# program[1234]: segfault at 0 ip 00000000004005b4 sp 00007ffd12345678

# 解析崩潰地址
addr2line -Cfpe program 0x4005b4

# 從 backtrace 解析多個地址
cat backtrace.txt | while read addr; do
    addr2line -Cfpe program "$addr"
done

# 結合 objdump 使用
objdump -d program | grep "call" | awk '{print $1}' | sed 's/://' | \
    xargs addr2line -fe program

# 從 core dump 提取地址
gdb -q -batch -ex "bt" -ex "quit" program core | \
    grep -oE '0x[0-9a-f]+' | \
    xargs addr2line -Cfpe program
```

## 安全分析工具

### 1. checksec - 安全機制檢查
```bash
# 安裝
git clone https://github.com/slimm609/checksec.sh
cd checksec.sh

# 使用
./checksec --file=/bin/ls
./checksec --dir=/usr/bin
./checksec --proc-all

# 檢查項目
# - RELRO (Relocation Read-Only)
# - Stack Canary
# - NX (No-eXecute)
# - PIE (Position Independent Executable)
# - RPATH/RUNPATH
# - FORTIFY_SOURCE
```

### 2. patchelf - ELF 修改工具
```bash
# 修改動態鏈接器
patchelf --set-interpreter /lib/ld-linux.so.2 program

# 修改 RPATH/RUNPATH
patchelf --set-rpath /custom/lib program
patchelf --remove-rpath program
patchelf --print-rpath program

# 添加/刪除依賴
patchelf --add-needed libfoo.so program
patchelf --remove-needed libbar.so program
patchelf --replace-needed libold.so libnew.so program

# 修改 SONAME
patchelf --set-soname libnew.so.1 library.so
```

### 3. radare2 - 逆向工程框架
```bash
# 基本使用
r2 program
[0x00000000]> aa              # 分析所有
[0x00000000]> afl             # 列出函數
[0x00000000]> pdf @main       # 反彙編 main
[0x00000000]> iz              # 列出字串
[0x00000000]> iI              # 二進制信息
[0x00000000]> ie              # 入口點
[0x00000000]> iS              # 節區

# 視覺模式
[0x00000000]> V               # 十六進制視圖
[0x00000000]> VV              # 圖形視圖

# 調試模式
r2 -d program
[0x00000000]> db main         # 設置斷點
[0x00000000]> dc              # 繼續執行
[0x00000000]> dr              # 顯示寄存器
```

### 4. binwalk - 固件分析
```bash
# 掃描二進制
binwalk firmware.bin

# 提取文件
binwalk -e firmware.bin

# 熵分析
binwalk -E firmware.bin

# 簽名掃描
binwalk -B firmware.bin
```

## 動態和靜態庫完整指南

### 靜態庫 (.a) 創建和使用

#### 1. 創建靜態庫
```c
// math_utils.c
#include "math_utils.h"
#include <math.h>

double calculate_area(double radius) {
    return M_PI * radius * radius;
}

double calculate_volume(double radius) {
    return (4.0/3.0) * M_PI * radius * radius * radius;
}

// math_utils.h
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

double calculate_area(double radius);
double calculate_volume(double radius);

#endif

// string_utils.c
#include "string_utils.h"
#include <string.h>
#include <ctype.h>

void to_uppercase(char *str) {
    while (*str) {
        *str = toupper(*str);
        str++;
    }
}

int count_words(const char *str) {
    int count = 0;
    int in_word = 0;
    
    while (*str) {
        if (isspace(*str)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            count++;
        }
        str++;
    }
    return count;
}
```

編譯和創建靜態庫：
```bash
# 編譯目標文件
gcc -c math_utils.c -o math_utils.o
gcc -c string_utils.c -o string_utils.o

# 創建靜態庫
ar rcs libutils.a math_utils.o string_utils.o

# 查看靜態庫內容
ar -t libutils.a
ar -tv libutils.a  # 詳細信息

# 提取特定目標文件
ar -x libutils.a math_utils.o

# 添加新目標文件到現有庫
gcc -c new_utils.c -o new_utils.o
ar -r libutils.a new_utils.o

# 創建索引（提高鏈接速度）
ranlib libutils.a

# 查看庫中的符號
nm libutils.a
```

#### 2. 使用靜態庫
```c
// main_static.c
#include <stdio.h>
#include "math_utils.h"
#include "string_utils.h"

int main() {
    // 使用數學工具
    double radius = 5.0;
    printf("Circle area: %.2f\n", calculate_area(radius));
    printf("Sphere volume: %.2f\n", calculate_volume(radius));
    
    // 使用字串工具
    char text[] = "hello world";
    to_uppercase(text);
    printf("Uppercase: %s\n", text);
    
    const char *sentence = "This is a test sentence";
    printf("Word count: %d\n", count_words(sentence));
    
    return 0;
}
```

編譯和鏈接：
```bash
# 方法1：直接指定庫文件
gcc main_static.c libutils.a -lm -o program_static

# 方法2：使用 -L 和 -l 選項
gcc main_static.c -L. -lutils -lm -o program_static

# 方法3：分步編譯
gcc -c main_static.c -o main_static.o
gcc main_static.o -L. -lutils -lm -o program_static

# 查看鏈接的庫（靜態庫會被嵌入）
ldd program_static  # 不會顯示 libutils.a
size program_static  # 查看大小

# 確認符號已經嵌入
nm program_static | grep calculate_area
```

### 動態庫 (.so) 創建和使用

#### 1. 創建動態庫
```c
// dynamic_lib.c
#include <stdio.h>
#include <time.h>

// 使用 visibility 屬性控制導出
__attribute__((visibility("default"))) 
void public_function() {
    printf("This is a public function\n");
}

__attribute__((visibility("hidden")))
void private_function() {
    printf("This is a private function (hidden)\n");
}

// 構造和析構函數
__attribute__((constructor))
void lib_init() {
    printf("Library initialized at %ld\n", time(NULL));
}

__attribute__((destructor))
void lib_cleanup() {
    printf("Library cleanup\n");
}

// 版本化符號
__asm__(".symver old_function_v1,old_function@VERSION_1.0");
void old_function_v1() {
    printf("Old implementation (v1.0)\n");
}

__asm__(".symver old_function_v2,old_function@@VERSION_2.0");
void old_function_v2() {
    printf("New implementation (v2.0)\n");
}
```

創建版本腳本：
```bash
# version.map
VERSION_1.0 {
    global:
        old_function;
    local:
        *;
};

VERSION_2.0 {
    global:
        old_function;
        public_function;
} VERSION_1.0;
```

編譯動態庫：
```bash
# 基本編譯
gcc -fPIC -c dynamic_lib.c -o dynamic_lib.o
gcc -shared -o libdynamic.so dynamic_lib.o

# 帶版本控制
gcc -fPIC -shared -Wl,--version-script=version.map \
    -o libdynamic.so.2.0 dynamic_lib.c

# 創建符號鏈接
ln -s libdynamic.so.2.0 libdynamic.so.2
ln -s libdynamic.so.2 libdynamic.so

# 設置 SONAME
gcc -fPIC -shared -Wl,-soname,libdynamic.so.2 \
    -o libdynamic.so.2.0 dynamic_lib.c

# 控制符號可見性
gcc -fPIC -fvisibility=hidden -shared -o libdynamic.so dynamic_lib.c

# 查看導出符號
nm -D libdynamic.so
readelf -W -s libdynamic.so | grep -E "FUNC.*GLOBAL.*DEFAULT"

# 查看版本信息
readelf -V libdynamic.so
```

#### 2. 使用動態庫 - 編譯時鏈接
```c
// main_dynamic.c
#include <stdio.h>

// 聲明外部函數
extern void public_function();
extern void old_function();

int main() {
    printf("=== Using Dynamic Library ===\n");
    
    public_function();
    old_function();  // 會使用默認版本 (VERSION_2.0)
    
    return 0;
}
```

編譯和運行：
```bash
# 編譯鏈接
gcc main_dynamic.c -L. -ldynamic -o program_dynamic

# 設置運行時庫路徑
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
./program_dynamic

# 或使用 rpath
gcc main_dynamic.c -L. -ldynamic -Wl,-rpath,. -o program_dynamic
./program_dynamic

# 查看依賴
ldd program_dynamic
readelf -d program_dynamic | grep NEEDED
```

### dlopen 動態加載範例

#### 1. 基本 dlopen 使用
```c
// dlopen_demo.c
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

int main() {
    void *handle;
    void (*func)();
    char *error;
    
    // 打開動態庫
    handle = dlopen("./libdynamic.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return 1;
    }
    
    // 清除錯誤
    dlerror();
    
    // 獲取函數指針
    func = (void (*)()) dlsym(handle, "public_function");
    error = dlerror();
    if (error) {
        fprintf(stderr, "dlsym error: %s\n", error);
        dlclose(handle);
        return 1;
    }
    
    // 調用函數
    func();
    
    // 獲取變量地址
    int *var = (int *)dlsym(handle, "global_variable");
    if (var) {
        printf("Global variable value: %d\n", *var);
    }
    
    // 關閉庫
    dlclose(handle);
    
    return 0;
}
```

#### 2. 進階 dlopen - 插件系統
```c
// plugin_interface.h
#ifndef PLUGIN_INTERFACE_H
#define PLUGIN_INTERFACE_H

typedef struct {
    const char *name;
    const char *version;
    int (*initialize)(void);
    int (*execute)(const char *args);
    void (*cleanup)(void);
} plugin_info_t;

#define PLUGIN_EXPORT __attribute__((visibility("default")))

#endif

// plugin1.c
#include "plugin_interface.h"
#include <stdio.h>

static int plugin1_init() {
    printf("Plugin 1 initialized\n");
    return 0;
}

static int plugin1_execute(const char *args) {
    printf("Plugin 1 executing with args: %s\n", args ? args : "(none)");
    return 0;
}

static void plugin1_cleanup() {
    printf("Plugin 1 cleanup\n");
}

PLUGIN_EXPORT plugin_info_t plugin_info = {
    .name = "Sample Plugin 1",
    .version = "1.0.0",
    .initialize = plugin1_init,
    .execute = plugin1_execute,
    .cleanup = plugin1_cleanup
};

// plugin_loader.c
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <dirent.h>
#include <string.h>
#include "plugin_interface.h"

typedef struct plugin_node {
    void *handle;
    plugin_info_t *info;
    struct plugin_node *next;
} plugin_node_t;

plugin_node_t *plugins = NULL;

void load_plugin(const char *path) {
    void *handle = dlopen(path, RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "Cannot load plugin %s: %s\n", path, dlerror());
        return;
    }
    
    plugin_info_t *info = dlsym(handle, "plugin_info");
    if (!info) {
        fprintf(stderr, "Plugin %s has no plugin_info: %s\n", path, dlerror());
        dlclose(handle);
        return;
    }
    
    // 初始化插件
    if (info->initialize && info->initialize() != 0) {
        fprintf(stderr, "Plugin %s initialization failed\n", path);
        dlclose(handle);
        return;
    }
    
    // 添加到插件列表
    plugin_node_t *node = malloc(sizeof(plugin_node_t));
    node->handle = handle;
    node->info = info;
    node->next = plugins;
    plugins = node;
    
    printf("Loaded plugin: %s (version %s)\n", info->name, info->version);
}

void load_all_plugins(const char *dir) {
    DIR *d = opendir(dir);
    if (!d) return;
    
    struct dirent *entry;
    while ((entry = readdir(d)) != NULL) {
        if (strstr(entry->d_name, ".so")) {
            char path[PATH_MAX];
            snprintf(path, sizeof(path), "%s/%s", dir, entry->d_name);
            load_plugin(path);
        }
    }
    closedir(d);
}

void execute_all_plugins(const char *args) {
    plugin_node_t *node = plugins;
    while (node) {
        if (node->info->execute) {
            node->info->execute(args);
        }
        node = node->next;
    }
}

void unload_all_plugins() {
    plugin_node_t *node = plugins;
    while (node) {
        plugin_node_t *next = node->next;
        if (node->info->cleanup) {
            node->info->cleanup();
        }
        dlclose(node->handle);
        free(node);
        node = next;
    }
    plugins = NULL;
}

int main() {
    printf("=== Plugin System Demo ===\n");
    
    // 載入所有插件
    load_all_plugins("./plugins");
    
    // 執行插件
    execute_all_plugins("test arguments");
    
    // 卸載插件
    unload_all_plugins();
    
    return 0;
}
```

編譯插件系統：
```bash
# 編譯插件
gcc -fPIC -shared -fvisibility=hidden -o plugins/plugin1.so plugin1.c
gcc -fPIC -shared -fvisibility=hidden -o plugins/plugin2.so plugin2.c

# 編譯載入器
gcc -o plugin_loader plugin_loader.c -ldl

# 運行
./plugin_loader
```

#### 3. dlopen 高級特性
```c
// dlopen_advanced.c
#include <stdio.h>
#include <dlfcn.h>
#include <gnu/lib-names.h>

void test_dlopen_flags() {
    void *handle;
    
    // RTLD_LAZY vs RTLD_NOW
    handle = dlopen("libm.so.6", RTLD_LAZY);  // 延遲綁定
    handle = dlopen("libm.so.6", RTLD_NOW);   // 立即綁定所有符號
    
    // RTLD_GLOBAL vs RTLD_LOCAL
    handle = dlopen("libm.so.6", RTLD_GLOBAL); // 符號全局可見
    handle = dlopen("libm.so.6", RTLD_LOCAL);  // 符號局部可見（默認）
    
    // RTLD_NODELETE - 防止 dlclose 卸載
    handle = dlopen("libm.so.6", RTLD_NODELETE);
    
    // RTLD_NOLOAD - 不加載，只檢查是否已加載
    handle = dlopen("libm.so.6", RTLD_NOLOAD);
    if (handle) {
        printf("libm.so.6 is already loaded\n");
    }
    
    // RTLD_DEEPBIND - 優先使用庫自己的符號
    handle = dlopen("./mylib.so", RTLD_DEEPBIND);
}

void test_dladdr() {
    Dl_info info;
    void *addr = (void *)printf;  // 使用 printf 函數地址
    
    if (dladdr(addr, &info)) {
        printf("Function: %s\n", info.dli_sname);
        printf("Library: %s\n", info.dli_fname);
        printf("Base address: %p\n", info.dli_fbase);
        printf("Symbol address: %p\n", info.dli_saddr);
    }
}

void test_dlinfo() {
    void *handle = dlopen("libm.so.6", RTLD_LAZY);
    if (!handle) return;
    
    // 獲取鏈接映射
    struct link_map *lm;
    if (dlinfo(handle, RTLD_DI_LINKMAP, &lm) == 0) {
        printf("Library path: %s\n", lm->l_name);
        printf("Base address: %p\n", (void *)lm->l_addr);
    }
    
    // 獲取 TLS 模塊 ID
    size_t tls_modid;
    if (dlinfo(handle, RTLD_DI_TLS_MODID, &tls_modid) == 0) {
        printf("TLS module ID: %zu\n", tls_modid);
    }
    
    dlclose(handle);
}

// 使用 dlvsym 獲取特定版本的符號
void test_dlvsym() {
    void *handle = dlopen(LIBC_SO, RTLD_LAZY);
    if (!handle) return;
    
    // 獲取特定版本的 memcpy
    void *(*memcpy_2_2_5)(void *, const void *, size_t);
    memcpy_2_2_5 = dlvsym(handle, "memcpy", "GLIBC_2.2.5");
    
    if (memcpy_2_2_5) {
        printf("Found memcpy@GLIBC_2.2.5 at %p\n", memcpy_2_2_5);
    }
    
    dlclose(handle);
}

int main() {
    printf("=== Testing dlopen advanced features ===\n\n");
    
    printf("Testing dlopen flags:\n");
    test_dlopen_flags();
    
    printf("\nTesting dladdr:\n");
    test_dladdr();
    
    printf("\nTesting dlinfo:\n");
    test_dlinfo();
    
    printf("\nTesting dlvsym:\n");
    test_dlvsym();
    
    return 0;
}
```

### 混合使用靜態和動態庫

```c
// hybrid_example.c
#include <stdio.h>
#include <dlfcn.h>

// 靜態鏈接的函數（來自 libutils.a）
extern double calculate_area(double radius);

// 動態鏈接的函數（來自 libdynamic.so）
extern void public_function();

// 運行時加載的函數（使用 dlopen）
typedef int (*plugin_func_t)(int);

int main() {
    printf("=== Hybrid Linking Example ===\n");
    
    // 1. 使用靜態鏈接的函數
    double area = calculate_area(5.0);
    printf("Static lib - Circle area: %.2f\n", area);
    
    // 2. 使用動態鏈接的函數
    printf("Dynamic lib - ");
    public_function();
    
    // 3. 使用 dlopen 加載的函數
    void *plugin = dlopen("./plugin.so", RTLD_LAZY);
    if (plugin) {
        plugin_func_t func = dlsym(plugin, "process");
        if (func) {
            int result = func(42);
            printf("Plugin result: %d\n", result);
        }
        dlclose(plugin);
    }
    
    return 0;
}
```

編譯：
```bash
# 編譯混合程序
gcc -c hybrid_example.c -o hybrid_example.o

# 鏈接靜態庫和動態庫
gcc hybrid_example.o \
    -L. -Wl,-Bstatic -lutils \     # 強制靜態鏈接 libutils
    -Wl,-Bdynamic -ldynamic \       # 動態鏈接 libdynamic
    -ldl -lm \                      # 系統庫
    -o hybrid_program

# 或者使用混合方式
gcc hybrid_example.c \
    ./libutils.a \                  # 直接指定靜態庫
    -L. -ldynamic \                  # 動態庫
    -ldl -lm \
    -Wl,-rpath,. \
    -o hybrid_program

# 驗證鏈接
ldd hybrid_program               # 只顯示動態庫
nm hybrid_program | grep calculate_area  # 靜態符號已嵌入
```

### 庫的調試和分析

```bash
#!/bin/bash
# analyze_library.sh

analyze_lib() {
    local lib=$1
    echo "=== Analyzing $lib ==="
    
    # 判斷庫類型
    if [[ $lib == *.a ]]; then
        echo "Static library detected"
        ar -t $lib
        echo -e "\nSymbols:"
        nm -C $lib | head -20
    elif [[ $lib == *.so* ]]; then
        echo "Shared library detected"
        
        # 基本信息
        file $lib
        
        # 依賴
        echo -e "\nDependencies:"
        ldd $lib 2>/dev/null || echo "Not executable"
        
        # SONAME
        echo -e "\nSONAME:"
        readelf -d $lib | grep SONAME
        
        # 導出符號
        echo -e "\nExported symbols (first 10):"
        nm -D -C $lib | grep " T " | head -10
        
        # 版本信息
        echo -e "\nVersion info:"
        readelf -V $lib | grep -A5 "Version symbols"
        
        # 構造/析構函數
        echo -e "\nConstructors/Destructors:"
        readelf -d $lib | grep -E "(INIT|FINI)"
        
        # 安全特性
        echo -e "\nSecurity features:"
        readelf -d $lib | grep -E "(BIND_NOW|RELRO)"
    fi
}

# 使用範例
analyze_lib "$1"
```

### 庫路徑調試技巧

```bash
# 調試庫搜索路徑
LD_DEBUG=libs ./program 2>&1 | grep "searching"

# 查看當前系統的庫搜索路徑
ldconfig -v 2>/dev/null | grep -v "^$" | grep "^/"

# 查看程序的 rpath/runpath
readelf -d program | grep -E "(RPATH|RUNPATH)"
chrpath -l program  # 需要安裝 chrpath

# 修改 rpath
chrpath -r /new/path program
patchelf --set-rpath /new/path program

# 查看當前進程的庫映射
cat /proc/$/maps | grep ".so"

# 預載入庫的順序測試
LD_PRELOAD="lib1.so lib2.so" LD_DEBUG=files ./program 2>&1 | grep "calling init"
```

### 完整 C++ 分析範例

```cpp
// demo.cpp
#include <iostream>
#include <vector>
#include <dlfcn.h>
#include <cmath>

class Calculator {
private:
    std::vector<double> history;
    
public:
    double add(double a, double b) {
        double result = a + b;
        history.push_back(result);
        return result;
    }
    
    void printHistory() {
        for (auto val : history) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }
};

extern "C" void exported_function() {
    std::cout << "This is an exported C function\n";
}

int main() {
    Calculator calc;
    
    // 使用類
    double result = calc.add(3.14, 2.86);
    std::cout << "Result: " << result << std::endl;
    calc.printHistory();
    
    // 動態載入
    void* handle = dlopen("libm.so.6", RTLD_LAZY);
    if (handle) {
        typedef double (*sqrt_func)(double);
        sqrt_func mysqrt = (sqrt_func)dlsym(handle, "sqrt");
        if (mysqrt) {
            std::cout << "sqrt(16) = " << mysqrt(16) << std::endl;
        }
        dlclose(handle);
    }
    
    exported_function();
    
    return 0;
}
```

#### 編譯和分析腳本
```bash
#!/bin/bash
# analyze.sh

# 編譯
echo "=== 編譯程序 ==="
g++ -o demo demo.cpp -ldl -g -O2
g++ -shared -fPIC -o libdemo.so demo.cpp -ldl

# 基本信息
echo -e "\n=== 文件類型 ==="
file demo

echo -e "\n=== 節區大小 ==="
size demo

# ELF 分析
echo -e "\n=== ELF Headers ==="
readelf -h demo | head -20

echo -e "\n=== Program Headers ==="
readelf -l demo | grep -A5 "LOAD"

echo -e "\n=== 動態段 ==="
readelf -d demo

# 符號分析
echo -e "\n=== 導出的 C++ 符號 (demangled) ==="
nm -C demo | grep " T " | head -10

echo -e "\n=== 導出的 C 符號 ==="
nm demo | grep "exported_function"

echo -e "\n=== 未定義符號 ==="
nm -u demo | head -10

# 依賴分析
echo -e "\n=== 共享庫依賴 ==="
ldd demo
ldd -u demo 2>/dev/null

# 字串分析
echo -e "\n=== 程序中的字串 ==="
strings demo | grep -E "(Result|sqrt|History)" | head -5

# 安全特性
echo -e "\n=== 安全特性檢查 ==="
checksec --file=demo 2>/dev/null || {
    echo "RELRO: $(readelf -l demo | grep GNU_RELRO)"
    echo "Stack: $(readelf -s demo | grep -q __stack_chk && echo "Canary found" || echo "No canary")"
    echo "NX: $(readelf -l demo | grep GNU_STACK | grep -q "RW" && echo "NX enabled" || echo "NX disabled")"
    echo "PIE: $(readelf -h demo | grep -q "DYN" && echo "PIE enabled" || echo "No PIE")"
}

# 反彙編主要函數
echo -e "\n=== main 函數反彙編 (前20行) ==="
objdump -d demo | sed -n '/<main>:/,/^$/p' | head -20

# 動態分析準備
echo -e "\n=== 準備動態分析 ==="
echo "strace -c ./demo                  # 系統調用統計"
echo "ltrace -c ./demo                  # 庫調用統計"
echo "LD_DEBUG=bindings ./demo 2>&1     # 符號綁定"
echo "valgrind --leak-check=full ./demo # 內存檢查"
```

### Rust 二進制分析範例

```rust
// main.rs
use std::ffi::{CString, c_void};
use std::ptr;
use std::collections::HashMap;

#[link(name = "m")]
extern "C" {
    fn sqrt(x: f64) -> f64;
    fn cos(x: f64) -> f64;
}

#[no_mangle]
pub extern "C" fn rust_exported_function(x: i32) -> i32 {
    println!("Called from C with value: {}", x);
    x * 2
}

struct DataProcessor {
    cache: HashMap<String, f64>,
}

impl DataProcessor {
    fn new() -> Self {
        DataProcessor {
            cache: HashMap::new(),
        }
    }
    
    fn process(&mut self, key: &str, value: f64) -> f64 {
        let result = unsafe { sqrt(value) + cos(value) };
        self.cache.insert(key.to_string(), result);
        result
    }
}

fn main() {
    println!("Rust Binary Analysis Demo");
    
    let mut processor = DataProcessor::new();
    let result = processor.process("test", 16.0);
    println!("Processed result: {}", result);
    
    // 動態載入
    unsafe {
        let lib = CString::new("libdl.so.2").unwrap();
        let handle = libc::dlopen(lib.as_ptr(), libc::RTLD_LAZY);
        if !handle.is_null() {
            println!("Successfully loaded libdl");
            libc::dlclose(handle);
        }
    }
    
    // 調用導出函數
    let doubled = rust_exported_function(21);
    println!("Doubled: {}", doubled);
}

// 添加 libc 依賴來使用 dlopen
mod libc {
    use std::ffi::c_void;
    pub const RTLD_LAZY: i32 = 1;
    
    extern "C" {
        pub fn dlopen(filename: *const i8, flag: i32) -> *mut c_void;
        pub fn dlclose(handle: *mut c_void) -> i32;
    }
}
```

#### Rust 分析腳本
```bash
#!/bin/bash
# analyze_rust.sh

# 編譯
echo "=== 編譯 Rust 程序 ==="
rustc -O -C debuginfo=2 main.rs -o rust_demo
rustc --crate-type=cdylib main.rs -o librust_demo.so

# Rust 特定分析
echo -e "\n=== Rust 符號 (未 mangle) ==="
nm rust_demo | grep "rust_exported_function"

echo -e "\n=== Rust 符號 (demangled) ==="
nm rust_demo | rustfilt | grep -E "(DataProcessor|process)" | head -5

echo -e "\n=== Rust 字串 ==="
strings rust_demo | grep "Rust Binary"

# 檢查 panic 處理
echo -e "\n=== Panic 處理 ==="
nm rust_demo | grep -E "panic|unwind" | head -5

# 查看 Rust 特定節區
echo -e "\n=== Rust 元數據 ==="
objdump -s -j .rodata rust_demo | head -20
```

### 動態鏈接除錯範例

```c
// ld_debug_test.c
#include <stdio.h>
#include <dlfcn.h>
#include <gnu/lib-names.h>

void test_dlopen() {
    printf("Testing dlopen...\n");
    
    // 嘗試載入多個庫
    const char* libs[] = {
        LIBM_SO,        // "libm.so.6"
        "libpthread.so.0",
        "libdl.so.2",
        "nonexistent.so"
    };
    
    for (int i = 0; i < 4; i++) {
        void* handle = dlopen(libs[i], RTLD_LAZY);
        if (handle) {
            printf("Successfully loaded: %s\n", libs[i]);
            
            // 查詢符號
            if (i == 0) {  // libm
                double (*sqrt_fn)(double) = dlsym(handle, "sqrt");
                if (sqrt_fn) {
                    printf("  sqrt(144) = %f\n", sqrt_fn(144));
                }
            }
            
            dlclose(handle);
        } else {
            printf("Failed to load %s: %s\n", libs[i], dlerror());
        }
    }
}

int main() {
    printf("=== Dynamic Linking Debug Test ===\n");
    test_dlopen();
    return 0;
}
```

#### LD_DEBUG 測試腳本
```bash
#!/bin/bash
# test_ld_debug.sh

# 編譯
gcc -o ld_test ld_debug_test.c -ldl

echo "=== 1. 庫搜索路徑 ==="
LD_DEBUG=libs ./ld_test 2>&1 | grep "searching"

echo -e "\n=== 2. 文件載入 ==="
LD_DEBUG=files ./ld_test 2>&1 | grep "calling init"

echo -e "\n=== 3. 符號綁定 ==="
LD_DEBUG=bindings ./ld_test 2>&1 | grep "binding.*sqrt"

echo -e "\n=== 4. 版本信息 ==="
LD_DEBUG=versions ./ld_test 2>&1 | head -20

echo -e "\n=== 5. 統計信息 ==="
LD_DEBUG=statistics ./ld_test 2>&1

echo -e "\n=== 6. 自定義路徑測試 ==="
mkdir -p /tmp/testlib
cp /lib/x86_64-linux-gnu/libm.so.6 /tmp/testlib/
LD_LIBRARY_PATH=/tmp/testlib LD_DEBUG=libs ./ld_test 2>&1 | grep testlib
```

### 綜合分析工具鏈

```bash
#!/bin/bash
# comprehensive_analysis.sh

analyze_binary() {
    local binary=$1
    local output_dir="analysis_$(basename $binary)"
    
    mkdir -p $output_dir
    
    echo "Analyzing $binary..."
    
    # 靜態分析
    file $binary > $output_dir/file_type.txt
    readelf -a $binary > $output_dir/readelf_all.txt
    objdump -d $binary > $output_dir/disassembly.txt
    nm -C $binary > $output_dir/symbols.txt
    strings -n 10 $binary > $output_dir/strings.txt
    ldd $binary > $output_dir/dependencies.txt 2>&1
    
    # 安全檢查
    checksec --file=$binary > $output_dir/security.txt 2>&1
    
    # 動態分析（需要運行）
    if [[ -x $binary ]]; then
        timeout 5 strace -c $binary > $output_dir/strace_stats.txt 2>&1
        timeout 5 ltrace -c $binary > $output_dir/ltrace_stats.txt 2>&1
        LD_DEBUG=statistics timeout 5 $binary > $output_dir/ld_stats.txt 2>&1
    fi
    
    # 生成報告
    cat > $output_dir/report.md << EOF
# Binary Analysis Report: $(basename $binary)

## Basic Information
\`\`\`
$(file $binary)
$(size $binary)
\`\`\`

## Dependencies
\`\`\`
$(ldd $binary 2>&1)
\`\`\`

## Security Features
\`\`\`
$(checksec --file=$binary 2>&1 | grep -E "RELRO|STACK|NX|PIE|RPATH|FORTIFY" || echo "checksec not available")
\`\`\`

## Exported Symbols (Top 10)
\`\`\`
$(nm -C $binary | grep " T " | head -10)
\`\`\`

## Interesting Strings
\`\`\`
$(strings $binary | grep -E "(error|warning|password|token|key|secret)" | head -10)
\`\`\`

## Analysis Files Generated
- readelf_all.txt: Complete ELF analysis
- disassembly.txt: Full disassembly
- symbols.txt: All symbols (demangled)
- strings.txt: All strings (min length 10)
- dependencies.txt: Library dependencies
- security.txt: Security features check

EOF
    
    echo "Analysis complete. Results in $output_dir/"
}

# 使用範例
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <binary_file>"
    echo "Example: $0 /usr/bin/ls"
    exit 1
fi

analyze_binary "$1"
```

## 進階技巧和提示

### 1. 符號版本控制
```bash
# 查看符號版本
readelf -V /lib/x86_64-linux-gnu/libc.so.6

# 創建版本腳本
cat > version.script << EOF
VERSION_1.0 {
    global:
        exported_function_v1;
    local:
        *;
};

VERSION_2.0 {
    global:
        exported_function_v2;
} VERSION_1.0;
EOF

gcc -shared -Wl,--version-script=version.script -o lib.so lib.c
```

### 2. GOT/PLT 分析
```bash
# 查看 GOT (Global Offset Table)
objdump -R program | grep JUMP_SLOT
readelf -r program | grep PLT

# 查看 PLT (Procedure Linkage Table)
objdump -d -j .plt program
objdump -d -j .plt.got program

# GOT 內容
gdb program
(gdb) info got
(gdb) x/10gx &_GLOBAL_OFFSET_TABLE_
```

### 3. RPATH vs RUNPATH
```bash
# 設置 RPATH (舊方式，優先級高於 LD_LIBRARY_PATH)
gcc -Wl,-rpath,/custom/lib program.c

# 設置 RUNPATH (新方式，優先級低於 LD_LIBRARY_PATH)
gcc -Wl,-rpath,/custom/lib -Wl,--enable-new-dtags program.c

# 查看
readelf -d program | grep -E 'RPATH|RUNPATH'
```

### 4. 弱符號處理
```c
// weak_symbol.c
#include <stdio.h>

// 弱符號定義
__attribute__((weak)) void optional_function() {
    printf("Default implementation\n");
}

// 弱引用
extern void another_function() __attribute__((weak));

int main() {
    optional_function();
    
    if (another_function) {
        another_function();
    } else {
        printf("another_function not available\n");
    }
    return 0;
}
```

### 5. 構造函數/析構函數
```c
// constructor.c
#include <stdio.h>

__attribute__((constructor(101))) void init1() {
    printf("Constructor 1 (priority 101)\n");
}

__attribute__((constructor(100))) void init2() {
    printf("Constructor 2 (priority 100)\n");
}

__attribute__((destructor)) void cleanup() {
    printf("Destructor\n");
}

int main() {
    printf("Main function\n");
    return 0;
}
```

## 常見問題診斷

### 1. "undefined symbol" 錯誤
```bash
# 診斷步驟
ldd -r program                    # 查看未解析符號
nm -u program                      # 列出未定義符號
LD_DEBUG=symbols ./program 2>&1   # 追蹤符號解析

# 查找符號所在庫
for lib in /lib/x86_64-linux-gnu/*.so*; do
    nm -D "$lib" 2>/dev/null | grep -q "symbol_name" && echo "$lib"
done
```

### 2. "version `GLIBC_X.XX' not found" 錯誤
```bash
# 檢查 glibc 版本
ldd --version
strings /lib/x86_64-linux-gnu/libc.so.6 | grep GLIBC_

# 查看程序需要的版本
readelf -V program | grep GLIBC

# 解決方案：使用 patchelf 降低版本要求（危險）
patchelf --replace-needed libc.so.6 libc.so.6.old program
```

### 3. 性能問題診斷
```bash
# CPU 分析
perf record -g ./program
perf report

# 內存分析
valgrind --tool=massif ./program
ms_print massif.out.*

# 系統調用開銷
strace -c ./program

# 庫調用開銷
ltrace -c ./program
```

## 最佳實踐

1. **安全編譯選項**
```bash
gcc -Wall -Wextra -Werror \
    -D_FORTIFY_SOURCE=2 \
    -fstack-protector-strong \
    -fPIE -pie \
    -Wl,-z,relro -Wl,-z,now \
    -o program program.c
```

2. **調試信息分離**
```bash
# 編譯帶調試信息
gcc -g -o program program.c

# 分離調試信息
objcopy --only-keep-debug program program.debug
strip --strip-debug program
objcopy --add-gnu-debuglink=program.debug program
```

3. **靜態分析工作流**
```bash
# 自動化分析腳本
for binary in "$@"; do
    echo "=== $binary ==="
    file "$binary"
    ldd "$binary" 2>&1
    checksec --file="$binary" 2>&1
    nm -C "$binary" | grep " T " | wc -l
    echo
done
```

## 參考資源

- [ELF Specification](https://refspecs.linuxfoundation.org/elf/elf.pdf)
- [Linux man pages](https://man7.org/linux/man-pages/)
- [GNU Binutils Documentation](https://sourceware.org/binutils/docs/)
- [LD.SO(8) Manual](https://man7.org/linux/man-pages/man8/ld.so.8.html)
- [Linker and Libraries Guide](https://docs.oracle.com/cd/E19683-01/816-1386/index.html)

---

**Note**: 本指南涵蓋了 Linux 二進制分析的主要工具和技術。建議根據具體需求選擇合適的工具組合使用。