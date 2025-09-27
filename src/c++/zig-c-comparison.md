# Zig vs C 語言完整比較指南

## 目錄
1. [語言概述](#語言概述)
2. [核心特性比較](#核心特性比較)
3. [語法比較](#語法比較)
4. [記憶體管理](#記憶體管理)
5. [錯誤處理](#錯誤處理)
6. [編譯時特性](#編譯時特性)
7. [標準函式庫](#標準函式庫)
8. [實際範例對比](#實際範例對比)

## 語言概述

### C 語言
- **發布年份**: 1972年
- **設計者**: Dennis Ritchie
- **設計理念**: 系統程式設計、可移植性、效率
- **主要用途**: 作業系統、嵌入式系統、系統軟體

### Zig 語言
- **發布年份**: 2016年
- **設計者**: Andrew Kelley
- **設計理念**: 取代 C 的現代系統程式語言，更安全、更簡單
- **主要用途**: 系統程式設計、嵌入式開發、WebAssembly

## 核心特性比較

| 特性 | C 語言 | Zig 語言 |
|------|--------|----------|
| **記憶體安全** | 手動管理，容易出錯 | 手動管理但有更多安全檢查 |
| **空指標** | 允許，常見錯誤來源 | 可選類型（Optional Types） |
| **錯誤處理** | 返回錯誤碼或 errno | 內建錯誤處理機制 |
| **預處理器** | 有（#define, #include） | 無，使用編譯時執行 |
| **標頭檔** | 需要 .h 檔案 | 不需要標頭檔 |
| **泛型程式設計** | 透過巨集或 void* | 編譯時泛型 |
| **編譯時執行** | 有限（巨集） | 完整的編譯時執行 |
| **未定義行為** | 大量存在 | 明確定義所有行為 |
| **交叉編譯** | 需要工具鏈 | 內建交叉編譯支援 |
| **C 相容性** | N/A | 可直接導入 C 程式碼 |

## 語法比較

### 1. 基本程式結構

**C 語言：**
```c
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

**Zig 語言：**
```zig
const std = @import("std");

pub fn main() void {
    std.debug.print("Hello, World!\n", .{});
}
```

### 2. 變數宣告

**C 語言：**
```c
int x = 10;           // 可變變數
const int y = 20;     // 常數
int *ptr = &x;        // 指標
```

**Zig 語言：**
```zig
var x: i32 = 10;      // 可變變數
const y: i32 = 20;    // 編譯時常數
var ptr: *i32 = &x;   // 指標
```

### 3. 資料型別

| C 型別 | Zig 型別 | 說明 |
|--------|----------|------|
| `char` | `u8` 或 `i8` | 8位元整數 |
| `short` | `i16` | 16位元有號整數 |
| `int` | `c_int` 或 `i32` | 32位元有號整數 |
| `long` | `c_long` 或 `i64` | 64位元有號整數 |
| `float` | `f32` | 32位元浮點數 |
| `double` | `f64` | 64位元浮點數 |
| `void*` | `*anyopaque` | 不透明指標 |
| `NULL` | `null` | 空值 |

### 4. 函式定義

**C 語言：**
```c
int add(int a, int b) {
    return a + b;
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
```

**Zig 語言：**
```zig
fn add(a: i32, b: i32) i32 {
    return a + b;
}

fn swap(a: *i32, b: *i32) void {
    const temp = a.*;
    a.* = b.*;
    b.* = temp;
}
```

### 5. 條件判斷

**C 語言：**
```c
if (x > 0) {
    printf("Positive\n");
} else if (x < 0) {
    printf("Negative\n");
} else {
    printf("Zero\n");
}

// 三元運算子
int result = (x > 0) ? 1 : -1;

// Switch
switch (x) {
    case 1:
        printf("One\n");
        break;
    case 2:
        printf("Two\n");
        break;
    default:
        printf("Other\n");
}
```

**Zig 語言：**
```zig
if (x > 0) {
    std.debug.print("Positive\n", .{});
} else if (x < 0) {
    std.debug.print("Negative\n", .{});
} else {
    std.debug.print("Zero\n", .{});
}

// if 表達式
const result = if (x > 0) 1 else -1;

// Switch
switch (x) {
    1 => std.debug.print("One\n", .{}),
    2 => std.debug.print("Two\n", .{}),
    else => std.debug.print("Other\n", .{}),
}
```

### 6. 迴圈

**C 語言：**
```c
// for 迴圈
for (int i = 0; i < 10; i++) {
    printf("%d ", i);
}

// while 迴圈
int i = 0;
while (i < 10) {
    printf("%d ", i);
    i++;
}

// do-while 迴圈
do {
    printf("%d ", i);
    i++;
} while (i < 10);
```

**Zig 語言：**
```zig
// for 迴圈（範圍）
for (0..10) |i| {
    std.debug.print("{} ", .{i});
}

// for 迴圈（陣列）
const array = [_]i32{1, 2, 3, 4, 5};
for (array) |item| {
    std.debug.print("{} ", .{item});
}

// while 迴圈
var i: usize = 0;
while (i < 10) : (i += 1) {
    std.debug.print("{} ", .{i});
}
```

### 7. 結構體

**C 語言：**
```c
struct Point {
    int x;
    int y;
};

struct Point p = {10, 20};
p.x = 30;

typedef struct {
    char name[50];
    int age;
} Person;
```

**Zig 語言：**
```zig
const Point = struct {
    x: i32,
    y: i32,
};

var p = Point{ .x = 10, .y = 20 };
p.x = 30;

const Person = struct {
    name: [50]u8,
    age: i32,
    
    // 可以包含方法
    pub fn greet(self: Person) void {
        std.debug.print("Hello, {s}\n", .{self.name});
    }
};
```

### 8. 列舉

**C 語言：**
```c
enum Color {
    RED,
    GREEN,
    BLUE
};

enum Color c = RED;
```

**Zig 語言：**
```zig
const Color = enum {
    red,
    green,
    blue,
};

var c = Color.red;

// 標籤聯合（Tagged Union）
const Value = union(enum) {
    int: i32,
    float: f32,
    string: []const u8,
};
```

## 記憶體管理

### 動態記憶體分配

**C 語言：**
```c
#include <stdlib.h>

int *arr = (int*)malloc(10 * sizeof(int));
if (arr == NULL) {
    // 處理錯誤
}

// 使用陣列
arr[0] = 42;

free(arr);  // 必須記得釋放
```

**Zig 語言：**
```zig
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    const arr = try allocator.alloc(i32, 10);
    defer allocator.free(arr);  // defer 確保釋放
    
    arr[0] = 42;
}
```

## 錯誤處理

### C 語言的錯誤處理
```c
FILE *file = fopen("test.txt", "r");
if (file == NULL) {
    perror("Error opening file");
    return -1;
}

// 或使用 errno
if (some_function() == -1) {
    if (errno == ENOENT) {
        printf("File not found\n");
    }
}
```

### Zig 語言的錯誤處理
```zig
const file = std.fs.cwd().openFile("test.txt", .{}) catch |err| {
    std.debug.print("Error opening file: {}\n", .{err});
    return err;
};
defer file.close();

// 錯誤聯合類型
fn divide(a: f32, b: f32) !f32 {
    if (b == 0) {
        return error.DivisionByZero;
    }
    return a / b;
}

// 使用 try
const result = try divide(10, 2);
```

## 編譯時特性

### C 語言的預處理器
```c
#define MAX_SIZE 100
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#ifdef DEBUG
    #define LOG(x) printf("%s\n", x)
#else
    #define LOG(x)
#endif
```

### Zig 語言的編譯時執行
```zig
const max_size = 100;  // 編譯時常數

fn min(comptime T: type, a: T, b: T) T {
    return if (a < b) a else b;
}

// 編譯時執行
const fibonacci = comptime blk: {
    var fib: [10]i32 = undefined;
    fib[0] = 0;
    fib[1] = 1;
    var i: usize = 2;
    while (i < 10) : (i += 1) {
        fib[i] = fib[i-1] + fib[i-2];
    }
    break :blk fib;
};

// 條件編譯
const debug = @import("builtin").mode == .Debug;
fn log(msg: []const u8) void {
    if (debug) {
        std.debug.print("{s}\n", .{msg});
    }
}
```

## 標準函式庫

### 字串操作

**C 語言：**
```c
#include <string.h>

char str1[100] = "Hello";
char str2[] = " World";

strcat(str1, str2);        // 串接
int len = strlen(str1);     // 長度
int cmp = strcmp(str1, str2); // 比較
char *copy = strcpy(dest, src); // 複製
```

**Zig 語言：**
```zig
const std = @import("std");

var buffer: [100]u8 = undefined;
const str1 = "Hello";
const str2 = " World";

// 使用 fmt 格式化
const result = try std.fmt.bufPrint(&buffer, "{s}{s}", .{str1, str2});

// 長度
const len = str1.len;

// 比較
const equal = std.mem.eql(u8, str1, str2);

// 複製
std.mem.copy(u8, &buffer, str1);
```

## 實際範例對比

### 範例 1：陣列操作

**C 語言：**
```c
#include <stdio.h>

void print_array(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

int main() {
    int numbers[] = {1, 2, 3, 4, 5};
    int size = sizeof(numbers) / sizeof(numbers[0]);
    
    print_array(numbers, size);
    printf("Sum: %d\n", sum_array(numbers, size));
    
    return 0;
}
```

**Zig 語言：**
```zig
const std = @import("std");

fn printArray(arr: []const i32) void {
    for (arr) |item| {
        std.debug.print("{} ", .{item});
    }
    std.debug.print("\n", .{});
}

fn sumArray(arr: []const i32) i32 {
    var sum: i32 = 0;
    for (arr) |item| {
        sum += item;
    }
    return sum;
}

pub fn main() void {
    const numbers = [_]i32{ 1, 2, 3, 4, 5 };
    
    printArray(&numbers);
    std.debug.print("Sum: {}\n", .{sumArray(&numbers)});
}
```

### 範例 2：鏈結串列

**C 語言：**
```c
#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* next;
};

struct Node* create_node(int data) {
    struct Node* node = (struct Node*)malloc(sizeof(struct Node));
    if (node == NULL) return NULL;
    node->data = data;
    node->next = NULL;
    return node;
}

void free_list(struct Node* head) {
    struct Node* temp;
    while (head != NULL) {
        temp = head;
        head = head->next;
        free(temp);
    }
}
```

**Zig 語言：**
```zig
const std = @import("std");

const Node = struct {
    data: i32,
    next: ?*Node,
    
    fn create(allocator: std.mem.Allocator, data: i32) !*Node {
        const node = try allocator.create(Node);
        node.* = Node{
            .data = data,
            .next = null,
        };
        return node;
    }
    
    fn destroyList(self: *Node, allocator: std.mem.Allocator) void {
        var current: ?*Node = self;
        while (current) |node| {
            const next = node.next;
            allocator.destroy(node);
            current = next;
        }
    }
};
```

## 優缺點總結

### C 語言優點
1. 成熟穩定，生態系統龐大
2. 幾乎所有平台都支援
3. 大量的函式庫和工具
4. 豐富的學習資源
5. 簡單直接的語法

### C 語言缺點
1. 大量未定義行為
2. 手動記憶體管理容易出錯
3. 缺乏現代語言特性
4. 預處理器系統複雜且容易出錯
5. 沒有內建的錯誤處理機制

### Zig 語言優點
1. 沒有未定義行為
2. 優秀的編譯時執行能力
3. 內建錯誤處理機制
4. 更好的型別安全
5. 內建交叉編譯支援
6. 可直接使用 C 程式碼
7. 不需要標頭檔
8. defer 語句確保資源清理

### Zig 語言缺點
1. 相對較新，生態系統較小
2. 文件和學習資源較少
3. 語言仍在發展中（尚未到 1.0 版）
4. IDE 支援不如 C 成熟
5. 社群相對較小

## 遷移建議

### 從 C 遷移到 Zig 的步驟

1. **漸進式遷移**：Zig 可以直接導入和使用 C 程式碼，可以逐步遷移
2. **學習新概念**：重點學習錯誤處理、可選類型、編譯時執行
3. **利用 Zig 的優勢**：使用 defer、錯誤聯合、編譯時驗證
4. **保持 C 相容性**：可以繼續使用現有的 C 函式庫

### 適合使用 Zig 的場景
- 新的系統程式專案
- 需要更好的安全性保證
- 嵌入式系統開發
- WebAssembly 目標
- 需要交叉編譯的專案

### 適合繼續使用 C 的場景
- 維護現有的大型 C 程式碼庫
- 需要最廣泛的平台支援
- 團隊已經熟悉 C
- 依賴特定的 C 工具鏈

## Zig 在 Ubuntu 的安裝與使用

### 安裝方法

#### 方法 1：使用 Snap（最簡單）
```bash
# 安裝最新穩定版
sudo snap install zig --classic

# 安裝開發版
sudo snap install zig --classic --edge
```

#### 方法 2：使用 APT（Ubuntu 22.04+）
```bash
# 更新套件列表
sudo apt update

# 安裝 Zig
sudo apt install zig
```

#### 方法 3：下載預編譯二進位檔（推薦，獲得最新版本）
```bash
# 1. 前往 https://ziglang.org/download/ 下載對應版本
# 或使用 wget 下載（以 0.11.0 為例）
wget https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz

# 2. 解壓縮
tar -xf zig-linux-x86_64-0.11.0.tar.xz

# 3. 移動到適當位置
sudo mv zig-linux-x86_64-0.11.0 /opt/zig

# 4. 加入 PATH（編輯 ~/.bashrc 或 ~/.zshrc）
echo 'export PATH="/opt/zig:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 5. 驗證安裝
zig version
```

#### 方法 4：從原始碼編譯
```bash
# 安裝依賴
sudo apt install cmake g++ make

# 克隆倉庫
git clone https://github.com/ziglang/zig.git
cd zig

# 建立編譯目錄
mkdir build
cd build

# 配置和編譯
cmake ..
make -j$(nproc)

# 安裝
sudo make install
```

### 基本使用指令

#### 1. 建立和執行第一個程式
```bash
# 建立專案目錄
mkdir hello-zig
cd hello-zig

# 建立主程式檔案
cat > main.zig << 'EOF'
const std = @import("std");

pub fn main() void {
    std.debug.print("Hello, Zig!\n", .{});
}
EOF

# 直接執行（開發時使用）
zig run main.zig

# 編譯成執行檔
zig build-exe main.zig

# 執行編譯後的程式
./main
```

#### 2. 編譯選項詳解
```bash
# 基本編譯
zig build-exe main.zig

# 指定輸出檔名
zig build-exe main.zig -femit-bin=myapp

# 優化等級
zig build-exe main.zig -O ReleaseFast    # 最佳效能
zig build-exe main.zig -O ReleaseSafe    # 平衡效能與安全
zig build-exe main.zig -O ReleaseSmall   # 最小體積
zig build-exe main.zig -O Debug          # 偵錯模式（預設）

# 靜態連結（預設）
zig build-exe main.zig

# 動態連結
zig build-exe main.zig -dynamic

# 交叉編譯（編譯給其他平台）
zig build-exe main.zig -target x86_64-windows
zig build-exe main.zig -target aarch64-linux
zig build-exe main.zig -target wasm32-wasi
```

### 使用 Zig 專案建構系統

#### 1. 初始化專案
```bash
# 建立新專案
mkdir myproject
cd myproject

# 初始化 Zig 專案
zig init-exe  # 建立執行檔專案
# 或
zig init-lib  # 建立函式庫專案

# 專案結構
tree
# .
# ├── build.zig       # 建構腳本
# ├── src
# │   └── main.zig    # 主程式
# └── zig-cache/      # 快取目錄（自動生成）
```

#### 2. build.zig 設定檔範例
```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    // 目標平台（null 表示主機平台）
    const target = b.standardTargetOptions(.{});
    
    // 優化模式
    const optimize = b.standardOptimizeOption(.{});
    
    // 建立執行檔
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = .{ .path = "src/main.zig" },
        .target = target,
        .optimize = optimize,
    });
    
    // 安裝執行檔
    b.installArtifact(exe);
    
    // 建立執行命令
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    
    // 加入命令列參數
    if (b.args) |args| {
        run_cmd.addArgs(args);
    }
    
    // 建立 "run" 步驟
    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);
    
    // 加入測試
    const unit_tests = b.addTest(.{
        .root_source_file = .{ .path = "src/main.zig" },
        .target = target,
        .optimize = optimize,
    });
    
    const run_unit_tests = b.addRunArtifact(unit_tests);
    
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_unit_tests.step);
}
```

#### 3. 使用 build.zig 建構專案
```bash
# 編譯專案
zig build

# 編譯並執行
zig build run

# 執行測試
zig build test

# 指定優化等級
zig build -Doptimize=ReleaseFast
zig build -Doptimize=ReleaseSafe
zig build -Doptimize=ReleaseSmall

# 交叉編譯
zig build -Dtarget=x86_64-windows
zig build -Dtarget=aarch64-linux-gnu

# 清理建構
rm -rf zig-cache zig-out
```

### 整合 C 程式碼

#### 1. 在 Zig 中使用 C 函式庫
```zig
// math_wrapper.zig
const c = @cImport({
    @cInclude("math.h");
    @cInclude("stdio.h");
});

pub fn main() void {
    const result = c.sqrt(16.0);
    _ = c.printf("Square root of 16 is: %f\n", result);
}
```

編譯：
```bash
# 編譯包含 C 程式碼的 Zig 程式
zig build-exe math_wrapper.zig -lc
./math_wrapper
```

#### 2. 混合 C 和 Zig 原始碼
```bash
# C 程式碼 (helper.c)
cat > helper.c << 'EOF'
#include <stdio.h>

void say_hello_from_c(const char* name) {
    printf("Hello from C, %s!\n", name);
}
EOF

# C 標頭檔 (helper.h)
cat > helper.h << 'EOF'
void say_hello_from_c(const char* name);
EOF

# Zig 主程式 (main.zig)
cat > main.zig << 'EOF'
const std = @import("std");
const c = @cImport({
    @cInclude("helper.h");
});

pub fn main() void {
    c.say_hello_from_c("Zig User");
    std.debug.print("Hello from Zig!\n", .{});
}
EOF

# 編譯混合專案
zig build-exe main.zig helper.c -lc
./main
```

### 開發環境設定

#### VSCode 設定
```bash
# 安裝 VSCode
sudo snap install code --classic

# 安裝 Zig 擴充套件
code --install-extension ziglang.vscode-zig

# 建立 VSCode 設定檔 (.vscode/settings.json)
mkdir .vscode
cat > .vscode/settings.json << 'EOF'
{
    "zig.buildOnSave": true,
    "zig.formattingProvider": "zls",
    "zig.zls.enableAutofix": true
}
EOF
```

#### 安裝 ZLS (Zig Language Server)
```bash
# 方法 1: 使用預編譯版本
wget https://github.com/zigtools/zls/releases/download/0.11.0/zls-x86_64-linux.tar.gz
tar -xf zls-x86_64-linux.tar.gz
sudo mv zls /usr/local/bin/

# 方法 2: 從原始碼編譯
git clone https://github.com/zigtools/zls
cd zls
zig build -Doptimize=ReleaseSafe
sudo cp zig-out/bin/zls /usr/local/bin/
```

### 常用開發指令

```bash
# 格式化程式碼
zig fmt src/

# 產生文件
zig build-docs

# 執行內建測試
zig test src/main.zig

# 檢查程式碼
zig ast-check src/main.zig

# 顯示建構快取
zig build --verbose-cc

# 清理快取
rm -rf zig-cache zig-out

# 查看 Zig 內建函式
zig builtin

# 查看支援的目標平台
zig targets

# C 程式碼轉換為 Zig
zig translate-c helper.c > helper.zig
```

### 偵錯 Zig 程式

#### 使用 GDB
```bash
# 編譯時加入偵錯資訊
zig build-exe main.zig -O Debug

# 使用 GDB 偵錯
gdb ./main

# GDB 指令
# (gdb) break main           # 設定中斷點
# (gdb) run                  # 執行程式
# (gdb) step                 # 單步執行
# (gdb) print variable_name  # 印出變數
# (gdb) backtrace           # 顯示呼叫堆疊
# (gdb) quit                # 離開
```

#### 使用 LLDB
```bash
# 安裝 LLDB
sudo apt install lldb

# 偵錯
lldb ./main

# LLDB 指令
# (lldb) b main             # 設定中斷點
# (lldb) r                  # 執行
# (lldb) s                  # 單步執行
# (lldb) p variable_name    # 印出變數
# (lldb) bt                 # 顯示呼叫堆疊
```

### 效能分析

```bash
# 使用 Valgrind 檢查記憶體洩漏
sudo apt install valgrind
zig build-exe main.zig -O Debug
valgrind --leak-check=full ./main

# 使用 perf 進行效能分析
sudo apt install linux-tools-generic
zig build-exe main.zig -O ReleaseFast
perf record ./main
perf report
```

### 常見問題解決

#### 1. 版本相容性問題
```bash
# 檢查 Zig 版本
zig version

# 使用特定版本的 Zig
# 下載並管理多個版本，使用符號連結切換
ls -la /opt/zig-*
sudo ln -sf /opt/zig-0.11.0 /opt/zig
```

#### 2. 編譯錯誤除錯
```bash
# 顯示詳細編譯資訊
zig build-exe main.zig --verbose-cc

# 顯示 AST（抽象語法樹）
zig ast-check --ast main.zig
```

#### 3. 記憶體問題除錯
```zig
// 使用 GeneralPurposeAllocator 的除錯模式
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{
        .safety = true,  // 啟用安全檢查
    }){};
    defer {
        const leaked = gpa.deinit();
        if (leaked) {
            std.debug.print("Memory leak detected!\n", .{});
        }
    }
    
    const allocator = gpa.allocator();
    // 使用 allocator...
}
```

## 結論

Zig 是一個現代化的系統程式語言，旨在解決 C 語言的許多問題，同時保持 C 的簡單性和效能。雖然 Zig 還在發展中，但它提供了許多吸引人的特性，特別是在安全性和開發體驗方面。對於新專案，Zig 是一個值得考慮的選擇；對於現有的 C 專案，可以考慮漸進式地引入 Zig。

選擇使用哪種語言應該基於專案需求、團隊經驗和長期維護考量。兩種語言都有其適用的場景，了解它們的差異有助於做出明智的技術決策。