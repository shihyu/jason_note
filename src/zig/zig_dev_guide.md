# Zig 開發環境完整指南

## 目錄
- [1. 安裝 Zig](#1-安裝-zig)
- [2. 編輯器配置](#2-編輯器配置)
- [3. 專案結構](#3-專案結構)
- [4. 建置系統](#4-建置系統)
- [5. 常用命令](#5-常用命令)
- [6. 實用工具](#6-實用工具)
- [7. 學習資源](#7-學習資源)
- [8. 快速開始](#8-快速開始)

---

## 1. 安裝 Zig

### 方法一：官網下載（推薦）

訪問 https://ziglang.org/download/

```bash
# 下載並解壓（以 Linux 為例）
wget https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz
tar xf zig-linux-x86_64-0.13.0.tar.xz

# 移動到工具目錄
mv zig-linux-x86_64-0.13.0 ~/.mybin/zig-0.13.0

# 加入 PATH（在 .bashrc 或 .zshrc）
export PATH="$HOME/.mybin/zig-0.13.0:$PATH"

# 重新載入
source ~/.bashrc
```

### 方法二：套件管理器

```bash
# Ubuntu/Debian (snap)
sudo snap install zig --classic --beta

# macOS (Homebrew)
brew install zig

# Arch Linux
sudo pacman -S zig
```

### 方法三：使用 zigup（版本管理器）

```bash
# 安裝 zigup
curl https://github.com/marler8997/zigup/releases/latest/download/zigup-$(uname -m)-linux -o zigup
chmod +x zigup
sudo mv zigup /usr/local/bin/

# 使用 zigup 安裝不同版本
zigup 0.13.0          # 穩定版
zigup master          # 最新開發版
zigup 0.16.0-dev      # 特定開發版本
```

### 驗證安裝

```bash
zig version
zig zen  # 顯示 Zig 的設計哲學
```

### 版本選擇建議

- **0.13.0**：最新穩定版，推薦用於生產環境
- **0.16.0-dev**：開發版本，API 可能變動，適合體驗新功能
- **master**：最新主線，每日更新

---

## 2. 編輯器配置

### Neovim 配置

#### 安裝 ZLS（Zig Language Server）

```bash
# 方法一：從源碼編譯
git clone https://github.com/zigtools/zls
cd zls
zig build -Doptimize=ReleaseSafe
# 二進制文件在 zig-out/bin/zls

# 方法二：下載預編譯版本
# 訪問 https://github.com/zigtools/zls/releases
```

#### Neovim 插件配置（使用 lazy.nvim）

```lua
-- plugins/zig.lua

return {
    -- Zig 語法高亮
    {
        'ziglang/zig.vim',
        ft = 'zig',
    },

    -- LSP 配置
    {
        'neovim/nvim-lspconfig',
        config = function()
            local lspconfig = require('lspconfig')
            
            -- Zig LSP 配置
            lspconfig.zls.setup({
                cmd = { vim.fn.expand('~/.local/bin/zls') },  -- 替換成你的 zls 路徑
                filetypes = { 'zig', 'zir' },
                root_dir = lspconfig.util.root_pattern('build.zig', '.git'),
                settings = {
                    zls = {
                        enable_snippets = true,
                        enable_ast_check_diagnostics = true,
                        enable_autofix = true,
                        enable_import_embedfile_argument_completions = true,
                    }
                }
            })
        end
    },

    -- 自動補全（可選）
    {
        'hrsh7th/nvim-cmp',
        dependencies = {
            'hrsh7th/cmp-nvim-lsp',
            'L3MON4D3/LuaSnip',
        },
    }
}
```

#### Zig 專用快捷鍵配置

```lua
-- 檔案類型偵測
vim.filetype.add({
    extension = {
        zig = 'zig',
        zir = 'zir',
        zon = 'zon',
    }
})

-- Zig 快捷鍵
local keymap = vim.keymap.set

-- 格式化
keymap('n', '<leader>zf', ':!zig fmt %<CR>', { desc = 'Format Zig file' })

-- 測試
keymap('n', '<leader>zt', ':!zig test %<CR>', { desc = 'Test Zig file' })

-- AST 檢查
keymap('n', '<leader>za', ':!zig ast-check %<CR>', { desc = 'AST check' })
```

#### 編譯和執行配置

```lua
-- 在你現有的編譯函數中加入
vim.cmd([[
function! Compile_gcc()
    if &filetype=="c"
        set autochdir
        execute "w"
        execute "!gcc -Wall -pedantic -g -O0 -std=gnu99 % -o %:r -lm -pthread"
    elseif &filetype=="cpp"
        set autochdir
        execute "w"
        execute "!g++ -Wall -Wextra -g -std=c++17 -pthread % -o %:r"
    elseif &filetype=="rust"
        set autochdir
        execute "w"
        execute "!rustc -C debuginfo=2 --edition 2024 %:r.rs"
    elseif &filetype=="zig"
        set autochdir
        execute "w"
        execute "!zig build-exe %"
    endif
endfunction
]])

vim.cmd([[
function! Run_gcc()
    if &filetype=="c" || &filetype=="cpp" || &filetype=="rust" || &filetype=="zig"
        set autochdir
        execute "! ./%:r"
    elseif &filetype=="python"
        set autochdir
        execute "w !python"
    endif
endfunction
]])

keymap('n', '<C-x><C-x>', ':call Compile_gcc()<CR>')
keymap('n', '<C-r><C-r>', ':call Run_gcc()<CR>')
```

### VS Code

安裝擴充套件：
- **Zig Language**（官方）
- 會自動下載和配置 zls

### 其他編輯器

- **Emacs**: `zig-mode`
- **Sublime Text**: Zig 語法支援
- **Vim**: `ziglang/zig.vim`

---

## 3. 專案結構

### 單檔案程式

```
hello.zig
```

直接編譯執行：
```bash
zig run hello.zig
# 或
zig build-exe hello.zig
./hello
```

### 標準專案結構（使用 zig init）

```
my-project/
├── build.zig          # 建置腳本
├── build.zig.zon      # 依賴管理（Zig 0.11+）
├── src/
│   ├── main.zig       # 主程式入口
│   └── root.zig       # 函式庫根模組
└── zig-out/           # 輸出目錄（自動生成）
    └── bin/
```

### 初始化專案

```bash
# 建立專案目錄
mkdir my-project && cd my-project

# 初始化（Zig 0.11+ 只有一個命令）
zig init

# 建置並執行
zig build run

# 執行測試
zig build test
```

### 複雜專案結構範例

```
my-project/
├── build.zig
├── build.zig.zon
├── src/
│   ├── main.zig
│   ├── lib/
│   │   ├── parser.zig
│   │   └── utils.zig
│   └── tests/
│       └── parser_test.zig
├── examples/
│   └── demo.zig
└── README.md
```

---

## 4. 建置系統

### 基本 build.zig 範例

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // 建立執行檔
    const exe = b.addExecutable(.{
        .name = "my-app",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);

    // 執行命令
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());

    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);

    // 測試
    const unit_tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&b.addRunArtifact(unit_tests).step);
}
```

### 常用建置命令

```bash
# 建置專案（預設 Debug 模式）
zig build

# 執行
zig build run

# 執行測試
zig build test

# 清理建置檔案
rm -rf zig-cache zig-out

# 指定優化等級
zig build -Doptimize=Debug         # 除錯模式（預設）
zig build -Doptimize=ReleaseFast   # 速度優先
zig build -Doptimize=ReleaseSmall  # 大小優先
zig build -Doptimize=ReleaseSafe   # 安全檢查 + 優化

# 交叉編譯
zig build -Dtarget=x86_64-windows
zig build -Dtarget=x86_64-macos
zig build -Dtarget=aarch64-linux
zig build -Dtarget=wasm32-wasi

# 查看所有可用的建置選項
zig build --help
```

---

## 5. 常用命令

### 編譯相關

```bash
# 編譯成執行檔
zig build-exe main.zig

# 編譯成靜態函式庫
zig build-lib mylib.zig

# 編譯成動態函式庫
zig build-lib mylib.zig -dynamic

# 編譯成物件檔
zig build-obj mycode.zig

# 直接執行（編譯並執行）
zig run main.zig

# 執行並傳入參數
zig run main.zig -- arg1 arg2
```

### 測試相關

```bash
# 執行測試
zig test main.zig

# 執行專案測試
zig build test

# 執行單一測試（使用過濾器）
zig test main.zig --test-filter "test_name"
```

### 格式化和檢查

```bash
# 格式化單一檔案
zig fmt main.zig

# 格式化整個目錄
zig fmt src/

# 格式化並檢查（不修改檔案）
zig fmt --check src/

# AST 語法檢查（不編譯）
zig ast-check main.zig
```

### 其他工具

```bash
# 顯示 Zig 的設計哲學
zig zen

# 翻譯 C 程式碼到 Zig
zig translate-c file.c > file.zig

# 編譯 C 程式（使用 Zig 作為 C 編譯器）
zig cc -o output main.c

# 編譯 C++ 程式
zig c++ -o output main.cpp

# 查看標準庫文件
zig std

# 查看完整幫助
zig --help
```

---

## 6. 實用工具

### 除錯工具

```bash
# 使用 GDB
gdb ./zig-out/bin/my-app

# 使用 LLDB
lldb ./zig-out/bin/my-app

# Valgrind（記憶體檢查）
valgrind ./zig-out/bin/my-app

# 使用 Zig 內建的 AddressSanitizer
zig build -Doptimize=Debug -fsanitize=address
```

### 效能分析

```bash
# 使用 perf
perf record ./zig-out/bin/my-app
perf report

# 使用 time
time ./zig-out/bin/my-app

# Zig 內建 benchmark
zig test --test-cmd-bin src/benchmark.zig
```

### 交叉編譯目標查詢

```bash
# 查看所有支援的目標平台
zig targets

# 輸出 JSON 格式
zig targets | jq
```

---

## 7. 學習資源

### 官方資源

- **官網**: https://ziglang.org/
- **語言參考**: https://ziglang.org/documentation/master/
- **標準庫文件**: https://ziglang.org/documentation/master/std/
- **GitHub**: https://github.com/ziglang/zig

### 學習教材

- **Ziglings**: https://github.com/ratfactor/ziglings  
  互動式練習，類似 Rustlings

- **Zig Learn**: https://ziglearn.org/  
  完整的學習指南

- **Zig Guide**: https://zig.guide/  
  社群維護的指南

- **Zig by Example**: https://zig-by-example.com/  
  實例學習

### 進階資源

- **Zig 標準庫原始碼**: 閱讀 `~/.mybin/zig-x.x.x/lib/std/`
- **Awesome Zig**: https://github.com/nrdmn/awesome-zig  
  精選的 Zig 資源列表

### 社群

- **Discord**: https://discord.gg/zig
- **Reddit**: r/Zig
- **Forum**: https://ziggit.dev/
- **中文社群**: 搜尋 "Zig 中文社區"

---

## 8. 快速開始

### Hello World

#### 方法一：單檔案（適合 Zig 0.11-0.15）

```zig
const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, World!\n", .{});
}
```

```bash
zig run hello.zig
```

#### 方法二：單檔案（適合 Zig 0.16+ 開發版）

```zig
const std = @import("std");

pub fn main() void {
    std.debug.print("Hello, World!\n", .{});
}
```

```bash
zig run hello.zig
```

#### 方法三：完整專案

```bash
# 1. 建立專案
mkdir hello-zig && cd hello-zig

# 2. 初始化
zig init

# 3. 編輯 src/main.zig
cat > src/main.zig << 'EOF'
const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, Zig!\n", .{});
}
EOF

# 4. 建置並執行
zig build run
```

### 基本語法範例

```zig
const std = @import("std");

// 常數
const PI: f32 = 3.14159;

// 函數
fn add(a: i32, b: i32) i32 {
    return a + b;
}

// 錯誤處理
fn divide(a: f32, b: f32) !f32 {
    if (b == 0) return error.DivisionByZero;
    return a / b;
}

// 測試
test "basic math" {
    try std.testing.expectEqual(@as(i32, 5), add(2, 3));
}

pub fn main() !void {
    const result = try divide(10, 2);
    std.debug.print("Result: {d}\n", .{result});
}
```

### 執行測試

```bash
zig test example.zig
```

---

## 附錄：版本差異說明

### Zig 0.13.0（穩定版）vs Zig 0.16.0-dev（開發版）

| 功能 | 0.13.0 | 0.16.0-dev |
|------|--------|------------|
| 標準輸出 | `std.io.getStdOut()` | `std.io.getStdOut()` 或 `std.debug.print()` |
| 專案初始化 | `zig init` | `zig init` |
| 建置檔案 | `b.path()` | `b.path()` |
| API 穩定性 | ✅ 穩定 | ⚠️ 可能變動 |

**建議**：
- 生產環境使用 **0.13.0** 穩定版
- 學習和實驗可以使用開發版體驗新特性
- 使用 `zigup` 管理多個版本

---

## 常見問題

### Q: 編譯錯誤 "std has no member named 'io'"

A: 這通常出現在 Zig 0.16+ 開發版。使用 `std.debug.print()` 代替 `std.io.getStdOut()`。

### Q: 如何選擇優化等級？

A:
- **Debug**: 開發時使用，包含完整除錯資訊
- **ReleaseSafe**: 生產環境，保留安全檢查
- **ReleaseFast**: 需要最高效能時
- **ReleaseSmall**: 需要最小二進制大小時

### Q: 如何管理依賴？

A: 使用 `build.zig.zon` 檔案（Zig 0.11+）。範例：

```zig
.{
    .name = "my-project",
    .version = "0.1.0",
    .dependencies = .{
        .@"some-package" = .{
            .url = "https://github.com/user/package/archive/tag.tar.gz",
            .hash = "...",
        },
    },
}
```

---

## 結語

Zig 是一個現代、高效的系統程式語言，適合用於：
- 系統程式開發
- 嵌入式開發
- 遊戲開發
- 作為更好的 C/C++ 替代方案

開始你的 Zig 之旅吧！🚀

**最後更新**: 2025-10-20