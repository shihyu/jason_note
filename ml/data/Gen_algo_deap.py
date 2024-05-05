import random
from deap import base, creator, tools


# 定義問題目標：這裡我們以求一元二次函數的最大值為例
def fitness_function(x):
    return -((x - 5) ** 2) + 25


# 設定DEAP的適應度函數最小化
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", float, fitness=creator.FitnessMax)

# 設定DEAP的toolbox
toolbox = base.Toolbox()

# 設定個體的產生方式
toolbox.register(
    "individual",
    tools.initIterate,
    creator.Individual,
    lambda: (random.uniform(0, 10),),
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# 設定演算法的參數
toolbox.register("mate", tools.cxBlend, alpha=0.5)  # 交配方式：混合交配
toolbox.register(
    "mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2
)  # 突變方式：高斯突變
toolbox.register("select", tools.selTournament, tournsize=3)  # 選擇方式：錦標賽選擇


# 設定演算法主函數
def main():
    population = toolbox.population(n=50)  # 初始化族群
    generations = 100  # 設定迭代次數

    for gen in range(generations):
        offspring = toolbox.select(population, len(population))  # 選擇父母
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.5:
                toolbox.mate(child1, child2)  # 以一定機率交配
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < 0.2:
                toolbox.mutate(mutant)  # 以一定機率突變
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(fitness_function, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = (fit,)

        population[:] = offspring

    best_individual = tools.selBest(population, 1)[0]
    print("最適個體:", best_individual)
    print("最適適應度:", best_individual.fitness.values[0])


if __name__ == "__main__":
    main()
