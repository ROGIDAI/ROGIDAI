import csv
import random
import sys
from math import comb
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from objectives.attractiveness import load_data
from objectives.binary import binary_utility
from objectives.proportional import proportional_utility
from objectives.pareto_huff import pareto_huff_utility
from established_algorithms.nsga2.settings import (
    BEHAVIOR_MODELS, K_VALUES, TEST_CASES, SEEDS,
    POP_SIZE, P_CROSSOVER, P_MUTATION, DUPLICATE_LIMIT, SCALAR_BUDGET, VERBOSE,
)

OUTPUT = ROOT / "outputs" / "established_algorithms" / "nsga2"
MODELS = {
    "binary": binary_utility,
    "proportional": proportional_utility,
    "pareto_huff": pareto_huff_utility,
}


def dominates(a, b):
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def non_dominated_sort(values):
    n = len(values)
    dominated = [[] for _ in range(n)]
    counts = [0] * n
    first = []

    for p in range(n):
        for q in range(p + 1, n):
            if dominates(values[p], values[q]):
                dominated[p].append(q)
                counts[q] += 1
            elif dominates(values[q], values[p]):
                dominated[q].append(p)
                counts[p] += 1

    for p in range(n):
        if counts[p] == 0:
            first.append(p)

    fronts = []
    while first:
        fronts.append(first)
        following = []
        for p in first:
            for q in dominated[p]:
                counts[q] -= 1
                if counts[q] == 0:
                    following.append(q)
        first = following
    return fronts


def crowding_distance(values, front):
    distances = {i: 0.0 for i in front}
    if len(front) <= 2:
        return {i: float("inf") for i in front}

    for m in range(len(values[0])):
        ordered = sorted(front, key=lambda i: values[i][m])
        distances[ordered[0]] = float("inf")
        distances[ordered[-1]] = float("inf")
        span = values[ordered[-1]][m] - values[ordered[0]][m]
        if span > 0:
            for j in range(1, len(ordered) - 1):
                i = ordered[j]
                distances[i] += (values[ordered[j + 1]][m] - values[ordered[j - 1]][m]) / span
    return distances


def tournament(ranks, distances, rng):
    a, b = rng.sample(range(len(ranks)), 2)
    if ranks[a] != ranks[b]:
        return a if ranks[a] < ranks[b] else b
    if distances[a] != distances[b]:
        return a if distances[a] > distances[b] else b
    return rng.choice((a, b))


def crossover(parent1, parent2, k, rng):
    choices = sorted(set(parent1) | set(parent2))
    return tuple(sorted(rng.sample(choices, k)))


def mutate(solution, n, rng):
    child = list(solution)
    position = rng.randrange(len(child))
    available = [j for j in range(n) if j not in child]
    child[position] = rng.choice(available)
    return tuple(sorted(child))


def update_archive(archive, solution, values):
    if solution in archive or any(dominates(old, values) for old in archive.values()):
        return
    for old_solution, old_values in list(archive.items()):
        if dominates(values, old_values):
            del archive[old_solution]
    archive[solution] = values


def run_nsga2(data, k, functions, budget, seed):
    rng = random.Random(seed)
    n = data.qualities.size
    max_evaluations = min(budget // len(functions), comb(n, k))
    archive = {}
    evaluated = set()
    duplicate_proposals = 0
    uniform_fallbacks = 0
    candidate_evaluations = 0
    start = perf_counter()

    def evaluate(solution):
        nonlocal candidate_evaluations
        evaluated.add(solution)
        values = tuple(function(solution, data) for function in functions)
        candidate_evaluations += 1
        update_archive(archive, solution, values)
        return values

    population = []
    used = set()
    while len(population) < POP_SIZE:
        solution = tuple(sorted(rng.sample(range(n), k)))
        if solution not in used:
            used.add(solution)
            population.append(solution)
    fitness = [evaluate(solution) for solution in population]
    generations = 0

    while candidate_evaluations < max_evaluations:
        fronts = non_dominated_sort(fitness)
        ranks = [0] * len(population)
        distances = [0.0] * len(population)
        for rank, front in enumerate(fronts):
            crowding = crowding_distance(fitness, front)
            for i in front:
                ranks[i] = rank
                distances[i] = crowding[i]

        offspring = []
        offspring_fitness = []
        count = min(POP_SIZE, max_evaluations - candidate_evaluations)
        for _ in range(count):
            child = None
            for _ in range(DUPLICATE_LIMIT):
                parent1 = population[tournament(ranks, distances, rng)]
                parent2 = population[tournament(ranks, distances, rng)]
                proposal = crossover(parent1, parent2, k, rng) if rng.random() < P_CROSSOVER else parent1
                if rng.random() < P_MUTATION:
                    proposal = mutate(proposal, n, rng)
                if proposal not in evaluated:
                    child = proposal
                    break
                duplicate_proposals += 1
            if child is None:
                uniform_fallbacks += 1
                while True:
                    proposal = tuple(sorted(rng.sample(range(n), k)))
                    if proposal not in evaluated:
                        child = proposal
                        break
                    duplicate_proposals += 1
            offspring.append(child)
            offspring_fitness.append(evaluate(child))

        combined = population + offspring
        combined_fitness = fitness + offspring_fitness
        population, fitness = [], []
        for front in non_dominated_sort(combined_fitness):
            if len(population) + len(front) <= POP_SIZE:
                chosen = front
            else:
                crowding = crowding_distance(combined_fitness, front)
                chosen = sorted(front, key=lambda i: (-crowding[i], i))[:POP_SIZE - len(population)]
            for i in chosen:
                population.append(combined[i])
                fitness.append(combined_fitness[i])
            if len(population) == POP_SIZE:
                break
        generations += 1
        if VERBOSE and generations % 20 == 0:
            print(f"Generation {generations}: {candidate_evaluations} evaluations")

    runtime = perf_counter() - start
    return archive, duplicate_proposals, uniform_fallbacks, candidate_evaluations, generations, runtime


def load_reference(label, k, test_case):
    path = ROOT / "outputs" / "complete_enumeration" / label / f"k{k}" / test_case / "pareto_front.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Missing exact reference: {path}")
    with path.open(newline="", encoding="utf-8") as file:
        return {
            tuple(int(row[f"facility_{i + 1}"]) for i in range(k))
            for row in csv.DictReader(file)
        }


def save_front(archive, directory, models, k):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "pareto_front.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([*(f"facility_{i + 1}" for i in range(k)),
                         *(f"{model}_utility" for model in models)])
        for solution, values in sorted(archive.items()):
            writer.writerow([*solution, *(format(value, ".17g") for value in values)])


def save_summary(row):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "summary.csv"
    rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
    keys = ("behavior_models", "k", "test_case", "seed", "scalar_budget")
    rows = [old for old in rows if any(old[key] != str(row[key]) for key in keys)]
    rows.append({key: str(value) for key, value in row.items()})
    rows.sort(key=lambda r: (r["behavior_models"], int(r["k"]), r["test_case"], int(r["seed"]), int(r["scalar_budget"])))
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    if BEHAVIOR_MODELS not in (["binary", "proportional"],
                               ["binary", "proportional", "pareto_huff"]):
        raise ValueError("Choose 2BM or 3BM behavior models")
    if not TEST_CASES or not K_VALUES or not SEEDS:
        raise ValueError("Choose test cases, K values and seeds")
    if POP_SIZE < 2 or DUPLICATE_LIMIT < 1 or not 0 <= P_CROSSOVER <= 1 or not 0 <= P_MUTATION <= 1:
        raise ValueError("Invalid NSGA-II parameters")
    if SCALAR_BUDGET % len(BEHAVIOR_MODELS) or SCALAR_BUDGET < POP_SIZE * len(BEHAVIOR_MODELS):
        raise ValueError("Budget must be divisible by the objective count and cover initial population")

    label = f"{len(BEHAVIOR_MODELS)}BM"
    functions = [MODELS[name] for name in BEHAVIOR_MODELS]
    for test_case in TEST_CASES:
        data = load_data(test_case)
        n = data.qualities.size
        for k in K_VALUES:
            if not 1 <= k < n or comb(n, k) < POP_SIZE:
                raise ValueError(f"Invalid k={k} or population size for {test_case}")
            reference = load_reference(label, k, test_case)
            if not reference:
                raise ValueError(f"Empty reference front for {test_case}, k={k}")
            for seed in SEEDS:
                archive, duplicates, fallbacks, evaluations, generations, runtime = run_nsga2(
                    data, k, functions, SCALAR_BUDGET, seed
                )
                recovered = len(reference.intersection(archive))
                directory = (OUTPUT / label / f"k{k}" / test_case /
                             f"budget_{SCALAR_BUDGET}" / f"seed_{seed}")
                save_front(archive, directory, BEHAVIOR_MODELS, k)
                save_summary({
                    "behavior_models": label,
                    "k": k,
                    "test_case": test_case,
                    "seed": seed,
                    "population_size": POP_SIZE,
                    "p_crossover": P_CROSSOVER,
                    "p_mutation": P_MUTATION,
                    "duplicate_limit": DUPLICATE_LIMIT,
                    "scalar_budget": SCALAR_BUDGET,
                    "candidate_evaluations": evaluations,
                    "scalar_evaluations": evaluations * len(functions),
                    "unique_solutions": evaluations,
                    "duplicate_proposals": duplicates,
                    "uniform_fallbacks": fallbacks,
                    "generations": generations,
                    "pareto_solutions": len(archive),
                    "reference_solutions": len(reference),
                    "reference_recovered": recovered,
                    "exact_recovery": int(recovered == len(reference)),
                    "runtime_seconds": f"{runtime:.6f}",
                })
                print(f"{test_case} | {label} | k={k} | seed={seed} | "
                      f"recovered={recovered}/{len(reference)} | "
                      f"Pareto={len(archive)} | {runtime:.2f}s")


if __name__ == "__main__":
    main()