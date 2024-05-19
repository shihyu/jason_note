## GA + Vectotbt 

https://www.youtube.com/watch?v=W-jxEZXu-pQ

```py
import numpy as np
import yfinance as yf
import multiprocessing
import time
import vectorbt as vbt
import warnings
from deap import base, creator, tools, algorithms

warnings.filterwarnings("ignore")


def run_strategy_bt(data, fast_ma, slow_ma):
    fast_ma = vbt.MA.run(data, fast_ma)
    slow_ma = vbt.MA.run(data, slow_ma)
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    return vbt.Portfolio.from_signals(data, entries, exits, init_cash=100)


# 定義適應度函數
def trade_fitness(individual, data):
    sma1, sma2 = individual
    if sma1 < sma2:
        fast_ma = sma1
        slow_ma = sma2
    else:
        fast_ma = sma2
        slow_ma = sma1

    pf = run_strategy_bt(data, fast_ma, slow_ma)
    returns_stats = pf.returns_stats(column=10, settings=dict(freq="d"))
    Annualized_Return = returns_stats["Annualized Return [%]"]
    Max_Drawdown = returns_stats["Max Drawdown [%]"]
    Sortino_Ratio = returns_stats["Sortino Ratio"]
    # print(Annualized_Return)
    # print(Max_Drawdown)
    # print(Sortino_Ratio)
    fitness = (Annualized_Return / abs(Max_Drawdown)) * Sortino_Ratio
    if np.isnan(fitness):
        fitness = 0

    print(
        f"pid: {multiprocessing.current_process().pid}, individual: {individual}, fitness: {fitness}"
    )
    return (fitness,)


if __name__ == "__main__":
    # 下載股票歷史數據
    ticker = "AAPL"
    data = yf.download(ticker, start="2020-01-01", end="2023-04-30")
    # fast_ma = vbt.MA.run(data, 10)
    # slow_ma = vbt.MA.run(data, 50)
    # entries = fast_ma.ma_crossed_above(slow_ma)
    # exits = fast_ma.ma_crossed_below(slow_ma)
    # pf = vbt.Portfolio.from_signals(data, entries, exits, init_cash=100)
    # returns_stats = pf.returns_stats(column=10, settings=dict(freq="d"))
    # print(data.head())
    # input()
    # 設置基因演算法參數
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    """
    在這個示例中,我們首先定義了交易策略的適應度函數 trade_fitness。這個函數計算了四個移動平均線的值,並根據它們的交叉關係生成交易訊號。然後,它計算了基於這個交易訊號的策略收益。適應度函數的輸出是策略的總收益。
    接下來,我們設置了基因演算法的參數,包括個體表示、交叉、變異、選擇等操作。個體由四個整數表示,分別對應四個移動平均線的天數,範圍為 5 到 250 天。
    然後,我們執行基因演算法優化,輸出了最優解及其適應度值(總收益)。
    運行這個程式碼,您將獲得最佳的四個移動平均線天數,以及使用這些天數時的最大策略收益。
    您可以根據需要調整適應度函數、個體表示等,以找到更複雜的交易策略。此外,您還可以添加其他約束條件,例如最大回撤等,使得優化更加全面。
    """
    toolbox = base.Toolbox()
    toolbox.register("attr_int", np.random.randint, 5, 100)

    toolbox.register(
        "individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=2
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", trade_fitness, data=data["Close"])
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=5, up=100, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    """
    創建一個進程池,裡面有8個工作進程
    使用toolbox.register("map", pool.map)將pool.map函數註冊為toolbox中的"map"函數。
    這樣在評估個體時,就會使用pool.map進行並行計算。
    在優化結束後,使用pool.close()關閉進程池,並使用pool.join()等待所有工作進程結束。
    """
    pool = multiprocessing.Pool(processes=8)
    # 使用toolbox.register將pool.map註冊為"map"函數
    toolbox.register("map", pool.map)

    # 執行基因演算法優化
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    start_time = time.time()
    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=0.5,
        mutpb=0.2,
        ngen=100,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )

    # 關閉進程池並等待所有結果
    pool.close()
    pool.join()
    end_time = time.time()
    print("Time taken: ", end_time - start_time)

    # 輸出最優解
    best_ind = hof.items[0]
    print("Best individual: ", best_ind)
    print("Best fitness: ", best_ind.fitness.values[0])

    sma1, sma2 = best_ind
    if sma1 < sma2:
        fast_ma = sma1
        slow_ma = sma2
    else:
        fast_ma = sma2
        slow_ma = sma1

    pf = run_strategy_bt(data["Close"], fast_ma, slow_ma)
    returns_stats = pf.returns_stats(column=10, settings=dict(freq="d"))
    print(returns_stats)
    stats = pf.stats(column=10, settings=dict(freq="d"))
    print(stats)
```

---

## 基於遺傳演算法（deap）的配詞問題與deap框架



### 前言

  該筆記主要記錄兩個問題：
  （1）基於deap庫的[遺傳演算法](https://so.csdn.net/so/search?q=遗传算法&spm=1001.2101.3001.7020)程序框架大致什麼樣？
  （2）在框架的基礎上如何實現經典的配詞問題？

### 基於deap的程序框架

```python
import numpy as np
from deap import base, tools, creator, algorithms
import random

# 問題定義；定式
creator.create('Fitness...', base.Fitness, weights=(...1.0,)) #　最大化問題
creator.create('Individual', list, fitness=creator.Fitness...)

# 個體編碼；主要依靠人為設計
geneLength=...
toolbox = base.Toolbox()
toolbox.register('個體實現方法的名稱',...)
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.個體實現方法的名稱, n=geneLength)
#print(toolbox.individual())#列印檢查個體

#建立種群；定式
N_POP = ...#種群內個體數量，參數過小，則搜尋速度過慢
toolbox.register('population',tools.initRepeat,list,toolbox.individual)
pop = toolbox.population(n=...)#建立一個種群pop
#for ind in pop:#列印一個種群檢查
#   print(ind)

#評價函數；主要依靠人為設計
def evaluate(ind):
    pass
    
#註冊各種工具，人為選擇具體的方法；寫法定式
toolbox.register('evaluate', evaluate)#評價函數
toolbox.register('select', tools...)#選擇
toolbox.register('mate', tools...)#交叉
toolbox.register('mutate', tools...)#突變

#超參數設定；人為根據理論與經驗設定
NGEN = ...#迭代步數，參數過小，則在收斂之前就結束搜尋
CXPB = ...#交叉機率，參數過小，則族群不能有效更新
MUTPB = ...#突變機率，參數過小，則容易陷入局部最優

#開始工作，先對初始的種群計算適應度；定式
invalid_ind = [ind for ind in pop if not ind.fitness.valid]
fitnesses = toolbox.map(toolbox.evaluate,invalid_ind)
for ind ,fitness in zip(invalid_ind,fitnesses):
    ind.fitness.values = fitness
    
#循環迭代，近似定式，但是可以自行增加一些提高遺傳演算法性能的方法
for gen in range(NGEN):
    offspring = toolbox.select(pop,N_POP)#先選擇一次
    offspring = [toolbox.clone(_) for _ in offspring]#再克隆一次，克隆是必須的

    for ind1,ind2 in zip(offspring[::2],offspring[1::2]):#交叉操作
        if random.random() < CXPB:#交叉
            toolbox.mate(ind1,ind2)
            del ind1.fitness.values
            del ind2.fitness.values
    for ind in offspring:#變異操作
        if random.random() <MUTPB:
            toolbox.mutate(ind)
            del ind.fitness.values
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]#將刪除了適應度的個體重新評估
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for fitness, ind in zip(fitnesses, invalid_ind):
        ind.fitness.values = fitness
   #精英選擇策略，加速收斂 
    combinedPop = pop + offspring#將子代與父代結合起來
    pop = tools.selBest(combinedPop,N_POP)#再從子代與父代的結合中選擇出適應度最高的一批作為新的種群

#顯示演算法運行結果
bestInd = tools.selBest(pop,1)[0]#選擇出最好的個體編號
bestFit = bestInd.fitness.values[0]#最好的個體適應度
print('best solution: '+str(bestInd))#列印解
print('best fitness: '+str(bestFit))#列印適應度

```

 由以上的程序框架可知：
  （1）個體編碼方式、評價函數基本依靠個人根據實際問題設計。
  （2）選擇方法註冊工具、迭代運算等基本是定式。
  （3）迭代運算雖然可以當做定式用，但是適當增加一些諸如精英選擇策略這樣的程式碼可以明顯提高演算法性能。



### 配詞問題

  配詞問題內容比較簡單，比如有個字串‘`woshidaxuesheng`’，希望能用隨機演算法經過尋優將等長的隨機字母序列生成同樣的內容。在遺傳演算法裡就等於是生成一個擁有很多隨機字母個體的種群，經過運算後得到一個個體內容最接近於‘`woshidaxuesheng`’。
  先貼上完整的原始碼，再分析問題。這裡可以看到配詞問題程式碼用了兩種評價函數：一種是將配詞問題轉化為最小化問題，令個體的內容與目標字串差異最小；一種是將配詞問題轉化為最大化問題，令個體的內容與目標字串相同性最強。
  本程式碼將最小化思路程序片段進行了註釋，使用最大化思路程序。

```python
import numpy as np
from deap import base, tools, creator, algorithms
import random

# 問題定義
#creator.create('FitnessMin', base.Fitness, weights=(-1.0,)) #　最小化問題
#creator.create('Individual', list, fitness=creator.FitnessMin)
creator.create('FitnessMax', base.Fitness, weights=(1.0,)) #　最大化問題
creator.create('Individual', list, fitness=creator.FitnessMax)

# 個體編碼
geneLength = 14#字串內有14個字元
toolbox = base.Toolbox()
toolbox.register('genASCII',random.randint, 97, 122)#英文小寫字符的ASCII碼範圍為97~122
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.genASCII, n=geneLength)
#print(toolbox.individual())

#建立種群
N_POP = 100#種群內個體數量，參數過小，則搜尋速度過慢
toolbox.register('population',tools.initRepeat,list,toolbox.individual)
pop = toolbox.population(n=N_POP)
#for ind in pop:#列印一個種群檢查
#   print(ind)

#評價函數
#def evaluate(ind):
#    target = list('zzyshiwodedidi')
#    target = [ord(item) for item in target]
#    return (sum(np.abs(np.asarray(target) - np.asarray(ind)))),
def evaluate(ind):
    target = list('zzyshiwodedidi')#需要匹配的字串
    target = [ord(item) for item in target]#將字串內的字元都轉換成ASCII碼
    return (sum(np.abs(np.asarray(target) == np.asarray(ind)))),
    
#註冊各種工具
toolbox.register('evaluate', evaluate)#評價函數
toolbox.register('select', tools.selTournament, tournsize=2)#錦標賽選擇
toolbox.register('mate', tools.cxUniform, indpb=0.5)#均勻交叉
toolbox.register('mutate', tools.mutShuffleIndexes, indpb=0.5)#亂序突變

#超參數設定
NGEN = 300#迭代步數，參數過小，則在收斂之前就結束搜尋
CXPB = 0.8#交叉機率，參數過小，則族群不能有效更新
MUTPB = 0.2#突變機率，參數過小，則容易陷入局部最優

#開始工作，先對初始的種群計算適應度
invalid_ind = [ind for ind in pop if not ind.fitness.valid]
fitnesses = toolbox.map(toolbox.evaluate,invalid_ind)
for ind ,fitness in zip(invalid_ind,fitnesses):
    ind.fitness.values = fitness
    
#循環迭代
for gen in range(NGEN):
    offspring = toolbox.select(pop,N_POP)#先選擇一次
    offspring = [toolbox.clone(_) for _ in offspring]#再克隆一次

    for ind1,ind2 in zip(offspring[::2],offspring[1::2]):#交叉
        if random.random() < CXPB:#交叉
            toolbox.mate(ind1,ind2)
            del ind1.fitness.values
            del ind2.fitness.values
    for ind in offspring:#變異
        if random.random() <MUTPB:
            toolbox.mutate(ind)
            del ind.fitness.values
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]#將刪除了適應度的個體重新評估
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for fitness, ind in zip(fitnesses, invalid_ind):
        ind.fitness.values = fitness
   #精英選擇策略，加速收斂 
    combinedPop = pop + offspring#將子代與父代結合起來
    pop = tools.selBest(combinedPop,N_POP)#再從子代與父代的結合中選擇出適應度最高的一批作為新的種群

bestInd = tools.selBest(pop,1)[0]#選擇出最好的個體編號
bestFit = bestInd.fitness.values[0]#最好的個體適應度
bestInd = [chr(item) for item in bestInd]#將該個體裡的ASCII碼轉換成字元形式
print('best solution: '+str(bestInd))#列印字元
print('best fitness: '+str(bestFit))#列印適應度，這裡可以看到適應度並不是我們需要的問題的解，僅僅是對解的一種評估得分
```

### 程式設計

#### 個體設計

  首先考慮個體是如何設計編碼的。
  我們要得到一個與’`zzyshiwodedidi`‘最相近的字串，顯然這個個體也得是個小寫字母的字串，而且長度得和’`zzyshiwodedidi`'相同，所以個體的基因長度肯定是14。
  綜上，個體應該是個長度為14的隨機小寫字母列表。

```python
# 個體編碼
geneLength = 14#字串內有14個字元
toolbox = base.Toolbox()
toolbox.register('genASCII',random.randint, 97, 122)#英文小寫字符的ASCII碼範圍為97~122
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.genASCII, n=geneLength)
#print(toolbox.individual())
```

小寫英文字母的ASCII碼範圍是97~122，而且ASCII碼肯定是整數，所以隨機函數應該是隨機生成整形（int），所以註冊函數寫成：

```python
toolbox.register('genASCII',random.randint, 97, 122)
```

再將這個註冊函數代入到個體的註冊函數里面即可。

```python
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.genASCII, n=geneLength)
```

#### 評價函數設計

  我們想要評價一個個體和’`zzyshiwodedidi`‘的相似程度，自然要進行比較，字元顯然不方便直接比，但是轉換成ASCII碼（數字）顯然就方便的多。
  於是評價函數的設計思路就是：將目標’`zzyshiwodedidi`'轉化為ASCII碼，然後與個體的基因依次對比（個體本身就是ASCII碼）。

```python
def evaluate(ind):
    target = list('zzyshiwodedidi')#需要匹配的字串
    target = [ord(item) for item in target]#將字串內的字元都轉換成ASCII碼
    return (sum(np.abs(np.asarray(target) == np.asarray(ind)))),
```

使用`ord`函數將字串裡的字元依次轉換為ASCII碼。

```python
	target = list('zzyshiwodedidi')#需要匹配的字串
    target = [ord(item) for item in target]#將字串內的字元都轉換成ASCII碼
```

依次轉換完成後需要依次比對，這裡需要注意一件事，**將目標字串轉換為ASCII碼序列，與直接的隨機數列表個體的資料形式不同**。



![在這裡插入圖片描述](images/20201202111748717.jpg)  
  

**由上圖可見，第一行個體是列表格式，元素之間用`,`割開；而第二行目標字串轉換完後是矩陣形式，是一個行向量**。
  因此需要將個體使用`np.asarry`函數轉換為矩陣形式：

```python
 return (sum(np.abs(np.asarray(target) == np.asarray(ind)))),
```

  當然只需要轉換個體就行了：

```python
 return (sum(np.abs(target == np.asarray(ind)))),
```

#### 精英選擇策略

  精英選擇策略，即在每一輪迭代循環中，將父代與交叉變異後的子代整一塊，形成一個雙倍於之前規模的大種群，隨後在這個大種群中提取出一半適應度最優的個體。
  說白了就是父代子代一起評，前一半的全提走，後一半的全踢走。
  顯然，這樣的做法會加速收斂，快速得到一個充滿高適應度個體的精英種群。
  這個策略以後也可以叫`內卷策略`。

```python
#精英選擇策略，加速收斂 
    combinedPop = pop + offspring#將子代與父代結合起來
```
