from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from scipy.stats import bernoulli
import numpy as np
import random


# 問題描述
GENE_LENGTH = 26  # 基因長度
SEARCH_RANGE = (-30, 30)  # 搜索範圍


# 目標函數
def objective_function(x):
    return (x**2 + x) * np.cos(2 * x) + x**2 + x


def decode(individual):
    """將個體解碼為對應的實數"""
    num = int("".join([str(_) for _ in individual]), 2)
    x = SEARCH_RANGE[0] + num * (SEARCH_RANGE[1] - SEARCH_RANGE[0]) / (
        2**GENE_LENGTH - 1
    )
    return x


def generate_individual():
    """生成一個隨機個體"""
    return [random.randint(0, 1) for _ in range(GENE_LENGTH)]


def evaluate(individual):
    """評估個體的適應度"""
    x = decode(individual)
    return (objective_function(x),)


def crossover(parent1, parent2):
    """均勻交叉"""
    child1, child2 = tools.cxUniform(parent1, parent2, indpb=0.5)
    return child1, child2


def mutate(individual):
    """按位翻轉變異"""
    (child,) = tools.mutFlipBit(individual, indpb=0.2)
    return child


def select(population):
    """錦標賽選擇"""
    return tools.selTournament(population, k=2, tournsize=2)


def main():
    # 初始化
    random.seed(42)
    toolbox = base.Toolbox()
    toolbox.register("individual", generate_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("select", select)
    toolbox.register("mate", crossover)
    toolbox.register("mutate", mutate)

    # 進行遺傳演算法
    population = toolbox.population(n=100)
    fit_stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    fit_stats.register("avg", np.mean)
    fit_stats.register("std", np.std)
    fit_stats.register("min", np.min)
    fit_stats.register("max", np.max)

    population, logbook = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=0.5,
        mutpb=0.2,
        ngen=50,
        stats=fit_stats,
        verbose=True,
    )

    # 輸出結果
    best_individual = tools.selBest(population, k=1)[0]
    print(f"Best individual: {best_individual}")
    print(f"Best fitness: {best_individual.fitness.values[0]}")


if __name__ == "__main__":
    main()
