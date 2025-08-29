# Python 效能分析完整指南：從 cProfile 到 py-spy

## 目錄
1. [概述](#概述)
2. [環境設置](#環境設置)
3. [cProfile 模組詳解](#cprofile-模組詳解)
4. [py-spy 進階分析](#py-spy-進階分析)
5. [實戰範例集](#實戰範例集)
6. [效能優化最佳實踐](#效能優化最佳實踐)
7. [常見問題與解決方案](#常見問題與解決方案)

## 概述

Python 雖然執行效率相較於 Go、C 等編譯語言較慢，但其易用性和豐富的生態系統大幅提升了開發效率。在處理效能問題時，正確的分析工具和方法能幫助我們找出真正的瓶頸。

### 為什麼需要效能分析？
- 找出程式中的效能瓶頸
- 驗證優化效果
- 理解程式執行流程
- 發現隱藏的效率問題

## 環境設置

### 安裝必要套件
```bash
# 基礎套件
pip install pandas numpy
pip install snakeviz  # cProfile 視覺化工具
pip install py-spy     # 進階效能分析工具

# 選用套件
pip install memory_profiler  # 記憶體分析
pip install line_profiler    # 逐行分析
pip install guppy3          # 堆積分析
```

### 準備測試資料
```python
# 生成測試資料集
import pandas as pd
import numpy as np

# 建立大型資料集用於測試
def create_test_data(rows=1000000):
    data = {
        'id': range(rows),
        'value': np.random.randn(rows),
        'category': np.random.choice(['A', 'B', 'C', 'D'], rows),
        'timestamp': pd.date_range('2024-01-01', periods=rows, freq='1min')
    }
    df = pd.DataFrame(data)
    df.to_csv('test_data.csv', index=False)
    return df
```

## cProfile 模組詳解

### 基本使用方法

#### 1. 命令列使用
```bash
# 基本分析
python -m cProfile script.py

# 按累積時間排序
python -m cProfile -s cumulative script.py

# 輸出到檔案
python -m cProfile -o profile.stats script.py

# 限制輸出行數
python -m cProfile -s cumulative script.py | head -20
```

#### 2. 程式內使用
```python
import cProfile
import pstats
from pstats import SortKey

def profile_function(func):
    """裝飾器：分析單一函數"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats(SortKey.CUMULATIVE)
        stats.print_stats(10)  # 顯示前 10 個最耗時的函數
        return result
    return wrapper

@profile_function
def my_slow_function():
    # 你的程式碼
    pass
```

### 報表欄位解釋

| 欄位 | 說明 | 重要性 |
|------|------|---------|
| ncalls | 函數呼叫次數 | 高頻呼叫可能是瓶頸 |
| tottime | 函數本身執行時間（不含子函數） | 找出直接耗時的函數 |
| percall | tottime/ncalls | 單次呼叫平均時間 |
| cumtime | 函數總執行時間（含子函數） | 整體耗時評估 |
| filename:lineno(function) | 函數位置 | 定位問題 |

### 視覺化分析 - SnakeViz

```bash
# 生成分析檔案
python -m cProfile -o profile.stats your_script.py

# 使用 SnakeViz 視覺化
snakeviz profile.stats

# 或者在 Jupyter Notebook 中使用
%load_ext snakeviz
%snakeviz your_function()
```

### 進階範例：資料處理效能分析

```python
import cProfile
import pstats
import pandas as pd
import numpy as np
from io import StringIO

class DataProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        
    def load_data(self):
        """載入資料 - 可能的瓶頸點"""
        self.data = pd.read_csv(self.filename)
        
    def process_data(self):
        """處理資料 - 多個潛在效能問題"""
        # 問題 1：使用 iterrows（很慢）
        results = []
        for idx, row in self.data.iterrows():
            if row['value'] > 0:
                results.append(row['id'] * 2)
        
        # 問題 2：重複計算
        for i in range(len(self.data)):
            self.data.loc[i, 'sqrt_value'] = np.sqrt(abs(self.data.loc[i, 'value']))
        
        # 問題 3：低效的字串操作
        self.data['category_upper'] = self.data['category'].apply(lambda x: x.upper())
        
        return results
    
    def optimize_process_data(self):
        """優化後的資料處理"""
        # 優化 1：向量化操作取代迴圈
        mask = self.data['value'] > 0
        results = (self.data.loc[mask, 'id'] * 2).tolist()
        
        # 優化 2：向量化計算
        self.data['sqrt_value'] = np.sqrt(np.abs(self.data['value']))
        
        # 優化 3：使用內建方法
        self.data['category_upper'] = self.data['category'].str.upper()
        
        return results

def compare_performance():
    """比較優化前後的效能"""
    processor = DataProcessor('test_data.csv')
    processor.load_data()
    
    # 分析原始版本
    print("=== 原始版本效能分析 ===")
    profiler1 = cProfile.Profile()
    profiler1.enable()
    processor.process_data()
    profiler1.disable()
    
    s1 = StringIO()
    ps1 = pstats.Stats(profiler1, stream=s1).sort_stats('cumulative')
    ps1.print_stats(10)
    print(s1.getvalue())
    
    # 分析優化版本
    print("\n=== 優化版本效能分析 ===")
    profiler2 = cProfile.Profile()
    profiler2.enable()
    processor.optimize_process_data()
    profiler2.disable()
    
    s2 = StringIO()
    ps2 = pstats.Stats(profiler2, stream=s2).sort_stats('cumulative')
    ps2.print_stats(10)
    print(s2.getvalue())
```

## py-spy 進階分析

### 安裝與基本使用

```bash
# 安裝
pip install py-spy

# macOS 可能需要 sudo
sudo pip install py-spy
```

### 主要功能

#### 1. Record - 生成火焰圖
```bash
# 基本記錄
py-spy record -o profile.svg -- python your_script.py

# 設定採樣率（預設 100Hz）
py-spy record -r 200 -o profile.svg -- python your_script.py

# 記錄執行中的程序
py-spy record -o profile.svg -p PID

# 包含原生擴展
py-spy record --native -o profile.svg -- python your_script.py
```

#### 2. Top - 即時監控
```bash
# 即時顯示最耗時的函數
py-spy top -- python your_script.py

# 監控執行中的程序
py-spy top -p PID
```

#### 3. Dump - 取得呼叫堆疊
```bash
# 取得當前呼叫堆疊
py-spy dump -p PID
```

### 實際範例：Web 應用效能分析

```python
# app.py - Flask 應用範例
from flask import Flask, jsonify
import time
import random
import pandas as pd

app = Flask(__name__)

def slow_database_query():
    """模擬慢速資料庫查詢"""
    time.sleep(random.uniform(0.1, 0.3))
    return pd.DataFrame({
        'id': range(1000),
        'value': [random.random() for _ in range(1000)]
    })

def complex_calculation(df):
    """複雜計算"""
    result = 0
    for _, row in df.iterrows():  # 效能問題：使用 iterrows
        result += row['value'] ** 2
    return result

@app.route('/api/data')
def get_data():
    # 取得資料
    df = slow_database_query()
    
    # 處理資料
    result = complex_calculation(df)
    
    return jsonify({
        'result': result,
        'count': len(df)
    })

if __name__ == '__main__':
    app.run(debug=False)
```

分析方法：
```bash
# 啟動應用並分析
py-spy record -o web_profile.svg -- python app.py &

# 使用 ab 或 wrk 進行壓力測試
ab -n 100 -c 10 http://localhost:5000/api/data

# 或使用 Python 腳本測試
python -c "
import requests
import concurrent.futures

def make_request():
    return requests.get('http://localhost:5000/api/data')

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(make_request) for _ in range(100)]
    concurrent.futures.wait(futures)
"
```

### 多執行緒/多處理程序分析

```python
# multiprocessing_example.py
import multiprocessing
import time
import numpy as np

def cpu_intensive_task(n):
    """CPU 密集型任務"""
    result = 0
    for i in range(n):
        result += np.sqrt(i) * np.sin(i)
    return result

def io_intensive_task(n):
    """I/O 密集型任務"""
    time.sleep(0.1)
    with open(f'temp_{n}.txt', 'w') as f:
        f.write('x' * 1000000)
    time.sleep(0.1)
    
def run_parallel():
    """平行處理範例"""
    with multiprocessing.Pool(processes=4) as pool:
        # CPU 密集型任務
        cpu_results = pool.map(cpu_intensive_task, [1000000] * 4)
        
        # I/O 密集型任務
        io_results = pool.map(io_intensive_task, range(4))
    
    return cpu_results

if __name__ == '__main__':
    results = run_parallel()
    print(f"Results: {results}")
```

分析指令：
```bash
# 分析多處理程序（包含子程序）
py-spy record -s -o multiprocess.svg -- python multiprocessing_example.py
```

## 實戰範例集

### 範例 1：DataFrame 操作優化

```python
import pandas as pd
import numpy as np
import time

def measure_time(func):
    """計時裝飾器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 耗時: {end - start:.4f} 秒")
        return result
    return wrapper

class DataFrameOptimization:
    def __init__(self, size=1000000):
        self.df = pd.DataFrame({
            'A': np.random.randn(size),
            'B': np.random.randn(size),
            'C': np.random.choice(['X', 'Y', 'Z'], size),
            'D': np.random.randint(0, 100, size)
        })
    
    @measure_time
    def slow_method(self):
        """低效方法：逐行處理"""
        results = []
        for idx, row in self.df.iterrows():
            if row['A'] > 0 and row['B'] < 0:
                results.append(row['D'] * 2)
        return results
    
    @measure_time
    def medium_method(self):
        """中等效率：使用 apply"""
        def process_row(row):
            if row['A'] > 0 and row['B'] < 0:
                return row['D'] * 2
            return None
        
        results = self.df.apply(process_row, axis=1)
        return results.dropna().tolist()
    
    @measure_time
    def fast_method(self):
        """高效方法：向量化操作"""
        mask = (self.df['A'] > 0) & (self.df['B'] < 0)
        results = (self.df.loc[mask, 'D'] * 2).tolist()
        return results
    
    @measure_time
    def numpy_method(self):
        """最快方法：使用 NumPy"""
        a_values = self.df['A'].values
        b_values = self.df['B'].values
        d_values = self.df['D'].values
        
        mask = (a_values > 0) & (b_values < 0)
        results = (d_values[mask] * 2).tolist()
        return results

# 執行比較
optimizer = DataFrameOptimization(size=100000)
print("=== DataFrame 操作效能比較 ===")
# optimizer.slow_method()  # 太慢，可能跳過
optimizer.medium_method()
optimizer.fast_method()
optimizer.numpy_method()
```

### 範例 2：記憶體分析

```python
from memory_profiler import profile
import numpy as np
import pandas as pd

@profile
def memory_intensive_function():
    """記憶體密集型函數"""
    # 階段 1：建立大型列表
    big_list = [i for i in range(1000000)]
    
    # 階段 2：轉換為 NumPy 陣列
    np_array = np.array(big_list)
    
    # 階段 3：建立 DataFrame
    df = pd.DataFrame({
        'col1': np_array,
        'col2': np_array * 2,
        'col3': np_array ** 2
    })
    
    # 階段 4：資料處理
    result = df.groupby(df['col1'] % 100).agg({
        'col2': 'sum',
        'col3': 'mean'
    })
    
    return result

# 執行記憶體分析
# python -m memory_profiler your_script.py
```

### 範例 3：快取優化

```python
import functools
import time

def measure_cache_performance():
    """測試快取效能影響"""
    
    # 無快取版本
    def fibonacci_no_cache(n):
        if n <= 1:
            return n
        return fibonacci_no_cache(n-1) + fibonacci_no_cache(n-2)
    
    # 有快取版本
    @functools.lru_cache(maxsize=128)
    def fibonacci_with_cache(n):
        if n <= 1:
            return n
        return fibonacci_with_cache(n-1) + fibonacci_with_cache(n-2)
    
    # 測試
    n = 35
    
    start = time.time()
    result1 = fibonacci_no_cache(n)
    time_no_cache = time.time() - start
    
    start = time.time()
    result2 = fibonacci_with_cache(n)
    time_with_cache = time.time() - start
    
    print(f"無快取: {time_no_cache:.4f} 秒")
    print(f"有快取: {time_with_cache:.4f} 秒")
    print(f"加速比: {time_no_cache/time_with_cache:.2f}x")
    
    # 查看快取資訊
    print(f"快取資訊: {fibonacci_with_cache.cache_info()}")
```

## 效能優化最佳實踐

### 1. 常見效能陷阱與解決方案

| 問題 | 解決方案 | 效能提升 |
|------|----------|----------|
| DataFrame.iterrows() | 使用向量化操作或 itertuples() | 10-100x |
| 頻繁的列表 append | 使用列表推導式或預先分配 | 2-5x |
| 重複計算 | 使用快取（lru_cache） | 視情況 |
| 字串串接在迴圈中 | 使用 join() 或 StringIO | 5-20x |
| 全域變數查找 | 使用局部變數 | 1.5-2x |
| 使用 + 合併列表 | 使用 extend() | 2-3x |

### 2. 優化策略優先順序

1. **演算法優化**：O(n²) → O(n log n)
2. **資料結構選擇**：list vs set vs dict
3. **向量化操作**：NumPy/Pandas 向量化
4. **並行處理**：multiprocessing/threading
5. **快取機制**：記憶化、結果快取
6. **延遲載入**：生成器、惰性求值
7. **編譯優化**：Cython、Numba

### 3. 程式碼優化範例

```python
# ❌ 差的做法
def bad_practices():
    # 1. 字串串接
    result = ""
    for i in range(10000):
        result += str(i)
    
    # 2. 重複計算
    data = []
    for i in range(1000):
        data.append(len([x for x in range(1000) if x % 2 == 0]))
    
    # 3. 不必要的函數呼叫
    for i in range(len(my_list)):
        process(my_list[i])

# ✅ 好的做法
def good_practices():
    # 1. 使用 join
    result = ''.join(str(i) for i in range(10000))
    
    # 2. 預先計算
    even_count = len([x for x in range(1000) if x % 2 == 0])
    data = [even_count] * 1000
    
    # 3. 直接迭代
    for item in my_list:
        process(item)
```

## 常見問題與解決方案

### Q1: cProfile 顯示太多無關資訊怎麼辦？

```python
import cProfile
import pstats
import re

def profile_specific_module(script_name, module_filter='your_module'):
    """只分析特定模組"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 執行你的程式碼
    exec(open(script_name).read())
    
    profiler.disable()
    
    # 過濾結果
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    # 只顯示特定模組的結果
    stats.print_stats(module_filter)
```

### Q2: 如何分析記憶體洩漏？

```python
import tracemalloc
import gc

def find_memory_leaks():
    """追蹤記憶體使用"""
    tracemalloc.start()
    
    # 執行可能有記憶體洩漏的程式碼
    snapshot1 = tracemalloc.take_snapshot()
    
    # ... 執行程式碼 ...
    
    snapshot2 = tracemalloc.take_snapshot()
    
    # 比較差異
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("[ Top 10 記憶體增長 ]")
    for stat in top_stats[:10]:
        print(stat)
    
    # 強制垃圾回收
    gc.collect()
```

### Q3: 如何選擇合適的分析工具？

| 情況 | 建議工具 | 原因 |
|------|----------|------|
| 初步分析 | cProfile | 內建、簡單、快速 |
| 詳細分析 | py-spy | 逐行分析、視覺化好 |
| 記憶體問題 | memory_profiler | 專門針對記憶體 |
| 生產環境 | py-spy | 可附加到執行中程序 |
| 特定函數 | line_profiler | 逐行時間分析 |
| C 擴展 | py-spy --native | 支援原生程式碼 |

### Q4: 優化後如何驗證效果？

```python
import timeit
import statistics

def benchmark_comparison():
    """基準測試比較"""
    
    # 設定測試
    setup_code = """
import numpy as np
data = np.random.randn(10000)
    """
    
    # 原始版本
    original_code = """
result = []
for x in data:
    if x > 0:
        result.append(x * 2)
    """
    
    # 優化版本
    optimized_code = """
result = data[data > 0] * 2
    """
    
    # 執行基準測試
    n_runs = 1000
    
    original_times = timeit.repeat(
        original_code, 
        setup=setup_code, 
        repeat=5, 
        number=n_runs
    )
    
    optimized_times = timeit.repeat(
        optimized_code, 
        setup=setup_code, 
        repeat=5, 
        number=n_runs
    )
    
    # 統計分析
    print(f"原始版本:")
    print(f"  平均: {statistics.mean(original_times):.6f} 秒")
    print(f"  標準差: {statistics.stdev(original_times):.6f} 秒")
    
    print(f"優化版本:")
    print(f"  平均: {statistics.mean(optimized_times):.6f} 秒")
    print(f"  標準差: {statistics.stdev(optimized_times):.6f} 秒")
    
    speedup = statistics.mean(original_times) / statistics.mean(optimized_times)
    print(f"加速比: {speedup:.2f}x")
```

## 進階技巧

### 1. 自訂 Profiler

```python
import sys
import functools
import time
from collections import defaultdict

class CustomProfiler:
    """自訂效能分析器"""
    def __init__(self):
        self.stats = defaultdict(lambda: {'calls': 0, 'total_time': 0})
        
    def profile(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            
            # 記錄統計
            func_name = f"{func.__module__}.{func.__name__}"
            self.stats[func_name]['calls'] += 1
            self.stats[func_name]['total_time'] += elapsed
            
            return result
        return wrapper
    
    def print_stats(self):
        """列印統計結果"""
        print(f"{'Function':<50} {'Calls':<10} {'Total Time':<15} {'Avg Time':<15}")
        print("-" * 90)
        
        for func_name, stats in sorted(
            self.stats.items(), 
            key=lambda x: x[1]['total_time'], 
            reverse=True
        ):
            avg_time = stats['total_time'] / stats['calls']
            print(f"{func_name:<50} {stats['calls']:<10} "
                  f"{stats['total_time']:<15.6f} {avg_time:<15.6f}")

# 使用範例
profiler = CustomProfiler()

@profiler.profile
def example_function():
    time.sleep(0.1)
    return "done"

# 執行後列印統計
profiler.print_stats()
```

### 2. 持續效能監控

```python
import psutil
import time
import threading

class PerformanceMonitor:
    """即時效能監控"""
    def __init__(self, interval=1):
        self.interval = interval
        self.monitoring = False
        self.stats = []
        
    def start(self):
        """開始監控"""
        self.monitoring = True
        thread = threading.Thread(target=self._monitor)
        thread.daemon = True
        thread.start()
        
    def _monitor(self):
        """監控迴圈"""
        process = psutil.Process()
        
        while self.monitoring:
            stats = {
                'timestamp': time.time(),
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'num_threads': process.num_threads(),
            }
            self.stats.append(stats)
            time.sleep(self.interval)
    
    def stop(self):
        """停止監控"""
        self.monitoring = False
        
    def get_summary(self):
        """取得摘要"""
        if not self.stats:
            return "No data collected"
        
        cpu_values = [s['cpu_percent'] for s in self.stats]
        mem_values = [s['memory_mb'] for s in self.stats]
        
        return {
            'avg_cpu': sum(cpu_values) / len(cpu_values),
            'max_cpu': max(cpu_values),
            'avg_memory_mb': sum(mem_values) / len(mem_values),
            'max_memory_mb': max(mem_values),
        }

# 使用範例
monitor = PerformanceMonitor()
monitor.start()

# 執行你的程式碼
time.sleep(5)

monitor.stop()
print(monitor.get_summary())
```

## 總結

效能分析是 Python 開發中的重要技能。掌握 cProfile 和 py-spy 等工具，結合正確的優化策略，能夠顯著提升程式效能。記住以下要點：

1. **先測量，後優化**：不要憑感覺優化，要基於數據
2. **找出真正的瓶頸**：通常 20% 的程式碼消耗 80% 的時間
3. **選擇合適的工具**：不同情況使用不同的分析工具
4. **持續監控**：建立效能基準，追蹤優化效果
5. **平衡可讀性與效能**：不要為了微小的效能提升犧牲程式碼品質

## 參考資源

- [Python 官方 Profile 文件](https://docs.python.org/3/library/profile.html)
- [py-spy GitHub](https://github.com/benfred/py-spy)
- [SnakeViz 文件](https://jiffyclub.github.io/snakeviz/)
- [Memory Profiler](https://github.com/pythonprofilers/memory_profiler)
- [Line Profiler](https://github.com/pyutils/line_profiler)
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [NumPy Optimization](https://numpy.org/doc/stable/user/c-info.python-as-glue.html)