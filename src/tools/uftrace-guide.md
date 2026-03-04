# uftrace 使用指南

`uftrace` 是 Linux 上相當實用的函式追蹤工具，適合用來觀察程式的呼叫路徑、執行時間、函式參數與回傳值。對 C、C++ 這類需要做函式級分析的情境特別好用。

官方資源：

- 原始碼：<https://github.com/namhyung/uftrace>
- 文件目錄：<https://github.com/namhyung/uftrace/tree/master/doc>

## 1. 安裝

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install uftrace
```

### CentOS / RHEL

```bash
sudo yum install uftrace

# 較新的發行版可改用 dnf
sudo dnf install uftrace
```

### 從原始碼編譯

```bash
git clone https://github.com/namhyung/uftrace.git
cd uftrace
make
sudo make install
```

## 2. 使用前準備

`uftrace` 通常需要搭配編譯期插樁資訊，常見作法如下：

```bash
gcc -pg -o program source.c

# 或者
gcc -finstrument-functions -o program source.c
```

若你要分析的程式比較複雜，建議保留除錯資訊，後續輸出會比較好讀：

```bash
gcc -g -pg -o program source.c
```

## 3. 基本工作流程

### 3.1 記錄執行軌跡

```bash
# 基本用法
uftrace record ./your_program

# 指定輸出目錄
uftrace record -d trace_data ./your_program

# 記錄函式參數
uftrace record -A main ./your_program
```

### 3.2 重播追蹤結果

```bash
# 直接重播
uftrace replay

# 從指定目錄讀取
uftrace replay -d trace_data

# 顯示函式參數與回傳值
uftrace replay -A main -R main
```

### 3.3 產生報表與呼叫圖

```bash
# 函式統計報表
uftrace report

# 依呼叫次數與總耗時排序
uftrace report -s call,total

# 顯示呼叫關係
uftrace graph
```

## 4. 常用選項

### 4.1 `record` 常見參數

```bash
# 限制追蹤深度
uftrace record -D 5 ./program

# 只追蹤特定函式
uftrace record -F main,func1,func2 ./program

# 排除雜訊函式
uftrace record -N printf,malloc,free ./program

# 只記錄耗時超過 1ms 的函式
uftrace record -t 1ms ./program

# 記錄核心函式
sudo uftrace record -k ./program

# 記錄回傳值
uftrace record -R func_name ./program
```

### 4.2 `replay` 常見參數

```bash
# 顯示時間戳
uftrace replay -t

# 顯示耗時
uftrace replay -T

# 僅顯示指定函式
uftrace replay -F main,important_func

# 顯示參數與回傳值
uftrace replay -A main -R main
```

## 5. 實作範例

### 5.1 範例程式

```c
#include <stdio.h>
#include <unistd.h>

void func_c(void) {
    printf("In function C\n");
    usleep(1000);
}

void func_b(void) {
    printf("In function B\n");
    usleep(2000);
    func_c();
}

void func_a(void) {
    printf("In function A\n");
    usleep(3000);
    func_b();
}

int main(void) {
    printf("Starting program\n");
    func_a();
    printf("Program finished\n");
    return 0;
}
```

### 5.2 編譯與追蹤

```bash
gcc -g -pg -o test test.c
uftrace record ./test
uftrace replay
```

### 5.3 輸出範例

```text
# DURATION     TID     FUNCTION
            [  1234] | main() {
   3.000 ms [  1234] |   func_a() {
   2.000 ms [  1234] |     func_b() {
   1.000 ms [  1234] |       func_c();
   2.000 ms [  1234] |     } /* func_b */
   3.000 ms [  1234] |   } /* func_a */
            [  1234] | } /* main */
```

## 6. 進階功能

### 6.1 使用腳本自訂分析

```bash
uftrace script -S analyze.py
```

```python
def uftrace_entry(ctx):
    print(f"進入: {ctx['name']}，時間戳: {ctx['timestamp']}")


def uftrace_exit(ctx):
    print(f"離開: {ctx['name']}，耗時: {ctx['duration']}")
```

### 6.2 匯出 Chrome Trace

```bash
uftrace dump --chrome > trace.json
```

之後可在 Chromium / Chrome 的追蹤檢視工具中載入 `trace.json` 進行視覺化分析。

![uftrace 的 Chrome Trace 視覺化畫面](images/uftrace-chrome.png)

### 6.3 匯出 Graphviz 呼叫圖

```bash
uftrace graph --graphviz | dot -Tpng -o callgraph.png
```

### 6.4 產生 Flame Graph 資料

```bash
uftrace dump --flame-graph > flamegraph.txt
./flamegraph.pl flamegraph.txt > flamegraph.svg
```

## 7. 除錯與調整技巧

### 7.1 過濾雜訊函式

```bash
uftrace record -N "malloc,free,printf,puts" ./program
uftrace record -F "main,func*" ./program
```

### 7.2 設定合理門檻

```bash
# 只觀察耗時超過 100us 的函式
uftrace record -t 100us ./program
```

### 7.3 控制追蹤資料量

```bash
uftrace record --max-stack 100M ./program
uftrace record -t 1ms -D 10 ./program
```

## 8. 常見問題

### 8.1 看不到函式呼叫

通常是因為編譯時沒有加上 `-pg` 或 `-finstrument-functions`。

```bash
gcc -g -pg -o program source.c
```

### 8.2 追蹤核心函式失敗

這類操作通常需要 `root` 權限：

```bash
sudo uftrace record -k ./program
```

### 8.3 想把預設參數固定下來

可建立 `~/.uftrace`：

```ini
record = -t 100us -D 20
replay = -T -t
```

## 9. 與其他工具比較

| 工具 | 優勢 | 適用情境 |
| --- | --- | --- |
| `uftrace` | 函式層級追蹤細節完整，能看呼叫關係 | 函式耗時分析、呼叫鏈追蹤 |
| `strace` | 系統呼叫層級觀察清楚 | 系統互動、I/O 問題排查 |
| `perf` | CPU 取樣與硬體事件分析能力強 | 整體效能瓶頸分析 |
| `gprof` | 傳統插樁式效能分析 | 舊專案或基本函式統計 |

## 10. 小結

如果你想知道「哪個函式被誰呼叫、花了多久、順序是什麼」，`uftrace` 會比單純的取樣式工具更直觀。它特別適合拿來理解大型 C / C++ 程式的執行路徑，也能和 Chrome Trace、Graphviz、Flame Graph 一起搭配使用。
