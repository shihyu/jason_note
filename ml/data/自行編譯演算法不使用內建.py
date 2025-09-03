import random
import numpy as np
from deap import creator, base, tools
from scipy.stats import bernoulli

# 設定隨機種子以確保結果可復現
random.seed(42)

# 定義問題為單目標最大化
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# 定義基因編碼長度和工具箱
GENE_LENGTH = 26
toolbox = base.Toolbox()
toolbox.register("binary", bernoulli.rvs, 0.5)
toolbox.register(
    "individual", tools.initRepeat, creator.Individual, toolbox.binary, n=GENE_LENGTH
)


# 定義適應度評價函數
def eval(individual):
    num = int("".join([str(_) for _ in individual]), 2)
    x = -30 + num * 60 / (2**26 - 1)
    return (((x**2 + x) * np.cos(2 * x) + x**2 + x),)


toolbox.register("evaluate", eval)

# 初始化族群
N_POP = 100
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
pop = toolbox.population(n=N_POP)

# 評價初始族群適應度
fitnesses = map(toolbox.evaluate, pop)
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit

# 設定遺傳演算法參數
N_GEN = 50  # 最大代數
CXPB = 0.5  # 交叉概率
MUTPB = 0.2  # 突變概率

# 註冊遺傳運算子
toolbox.register("tourSel", tools.selTournament, tournsize=2)
toolbox.register("crossover", tools.cxUniform)
toolbox.register("mutate", tools.mutFlipBit)

# 設定記錄演算法狀態
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)
logbook = tools.Logbook()

# 開始遺傳迭代
for gen in range(N_GEN):

    # 選擇育種族群
    selectedTour = toolbox.tourSel(pop, N_POP)
    selectedInd = list(map(toolbox.clone, selectedTour))

    # 交叉
    for child1, child2 in zip(selectedInd[::2], selectedInd[1::2]):
        if random.random() < CXPB:
            toolbox.crossover(child1, child2, 0.5)
            del child1.fitness.values
            del child2.fitness.values

    # 突變
    for mutant in selectedInd:
        if random.random() < MUTPB:
            toolbox.mutate(mutant, 0.5)
            del mutant.fitness.values

    # 重新評價被改變個體
    invalid_ind = [ind for ind in selectedInd if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # 更新族群
    pop[:] = selectedInd

    # 記錄當代狀態
    record = stats.compile(pop)
    logbook.record(gen=gen, **record)

# 輸出演算過程記錄
logbook.header = "gen", "avg", "std", "min", "max"
print(logbook)
