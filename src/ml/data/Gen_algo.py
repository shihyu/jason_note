import random


# 定義目標函數
def fitness_function(x):
    return -((x - 5) ** 2) + 25


# 產生初始個體（隨機生成）
def generate_individual():
    return random.uniform(0, 10)


# 計算個體的適應度
def calculate_fitness(individual):
    return fitness_function(individual)


# 交配兩個個體
def crossover(parent1, parent2):
    return (parent1 + parent2) / 2


# 突變個體
def mutate(individual, mutation_rate):
    if random.random() < mutation_rate:
        individual += random.uniform(-0.5, 0.5)
    return individual


# 基因演算法主函數
def genetic_algorithm(population_size, generations, mutation_rate):
    population = [generate_individual() for _ in range(population_size)]

    for generation in range(generations):
        # 計算每個個體的適應度
        fitness_scores = [calculate_fitness(individual) for individual in population]

        # 選擇父母進行交配
        parents = random.choices(population, weights=fitness_scores, k=2)

        # 交配並產生下一代
        offspring = crossover(parents[0], parents[1])

        # 突變下一代
        offspring = mutate(offspring, mutation_rate)

        # 將下一代加入新的族群
        population.append(offspring)

        # 移除最不適應的個體
        min_fitness_index = fitness_scores.index(min(fitness_scores))
        del population[min_fitness_index]

    # 找到最適合的個體
    best_individual = max(population, key=calculate_fitness)
    best_fitness = fitness_function(best_individual)

    return best_individual, best_fitness


"""
基因演算法是一種優化問題的搜尋方法，模仿了自然界的進化機制。這裡我們來實現一個簡單的基因演算法來解決一個最基本的問題：找到給定函數的最大值。

假設我們想要最大化的函數是一個簡單的一元二次函數，例如：

f(x) = -(x - 5)**2 + 25

我們的目標是找到使這個函數達到最大值的 x。

"""

if __name__ == "__main__":
    # 設定演算法參數並運行
    population_size = 50
    generations = 100
    mutation_rate = 0.1

    best_individual, best_fitness = genetic_algorithm(
        population_size, generations, mutation_rate
    )
    print("最適個體:", best_individual)
    print("最適適應度:", best_fitness)
