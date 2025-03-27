import random
import numpy as np
from deap import base, creator, tools, algorithms

# Sample data: friend lists for each youth (0-139)
youth_list = ["YW1", "YW2", "YW3", "YW4", "YM1", "YM2", "YW5", "YM3", "YM4", "YM5", "YW6", "YW7", "YM6", "YM7", "YM8", "YM9", "YM10", "YM11", "YW8", "YM12", "YM13", "YM14", "YW9", "YM15", "YM16", "YM17", "YW10", "YW11", "YM18", "YM19", "YW12", "YM20", "YW13", "YW14", "YW15", "YM21", "YM22", "YM24", "YM25", "YM26", "YM27", "YW16", "YW17", "YM28", "YM29", "YW18", "YM30", "YM31", "YM32", "YM33", "YW19", "YW20", "YM34", "YM35", "YW21", "YM36", "YW22", "YW23", "YW24", "YM37", "YW25", "YW26", "YW27", "YW28", "YM38", "YW29", "YW30", "YW31", "YM39", "YM40", "YW32", "YW33", "YM41", "YW34", "YW35", "YW36", "YW38", "YW39", "YM42", "YM43", "YW40", "YW41", "YW42", "YM44", "YM45", "YM46", "YW43", "YW45", "YM48", "YW46", "YM49", "YW47", "YW48", "YW49", "YM50", "YW50", "YM51", "YW51", "YM52", "YM53", "YM54", "YW52", "YM55", "YW53", "YM56", "YW54", "YW55", "YM57", "YM58", "YM59", "YW56", "YW57", "YM60", "YM61", "YW58", "YM62", "YW59", "YW60", "YM63", "YW61", "YW62", "YM64", "YW63", "YM65", "YM66", "YM67", "YW68", "YM69", "YM70", "YM71", "YM72", "YW69", "YM73", "YM74", "YM75", "YM76", "YM77", "YM78", "YW70", "YM79", "YW71"]
friend_lists = [...]  # Replace with your actual data

# Constants
NUM_GROUPS = 10
MAX_AGE_DIFF = 18 * 12  # Maximum acceptable age difference in months

def eval_fitness(individual):
    groups = [individual[i:i + NUM_GROUPS] for i in range(0, len(individual), NUM_GROUPS)]
    friend_pairs_count = sum(sum(g == f) for g in groups for f in friend_lists[y]) for y in range(140))
    age_range_penalty = sum(max(abs(y.age - x.age)) - MAX_AGE_DIFF, 0)
                            for y in individuals for x in groups[individual.index(y)])
    return friend_pairs_count, age_range_penalty

creator.create("FitnessMax", base.Fitness, weights=(1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("indices", random.sample, range(140), NUM_GROUPS)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.indices, n=NUM_GROUPS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def cxTwoPoint(x):
    """Ordered crossover for grouped individuals"""
    if random.random() < 0.5:
        return x
    else:
        return toolbox.clone(x)

toolbox.register("evaluate", eval_fitness)
toolbox.register("mate", cxTwoPoint)
toolbox.register("mutate", tools.mutationOrdered, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

population = toolbox.population(n=300)
hof = tools.HallOfFame(1)

stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
stats_size = tools.Statistics(lambda ind: len(ind))
mstats = tools.MultiStatistics([stats_fit, stats_size])
mstats.register("avg", numpy.mean)
mstats.register("size", lambda ind: len(ind))

population, logbook = algorithms.eaSimple(population, toolbox, cxpb=0.8, mutpb=0.2,
                                           ngen=50, stats=mstats, halloffame=hof, verbose=True)

# Print best individual and its fitness value
best_ind = hof[0]
print(f"Best individual: {best_ind}")
print(f"Fitness: {eval_fitness(best_ind)}")
