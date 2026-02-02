# OpenEvolve 完整指南

## 🎯 什麼是 OpenEvolve?

OpenEvolve 是一個**自動程式碼演化工具**，它結合了傳統**基因演算法 (Genetic Algorithm)** 的演化概念與現代 **AI (LLM)** 的智能，自動優化你的程式碼。

### 核心公式
```
OpenEvolve = 基因演算法 + AI (LLM) + MAP-Elites
```

---

## 🧬 與基因演算法的關係

### 相同的演化循環

兩者都遵循生物演化的模式：

```
初始種群 → 評估適應度 → 選擇 → 變異/交配 → 新一代 → 重複
```

### 核心組件對照表

| 基因演算法概念 | OpenEvolve 實作 | 說明 |
|--------------|----------------|------|
| **染色體 (Chromosome)** | 程式碼 (Code) | 要優化的對象 |
| **基因 (Gene)** | 程式碼片段/函數 | 組成染色體的單位 |
| **適應度函數 (Fitness)** | 評估器 (Evaluator) | 評分機制 |
| **變異 (Mutation)** | LLM 生成變異 | 產生新版本 |
| **交配 (Crossover)** | 程式碼混合 | 結合多個解決方案 |
| **選擇 (Selection)** | 保留最佳解 | 淘汰低分程式 |
| **種群 (Population)** | 程式資料庫 | 候選解集合 |

---

## 🆚 傳統 GA vs OpenEvolve 對比

### 1️⃣ 變異方式的差異

#### 傳統基因演算法
```python
# 傳統 GA: 隨機變異（盲目搜索）
def mutate(chromosome):
    # 隨機改變某些位元
    pos = random.randint(0, len(chromosome)-1)
    chromosome[pos] = random.choice([0, 1])
    return chromosome
```

**特點:**
- ❌ 隨機變異，不理解內容
- ❌ 可能產生無意義的結果
- ✅ 計算成本低
- ✅ 理論基礎紮實

#### OpenEvolve (LLM 驅動)
```python
# OpenEvolve: 使用 LLM 智能變異
def mutate_with_llm(code, fitness_feedback):
    # AI 理解程式碼並產生有意義的改進
    prompt = f"""
    這段程式碼分數是 {fitness_feedback}
    請優化它：
    {code}
    """
    improved_code = llm.generate(prompt)
    return improved_code
```

**特點:**
- ✅ **智能變異**，理解程式語義
- ✅ 產生有意義的改進
- ✅ 可處理複雜結構
- ❌ 需要 API 成本

---

### 2️⃣ 實際演化路徑對比

#### 例子：優化排序函數

**傳統 GA 的演化路徑：**
```
第 0 代: [隨機排列程式碼]
第 1 代: [隨機變異，可能變更糟]
第 2 代: [隨機變異，可能變更糟]
第 3 代: [隨機變異，可能變更好]
...
第 50 代: [經過大量嘗試，可能找到解]

❌ 盲目搜索，需要大量迭代
```

**OpenEvolve 的演化路徑：**
```
第 0 代: 冒泡排序 (分數: 0.3)
       ↓ LLM 分析：「有太多不必要的比較」
       
第 1 代: 選擇排序 (分數: 0.5)
       ↓ LLM 分析：「可以使用分治法加速」
       
第 2 代: 快速排序 (分數: 0.8)
       ↓ LLM 分析：「Python 內建函數更優」
       
第 3 代: sorted() (分數: 1.0)
       ✅ 達到最佳解！

✅ 智能引導，快速收斂
```

---

### 3️⃣ 性能對比表

| 特性 | 傳統基因演算法 | OpenEvolve |
|-----|--------------|-----------|
| **搜索方式** | 🎲 隨機探索 | 🧠 智能引導 |
| **理解能力** | ❌ 不理解內容 | ✅ 理解語義 |
| **收斂速度** | 🐌 慢（需大量迭代） | 🚀 快（智能跳躍） |
| **計算成本** | 💚 低 | 💰 高（LLM API） |
| **適用場景** | 參數優化、組合問題 | 程式碼優化、複雜結構 |
| **迭代次數** | 通常需要數千次 | 通常需要數十次 |

---

### 4️⃣ 使用場景對比

#### 傳統 GA 適合：
- ✅ 參數優化（找最佳係數）
- ✅ 組合優化（旅行推銷員問題）
- ✅ 固定結構的問題
- ✅ 需要快速大量迭代
- ✅ 沒有 API 成本限制

#### OpenEvolve 適合：
- ✅ **程式碼優化** ⭐
- ✅ **演算法改進** ⭐
- ✅ 需要語義理解
- ✅ 複雜結構演化
- ✅ 創新解決方案探索
- ✅ 快速得到高品質結果

---

### 5️⃣ OpenEvolve 的特殊算法：MAP-Elites

OpenEvolve 不只是簡單的 GA，還整合了 **MAP-Elites** 算法：

```
傳統 GA:              OpenEvolve (MAP-Elites):
只保留最佳解          保留多樣化的優秀解
     ⭐              ⭐ ⭐ ⭐
                     ⭐ ⭐ ⭐
                     ⭐ ⭐ ⭐
```

**優勢：**
- 🎯 探索多種解決方案
- 🔄 避免過早收斂到局部最優
- 💡 保持創新性和多樣性

---

## 🚀 快速開始

### 安裝
```bash
pip install openevolve --break-system-packages
```

### 設定 API Key
```bash
export OPENAI_API_KEY='your-openai-api-key'
```

### 三種使用方式

#### 方式 A: 演化函數
```python
from openevolve import evolve_function

def slow_sort(arr):
    # 你的低效實作
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

result = evolve_function(
    slow_sort,
    test_cases=[([3,1,2], [1,2,3])],
    iterations=50
)
print(result.best_code)
```

#### 方式 B: 演化程式碼
```python
from openevolve import evolve_code

initial_code = '''
def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

def evaluate(program_path):
    # 你的評估邏輯
    return {"score": 0.95}

result = evolve_code(initial_code, evaluate, iterations=50)
```

#### 方式 C: 完整控制
```python
from openevolve import run_evolution, Config

config = Config(
    max_iterations=100,
    checkpoint_interval=10
)

result = run_evolution(
    initial_program='program.py',
    evaluator='evaluator.py',
    config=config
)
```

---

## 📚 核心組件說明

### 1. 初始程式 (Initial Program)

使用特殊標記指定要演化的區塊：

```python
initial_code = """
# EVOLVE-BLOCK-START
def your_function():
    # 你的程式碼
    pass
# EVOLVE-BLOCK-END
"""
```

### 2. 評估函數 (Evaluator)

必須返回包含 'score' 的字典，分數範圍 0.0 到 1.0：

```python
def my_evaluator(program_path):
    """
    評估程式品質
    """
    import importlib.util
    import time
    
    # 載入程式
    spec = importlib.util.spec_from_file_location("test", program_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
        
        # 測試正確性
        result = module.calculate_sum([1, 2, 3])
        if result != 6:
            return {"score": 0.0}
        
        # 測試性能
        start = time.time()
        module.calculate_sum(list(range(10000)))
        duration = time.time() - start
        
        # 基於速度給分
        performance = 1.0 / (duration * 100 + 1)
        
        return {
            "score": min(1.0, performance),
            "runtime": duration,
            "correctness": True
        }
    except Exception as e:
        return {"score": 0.0, "error": str(e)}
```

### 3. 配置 (Config)

```python
from openevolve import Config

config = Config(
    max_iterations=100,      # 最大迭代次數
    checkpoint_interval=10,  # 檢查點頻率
    random_seed=42,          # 隨機種子
    log_level='INFO',        # 日誌級別
)
```

---

## 💡 實戰範例

### 範例 1: 優化排序函數

```python
from openevolve import evolve_function

# 初始的低效冒泡排序
def initial_sort(arr):
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(n-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# 測試案例
test_cases = [
    ([3, 1, 2], [1, 2, 3]),
    ([5, 2, 8, 1], [1, 2, 5, 8]),
    ([10, 7, 3, 9, 1, 5], [1, 3, 5, 7, 9, 10]),
]

# 執行演化
result = evolve_function(
    initial_sort,
    test_cases=test_cases,
    iterations=10
)

print(f"最佳分數: {result.best_score}")
print(f"優化後程式碼:\n{result.best_code}")
```

### 範例 2: 優化 Fibonacci

```python
from openevolve import evolve_code
import time

# 低效的遞迴實作
initial_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

# 評估函數
def evaluate_fibonacci(program_path):
    import importlib.util
    
    spec = importlib.util.spec_from_file_location("fib", program_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
        
        # 測試正確性
        test_cases = [(0, 0), (1, 1), (10, 55), (15, 610)]
        for n, expected in test_cases:
            if module.fibonacci(n) != expected:
                return {"score": 0.0}
        
        # 測試性能
        start = time.time()
        module.fibonacci(20)
        duration = time.time() - start
        
        speed_score = max(0, 1.0 - duration)
        
        return {
            "score": speed_score,
            "runtime": duration,
            "correctness": True
        }
    except:
        return {"score": 0.0}

# 執行演化
result = evolve_code(
    initial_code,
    evaluator=evaluate_fibonacci,
    iterations=10
)

print(f"優化結果:\n{result.best_code}")
```

---

## 📊 工作原理演示

### 演化過程示意

```
初始程式 (第 0 代)
    ↓
評估分數: 0.3
    ↓
LLM 分析: "程式碼有冗餘迴圈"
    ↓
生成變異 (第 1 代)
    ↓
評估分數: 0.6 ✨ 改進!
    ↓
LLM 分析: "可以使用內建函數"
    ↓
生成變異 (第 2 代)
    ↓
評估分數: 1.0 🎯 完美!
```

### 核心差異總結

```
傳統 GA 的思維:
"讓我隨機嘗試 10000 種可能性，總會找到好的"
❌ 像猴子打字機

OpenEvolve 的思維:
"我理解這個問題，讓我針對性地改進"
✅ 像專業程式設計師
```

---

## 🎓 進階功能

### 檢查點系統
```python
# 保存進度
result = run_evolution(
    initial_program='program.py',
    evaluator='evaluator.py',
    checkpoint_path='checkpoint.pkl'
)

# 從檢查點恢復
result = run_evolution(
    initial_program='program.py',
    evaluator='evaluator.py',
    checkpoint_path='checkpoint.pkl'  # 自動恢復
)
```

### 並行處理
```python
config = Config(
    max_tasks_per_child=4  # 並行評估
)
```

### 早停機制
```python
config = Config(
    early_stopping_patience=10,  # 10 次無改進則停止
    convergence_threshold=0.001,  # 收斂閾值
    early_stopping_metric='combined_score'
)
```

---

## ⚠️ 注意事項

### 1. API 成本
- OpenEvolve 使用 OpenAI API
- 每次迭代都會調用 LLM
- 建議從小規模開始測試

### 2. 執行時間
- 演化過程可能需要較長時間
- 取決於迭代次數和評估複雜度
- 使用 checkpoint 避免重新開始

### 3. 結果驗證
- 始終驗證演化後的程式碼
- 測試邊界條件
- 確保正確性

### 4. 安全性
- 評估函數會執行程式碼
- 謹慎處理不受信任的輸入
- 在隔離環境中運行

---

## 📈 最佳實踐

### ✅ 好的評估函數設計
```python
def good_evaluator(program_path):
    return {
        "score": 0.95,        # 必須：0.0-1.0
        "runtime": 0.001,     # 可選：性能指標
        "correctness": True,  # 可選：正確性
        "memory": 1024,       # 可選：記憶體使用
    }
```

### ✅ 好的初始程式
- 功能明確
- 有改進空間
- 可測試驗證

### ❌ 避免的陷阱
- 評估函數過於複雜
- 沒有正確性檢查
- 迭代次數過少
- 忽略邊界條件

---

## 🔗 資源與支援

### 官方資源
- GitHub: https://github.com/openevolve/openevolve
- 套件版本: 0.2.26

### 學習資源
- 基因演算法基礎
- LLM prompt engineering
- Python 性能優化

### 社群支援
- 加入討論分享經驗
- 報告問題和建議
- 貢獻範例和改進

---

## 🎯 總結

### OpenEvolve 的本質

```
OpenEvolve = 基因演算法的演化框架
           + LLM 的智能理解
           + MAP-Elites 的多樣性維護
```

### 關鍵優勢

| 優勢 | 說明 |
|-----|------|
| 🧠 智能演化 | 理解程式語義，非盲目搜索 |
| 🚀 快速收斂 | 比傳統 GA 快 10-100 倍 |
| 💡 創新解決方案 | 可能發現人類未想到的優化 |
| 🎯 高品質輸出 | 生成可讀、可維護的程式碼 |

### 適用場景

- ✅ 演算法性能優化
- ✅ 程式碼重構
- ✅ 學習最佳實踐
- ✅ 探索不同實作方式
- ✅ 自動化程式改進

### 開始你的演化之旅！

OpenEvolve 將傳統演化算法與現代 AI 完美結合，讓程式碼優化變得智能且高效。立即嘗試，見證程式碼的進化！🚀

---

**版本**: OpenEvolve 0.2.26  
**文檔更新**: 2025-02-02
