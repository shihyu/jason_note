# GDB Script 斷點打印後自動繼續的技巧解析

## 🎯 核心技巧

這個腳本實現「斷點命中→打印訊息→自動繼續」的關鍵技巧在於：

### 1. **斷點命令配置 (Breakpoint Commands)**

```python
# 關鍵代碼在這裡
def configure_breakpoints():
    for bp in gdb.breakpoints():
        if bp.number > 1:
            # 這行是核心！為每個斷點設置自動執行的命令
            bp.commands = "silent\nshow_full_location\ncontinue"
            # 或簡化版本
            # bp.commands = "continue"
```

## 📖 技術原理詳解

### 斷點命令的執行流程

當斷點被命中時，GDB 會：
1. **暫停程式執行**
2. **執行預設的命令序列**
3. **根據命令決定下一步動作**

```gdb
# 命令序列解析
silent              # 1. 抑制預設的斷點命中訊息
show_full_location  # 2. 執行自定義函數，打印調試資訊
continue           # 3. 自動繼續執行程式
```

### 關鍵命令說明

| 命令 | 作用 | 效果 |
|------|------|------|
| `silent` | 靜默模式 | 不顯示「Breakpoint X hit」訊息 |
| `continue` | 繼續執行 | 程式自動繼續，不等待用戶輸入 |
| 自定義函數 | 執行特定操作 | 在繼續前執行任何需要的動作 |

## 🔧 實現方式比較

### 方式一：使用 GDB Commands（傳統方式）

```gdb
# 為特定斷點設置命令
break main
commands 2  # 2 是斷點編號
  silent
  printf "Hit main function\n"
  backtrace 1
  continue
end
```

### 方式二：使用 Python API（腳本採用的方式）

```python
import gdb

# 更靈活的方式
for bp in gdb.breakpoints():
    bp.commands = """
        silent
        python print(f"⚡ Hit: {gdb.selected_frame().name()}")
        continue
    """
```

### 方式三：定義斷點類（進階方式）

```python
class AutoContinueBreakpoint(gdb.Breakpoint):
    def __init__(self, spec):
        super().__init__(spec, gdb.BP_BREAKPOINT)
        
    def stop(self):
        # 返回 False 表示不停止，自動繼續
        frame = gdb.selected_frame()
        print(f"📍 Passing through: {frame.name()}")
        return False  # 這是關鍵！False = 繼續執行
```

## 💡 核心技巧總結

### 1. **批量配置的優勢**

```python
# 腳本的聰明之處：一次配置所有斷點
configured_count = 0
for bp in gdb.breakpoints():
    if bp.number > 1:  # 跳過 catchpoint
        bp.commands = "continue"
        configured_count += 1
```

### 2. **動態載入時機**

```gdb
# 等待動態庫載入後才設置斷點
catch load libintiface_engine_flutter_bridge.so
commands 1
    source breakpoints.txt  # 載入斷點
    python configure_breakpoints()  # 批量配置
    continue
end
```

## 🎨 實用範例

### 簡單的追蹤腳本

```gdb
# trace.gdb - 最簡追蹤腳本
define setup_trace
    # 設置斷點
    break process_message
    break handle_error
    
    # 配置自動繼續
    python
for bp in gdb.breakpoints():
    bp.commands = """
        silent
        echo ===
        where 1
        continue
    """
    end
end

# 使用
setup_trace
run
```

### 帶條件的智能斷點

```python
class ConditionalTracer(gdb.Breakpoint):
    def __init__(self, spec, condition_func):
        super().__init__(spec)
        self.condition_func = condition_func
        
    def stop(self):
        # 根據條件決定是否打印
        if self.condition_func():
            print(f"⚠️ Condition met at {self.location}")
            # 可以選擇停止或繼續
            return False  # 打印後繼續
        return False  # 直接繼續

# 使用範例
def check_error():
    # 檢查是否有錯誤
    return gdb.parse_and_eval("error_code") != 0

bp = ConditionalTracer("process_data", check_error)
```

### 計數型斷點

```python
class CountingBreakpoint(gdb.Breakpoint):
    def __init__(self, spec, threshold=10):
        super().__init__(spec)
        self.count = 0
        self.threshold = threshold
        
    def stop(self):
        self.count += 1
        if self.count % self.threshold == 0:
            print(f"📊 {self.location} hit {self.count} times")
        return False  # 永遠不停止

# 每10次打印一次統計
bp = CountingBreakpoint("hot_function", 10)
```

## ⚡ 效能考量

### 斷點開銷比較

```python
# 最小開銷版本
bp.commands = "continue"

# 中等開銷版本
bp.commands = """
    silent
    printf "."
    continue
"""

# 高開銷版本
bp.commands = """
    silent
    python complex_analysis()
    backtrace
    info locals
    continue
"""
```

### 選擇性追蹤優化

```python
class OptimizedTracer(gdb.Breakpoint):
    def __init__(self, spec):
        super().__init__(spec)
        self.sample_rate = 100  # 每100次採樣一次
        self.counter = 0
        
    def stop(self):
        self.counter += 1
        if self.counter % self.sample_rate == 0:
            self.detailed_analysis()
        return False
    
    def detailed_analysis(self):
        # 只在採樣時執行昂貴操作
        frame = gdb.selected_frame()
        print(f"📈 Sample #{self.counter}: {frame.name()}")
```

## 🛠️ 進階調試技巧

### 1. 動態開關追蹤

```python
# 全局控制
class TraceControl:
    enabled = True
    verbose = False
    filters = []

class SmartBreakpoint(gdb.Breakpoint):
    def stop(self):
        if not TraceControl.enabled:
            return False
            
        frame_name = gdb.selected_frame().name()
        
        # 應用過濾器
        if TraceControl.filters:
            if not any(f in frame_name for f in TraceControl.filters):
                return False
        
        # 詳細或簡單輸出
        if TraceControl.verbose:
            self.detailed_trace()
        else:
            print(".", end="", flush=True)
            
        return False

# 運行時控制
(gdb) python TraceControl.enabled = False
(gdb) python TraceControl.filters = ["engine", "core"]
(gdb) python TraceControl.verbose = True
```

### 2. 時間戳追蹤

```python
import time

class TimedBreakpoint(gdb.Breakpoint):
    def __init__(self, spec):
        super().__init__(spec)
        self.last_hit = None
        
    def stop(self):
        now = time.time()
        if self.last_hit:
            delta = now - self.last_hit
            if delta > 0.1:  # 只記錄超過100ms的間隔
                print(f"⏱️ {self.location}: {delta:.3f}s since last hit")
        self.last_hit = now
        return False
```

### 3. 堆疊深度追蹤

```python
class StackDepthTracer(gdb.Breakpoint):
    def __init__(self, spec):
        super().__init__(spec)
        self.max_depth = 0
        
    def stop(self):
        depth = len(gdb.newest_frame().older())
        if depth > self.max_depth:
            self.max_depth = depth
            print(f"📏 New max stack depth: {depth} at {self.location}")
        return False
```

## 📊 完整工作流程圖

```
程式啟動
    ↓
動態庫載入檢測 (catch load)
    ↓
觸發載入事件
    ↓
執行載入命令序列
    ├─→ 載入斷點檔案 (source breakpoints.txt)
    ├─→ 批量配置斷點 (Python configure_breakpoints)
    └─→ 繼續執行 (continue)
         ↓
    ┌────────┐
    │ 程式   │
    │ 執行   │←──────┐
    └────────┘       │
         ↓           │
    遇到斷點         │
         ↓           │
    GDB 暫停         │
         ↓           │
    執行 bp.commands │
         ├─→ silent  │
         ├─→ 自定義  │
         └─→ continue┘
```

## 🔍 除錯斷點命令

### 測試單一斷點

```gdb
# 手動測試
(gdb) break test_function
Breakpoint 2 at 0x4005c0: file test.c, line 10.

(gdb) commands 2
Type commands for breakpoint(s) 2, one per line.
End with a line saying just "end".
> silent
> printf "Test: hit breakpoint\n"
> continue
> end

(gdb) run
Test: hit breakpoint
[程式繼續執行...]
```

### 檢查斷點配置

```python
# 顯示所有斷點的命令
python
for bp in gdb.breakpoints():
    print(f"Breakpoint {bp.number}:")
    print(f"  Location: {bp.location}")
    print(f"  Commands: {bp.commands}")
    print(f"  Enabled: {bp.enabled}")
end
```

## 🎓 最佳實踐

### 1. **分層追蹤策略**

```python
# 不同層級的追蹤
class LayeredTracer:
    CRITICAL = 1
    INFO = 2
    DEBUG = 3
    
    level = INFO
    
    @classmethod
    def trace(cls, level, message):
        if level <= cls.level:
            print(message)

class SmartBreakpoint(gdb.Breakpoint):
    def __init__(self, spec, level=LayeredTracer.INFO):
        super().__init__(spec)
        self.level = level
        
    def stop(self):
        LayeredTracer.trace(
            self.level,
            f"[{self.level}] {self.location}"
        )
        return False
```

### 2. **錯誤恢復機制**

```python
class SafeBreakpoint(gdb.Breakpoint):
    def stop(self):
        try:
            # 執行可能出錯的操作
            self.analyze()
        except Exception as e:
            print(f"❌ Error in breakpoint: {e}")
        finally:
            # 確保程式繼續執行
            return False
```

### 3. **資源管理**

```python
class ResourceAwareBreakpoint(gdb.Breakpoint):
    def __init__(self, spec, max_logs=1000):
        super().__init__(spec)
        self.logs = []
        self.max_logs = max_logs
        
    def stop(self):
        # 防止記憶體無限增長
        if len(self.logs) >= self.max_logs:
            self.logs.pop(0)
        
        self.logs.append({
            'time': time.time(),
            'frame': gdb.selected_frame().name()
        })
        
        return False
```

## 💾 輸出到檔案

```python
class FileTracer(gdb.Breakpoint):
    def __init__(self, spec, filename="/tmp/trace.log"):
        super().__init__(spec)
        self.file = open(filename, "a")
        
    def stop(self):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        frame = gdb.selected_frame()
        self.file.write(f"{timestamp} - {frame.name()}\n")
        self.file.flush()  # 確保即時寫入
        return False
        
    def __del__(self):
        if hasattr(self, 'file'):
            self.file.close()
```

## 📚 相關資源

- [GDB Python API 文檔](https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html)
- [GDB 斷點命令文檔](https://sourceware.org/gdb/current/onlinedocs/gdb/Break-Commands.html)
- [高級 GDB 腳本技術](https://interrupt.memfault.com/blog/advanced-gdb)

## 🎯 關鍵要點總結

1. **核心機制**：使用 `bp.commands = "continue"` 實現自動繼續
2. **靈活性**：Python API 提供比傳統 GDB 命令更強大的控制
3. **效能**：注意斷點命令的開銷，高頻斷點使用簡單命令
4. **可靠性**：使用異常處理確保調試不影響程式執行
5. **可擴展**：透過類繼承和組合實現複雜的追蹤邏輯

這個技巧將 GDB 從互動式調試器轉變為強大的自動化追蹤和分析工具！