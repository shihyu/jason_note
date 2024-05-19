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

