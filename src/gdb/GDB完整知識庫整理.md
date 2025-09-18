# GDB 完整知識庫整理

## 目錄

- [第一部分：GDB 基礎與安裝](#第一部分gdb-基礎與安裝)
- [第二部分：GDB 常用指令](#第二部分gdb-常用指令)
- [第三部分：GDB 程式追蹤與調試](#第三部分gdb-程式追蹤與調試)
- [第四部分：GDB 自動化與腳本](#第四部分gdb-自動化與腳本)
- [第五部分：特定語言調試](#第五部分特定語言調試)
- [第六部分：進階功能](#第六部分進階功能)
- [第七部分：特殊平台調試](#第七部分特殊平台調試)
- [第八部分：實用工具與專案](#第八部分實用工具與專案)

---

## 第一部分：GDB 基礎與安裝

### GDB 編譯與安裝

#### 基本編譯步驟
```sh
sudo apt-get install libgmp-dev libmpfr-dev

git clone https://github.com/bminor/binutils-gdb

../configure --enable-targets=all \
--prefix=/home/shihyu/.mybin/gdb

make -j8 && make install
```

#### 編譯 GDB 7.9 with Python 支援
```sh
sudo apt-get install texinfo libncurses-dev libreadline-dev python-dev

# 修改 gdb/remote.c 解決 'g' packet reply is too long 問題
# 屏蔽 process_g_packet 函數中的錯誤檢查並添加動態調整程式碼

# 使用 Anaconda Python
export LDFLAGS="-Wl,-rpath,/home/shihyu/anaconda3/lib -L/home/shihyu/anaconda3/lib"

../configure --enable-targets=all \
             --enable-64-bit-bfd  \
             --with-python=python3.7 \
             --with-system-readline \
             --prefix=/home/shihyu/.mybin/gdb8.3_python3

make && make install
```

---

## 第二部分：GDB 常用指令

### 記憶體檢視指令 (examine)

格式：`x /nfu <address>`

參數說明：
- **n**：要顯示的內存單元個數
- **f**：顯示格式
  - x：十六進制
  - d：十進制
  - u：無符號十進制
  - o：八進制
  - t：二進制
  - a：地址格式
  - i：指令格式
  - c：字符格式
  - f：浮點數格式
- **u**：單元長度
  - b：單字節
  - h：雙字節
  - w：四字節
  - g：八字節

### 基本調試指令

#### 斷點設置
```gdb
break main              # 在 main 函數設置斷點
break file.c:100       # 在指定檔案的行號設置斷點
break function_name    # 在函數入口設置斷點
info breakpoints       # 查看所有斷點
delete 1               # 刪除斷點編號 1
```

#### 執行控制
```gdb
run                    # 開始執行程式
continue              # 繼續執行
step                  # 單步執行（進入函數）
next                  # 單步執行（不進入函數）
finish                # 執行到當前函數返回
```

#### 變數與記憶體檢視
```gdb
print variable        # 打印變數值
print *pointer       # 打印指標指向的值
info locals          # 查看局部變數
info args           # 查看函數參數
display variable    # 每次停止時顯示變數
```

#### 堆疊操作
```gdb
backtrace           # 顯示函數調用堆疊
frame n             # 切換到第 n 個堆疊框架
up                  # 向上移動堆疊框架
down                # 向下移動堆疊框架
```

### GDB Dashboard 與增強工具

- **GDB Dashboard**：https://github.com/cyrus-and/gdb-dashboard
- **Gdbinit for OS X/iOS**：https://github.com/gdbinit/Gdbinit
- **dotgdb**：https://github.com/dholm/dotgdb

---

## 第三部分：GDB 程式追蹤與調試

### 方法一：基本 GDB 命令追蹤

```bash
# 編譯程式（加入除錯資訊）
gcc -g -o demo demo.c

# 啟動 GDB 並設定記錄
gdb ./demo

(gdb) set logging enabled on
(gdb) set logging file basic_trace.txt
(gdb) set trace-commands on

# 設置斷點
(gdb) break main
(gdb) break calculate

# 設定自動命令
(gdb) commands 1-2
> silent
> printf "=== Function: "
> where 1
> info args
> info locals
> continue
> end

# 執行程式
(gdb) run
```

### 方法二：使用 Python 腳本自動追蹤

```bash
# 啟動 GDB 並載入腳本
gdb ./demo
(gdb) source trace.py
(gdb) trace-start
(gdb) run
(gdb) trace-stop
```

### 方法三：記錄/重播功能

```bash
gdb ./demo
(gdb) start
(gdb) record              # 開啟記錄
(gdb) continue
(gdb) reverse-continue    # 反向執行
(gdb) reverse-step       # 反向單步
(gdb) info record        # 查看記錄資訊
```

### Watchpoint 使用指南

#### 基本語法
```gdb
watch <expression>         # 當表達式值改變時中斷
rwatch <expression>       # 當表達式被讀取時中斷
awatch <expression>       # 當表達式被讀或寫時中斷
```

#### 實際範例
```gdb
watch counter             # 監控變數 counter
watch ptr->value         # 監控結構體成員
watch array[5]           # 監控陣列元素
watch *(int*)0x12345678  # 監控特定記憶體地址
```

---

## 第四部分：GDB 自動化與腳本

### GDB 命令行參數

#### 四種執行腳本的方法

1. **使用 `-x` 參數**
```bash
gdb -x script.gdb ./program
```

2. **使用 `--command` 參數**
```bash
gdb --command=script.gdb ./program
```

3. **使用 `-ex` 執行單個命令**
```bash
gdb -ex "break main" -ex "run" ./program
```

4. **使用 `--eval-command`**
```bash
gdb --eval-command="break main" --eval-command="run" ./program
```

### Commands 腳本語法

#### 基本結構
```gdb
commands [breakpoint-number]
  silent                  # 不顯示斷點訊息
  # 你的命令
  printf "Variable: %d\n", variable
  continue               # 自動繼續執行
end
```

#### 進階範例
```gdb
# 追蹤函數調用
define trace_function
  commands $arg0
    silent
    printf "[%s] called with args: ", $arg1
    info args
    continue
  end
end
```

### 函數調用追蹤與流程圖生成

#### 創建追蹤腳本
```gdb
# trace.gdb
set pagination off
set logging file trace.log
set logging on

define hook-stop
  where 1
  info args
end

break function1
break function2
commands 1-2
  silent
  continue
end

run
```

#### 生成調用圖
```python
# 解析追蹤日誌生成 DOT 格式
def parse_trace_to_dot(trace_file):
    with open(trace_file) as f:
        lines = f.readlines()
    # 處理邏輯...
    generate_dot_file(calls)
```

---

## 第五部分：特定語言調試

### Rust 調試

#### 編譯與調試
```bash
# 編譯 Rust 程式（包含除錯資訊）
rustc -C debuginfo=2 test.rs

# 或使用 cargo
cargo build --debug
```

#### Rust GDB 特殊命令
```gdb
# 打印 Rust 字串
print string_var

# 查看 Vec 內容
print vec_var.buf.ptr.pointer

# 查看 Option 類型
print option_var
```

#### Rust 調試範例
```rust
trait Printable {
    fn print(&self);
}

struct Point {
    x: i32,
    y: i32,
}

impl Printable for Point {
    fn print(&self) {
        println!("({}, {})", self.x, self.y);
    }
}

fn main() {
    let list = vec![Point { x: 1, y: 2 }, Point { x: 3, y: 4 }];
    // 設置斷點調試
}
```

### Go 語言調試

#### Go 程式編譯
```bash
# 關閉優化，保留除錯資訊
go build -gcflags="-N -l" main.go
```

#### Go GDB 命令
```gdb
# 查看 goroutine
info goroutines

# 切換 goroutine
goroutine 2 bt

# 打印 Go 字串
print string_var
```

#### Go 測試範例
```go
package main

import "fmt"

func add(a, b int) int {
    result := a + b
    fmt.Printf("Adding %d + %d = %d\n", a, b, result)
    return result
}

func main() {
    fmt.Println("=== Go GDB Debug Test ===")
    result := add(5, 3)
    fmt.Printf("Result: %d\n", result)
}
```

---

## 第六部分：進階功能

### 動態庫分析 (.so 檔案)

#### 查看動態庫資訊
```gdb
info sharedlibrary        # 列出載入的動態庫
sharedlibrary libname    # 載入符號資訊
```

#### 設置動態庫斷點
```gdb
# 在動態庫函數設置斷點
break libname.so:function_name

# 設置延遲斷點
set breakpoint pending on
break function_in_so
```

### JeMalloc 記憶體調試

#### 編譯時啟用 JeMalloc
```bash
gcc -g -o app app.c -ljemalloc
```

#### GDB 中分析 JeMalloc
```gdb
# 查看記憶體統計
call je_malloc_stats_print(NULL, NULL, NULL)

# 設置環境變數
set environment MALLOC_CONF=stats_print:true
```

### 圖形化調用關係

#### 生成調用圖工具
- 使用 `gdb_graphs` 專案生成可視化調用圖
- 輸出 DOT 格式，可用 Graphviz 渲染

```bash
# 生成調用追蹤
gdb -x trace_calls.gdb ./program

# 轉換為圖形
python parse_trace.py trace.log > calls.dot
dot -Tpng calls.dot -o calls.png
```

---

## 第七部分：特殊平台調試

### QEMU + GDB 調試 RISC-V Linux Kernel

#### 環境準備
```bash
# 安裝必要套件
sudo apt install \
    git \
    autoconf \
    automake \
    autotools-dev \
    ninja-build \
    build-essential \
    libmpc-dev \
    libmpfr-dev \
    libgmp-dev \
    libglib2.0-dev \
    libpixman-1-dev
```

#### 編譯 RISC-V 工具鏈
```bash
git clone https://github.com/riscv/riscv-gnu-toolchain
cd riscv-gnu-toolchain
./configure --prefix=/opt/riscv
make linux
```

#### QEMU 調試 Kernel
```bash
# 啟動 QEMU（等待 GDB 連接）
qemu-system-riscv64 \
    -machine virt \
    -kernel linux/arch/riscv/boot/Image \
    -s -S

# 另一終端啟動 GDB
riscv64-linux-gnu-gdb vmlinux
(gdb) target remote :1234
(gdb) break start_kernel
(gdb) continue
```

---

## 第八部分：實用工具與專案

### GDB Tracer 工具

位於 `src/gdb-tracer/` 的追蹤工具，支援：
- 自動函數調用追蹤
- 生成執行流程報告
- 支援 Rust 程式調試

### GDB Trace Python 工具

位於 `src/gdb_trace_python_src/` 的 Python 增強工具：
- 自動化追蹤腳本
- 日誌解析與分析
- 調用關係視覺化

### 可點擊調用圖生成器

位於 `src/GDB_GenerateClickbleCallGraph-/` 的工具：
- 生成互動式 HTML 調用圖
- 支援函數跳轉導航
- 程式碼覆蓋率分析

### Rust GDB 範例專案

位於 `src/rust-gdb-example/` 的完整範例：
- Rust 程式調試最佳實踐
- 常見問題與解決方案
- 性能分析範例

---

## 附錄：快速參考卡

### 最常用命令速查

| 命令 | 簡寫 | 說明 |
|------|------|------|
| break | b | 設置斷點 |
| run | r | 執行程式 |
| continue | c | 繼續執行 |
| next | n | 單步執行（跳過函數）|
| step | s | 單步執行（進入函數）|
| print | p | 打印變數 |
| backtrace | bt | 顯示調用堆疊 |
| quit | q | 退出 GDB |
| info | i | 顯示資訊 |
| list | l | 顯示原始碼 |

### 環境設定建議

```bash
# ~/.gdbinit 設定檔
set history save on
set history size 1000
set print pretty on
set print array on
set print array-indexes on
set pagination off
```

### 調試技巧總結

1. **使用條件斷點**：`break file.c:100 if variable == 5`
2. **自動化重複任務**：使用 commands 和 define
3. **保存調試會話**：`save breakpoints file.bp`
4. **遠端調試**：`target remote hostname:port`
5. **核心轉儲分析**：`gdb program core.dump`

---

## 參考資源

- [GDB 官方文檔](https://www.gnu.org/software/gdb/documentation/)
- [GDB Dashboard](https://github.com/cyrus-and/gdb-dashboard)
- [Rust GDB 範例](https://github.com/zupzup/rust-gdb-example)
- [RISC-V 調試指南](https://blog.csdn.net/m0_43422086/article/details/125276723)

---

*本文檔整理自 GDB 相關知識庫，涵蓋基礎到進階的完整調試技術。*