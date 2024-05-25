from deap import algorithms, base, creator, tools
from scipy.stats import bernoulli
import numpy as np
import random

random.seed(42)  # 確保可以復現結果

# 描述問題
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # 單目標，最大值問題
creator.create("Individual", list, fitness=creator.FitnessMax)  # 編碼繼承list類

# 個體編碼
GENE_LENGTH = 26  # 需要26位編碼

toolbox = base.Toolbox()
toolbox.register(
    "binary", bernoulli.rvs, 0.5
)  # 註冊一個Binary的alias，指向scipy.stats中的bernoulli.rvs，機率為0.5
toolbox.register(
    "individual", tools.initRepeat, creator.Individual, toolbox.binary, n=GENE_LENGTH
)  # 用tools.initRepeat生成長度為GENE_LENGTH的Individual


# 評價函數
def decode(individual):
    num = int("".join([str(_) for _ in individual]), 2)  # 解碼到10進制
    x = -30 + (num / (2**26 - 1)) * 60  # 對應回-30，30區間
    return x


def eval(individual):
    x = decode(individual)
    return (((x**2 + x) * np.cos(2 * x) + x**2 + x),)


# 生成初始族群
N_POP = 100  # 族群中的個體數量
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
pop = toolbox.population(n=N_POP)

# 在工具箱中註冊遺傳演算法需要的工具
toolbox.register("evaluate", eval)
toolbox.register(
    "select", tools.selTournament, tournsize=2
)  # 註冊Tournsize為2的錦標賽選擇
toolbox.register("mate", tools.cxUniform, indpb=0.5)  # 注意這裡的indpb需要顯示給出
toolbox.register("mutate", tools.mutFlipBit, indpb=0.5)

# 註冊計算過程中需要記錄的資料
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

# 呼叫DEAP內建的演算法
resultPop, logbook = algorithms.eaSimple(
    pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, stats=stats, verbose=False
)

# 輸出計算過程
logbook.header = "gen", "nevals", "avg", "std", "min", "max"
print(logbook)
