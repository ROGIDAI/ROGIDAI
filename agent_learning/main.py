import csv
import random
from pathlib import Path
from time import perf_counter

import numpy as np

from objectives.attractiveness import load_data
from objectives.binary import binary_utility
from objectives.proportional import proportional_utility
from objectives.pareto_huff import pareto_huff_utility
from agent_learning.settings import (
    BEHAVIOR_MODELS, K_VALUES, TEST_CASES, SEEDS, EPISODES,
    ALPHA, BETA, EXPORT_TEMPERATURE, VERBOSE,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_OUTPUT = ROOT / "data" / "learned_probabilities"
SUMMARY = ROOT / "outputs" / "agent_learning" / "summary.csv"

MODELS = {
    "binary": (binary_utility, 1),
    "proportional": (proportional_utility, 2),
    "pareto_huff": (pareto_huff_utility, 3),
}


def softmax(ranks, available, temperature=1.0):
    values = ranks[available] / temperature
    weights = np.exp(values - values.max())
    probabilities = weights / weights.sum()
    if len(probabilities) > 1:
        probabilities[-1] = 1.0 - float(probabilities[:-1].sum())
    probabilities = np.clip(probabilities, 0.0, None)
    return probabilities / probabilities.sum()


def sample_solution(ranks, k, rng):
    available = list(range(len(ranks)))
    selected = []
    chosen = []

    for _ in range(k):
        probabilities = softmax(ranks, available)
        probabilities = probabilities / probabilities.sum()
        draw = rng.random()
        cumulative = 0.0
        index = len(available) - 1

        for i, probability in enumerate(probabilities):
            cumulative += float(probability)
            if draw < cumulative:
                index = i
                break

        candidate = available.pop(index)
        selected.append(candidate)
        chosen.append((candidate, float(probabilities[index])))

    return tuple(sorted(selected)), chosen


def train(data, k, seed, evaluator):
    ranks = np.zeros(data.qualities.size, dtype=float)
    rng = random.Random(seed)
    baseline = 0.0
    best_reward = float("-inf")
    seen = set()
    start = perf_counter()

    for episode in range(1, EPISODES + 1):
        solution, chosen = sample_solution(ranks, k, rng)
        seen.add(solution)
        reward = evaluator(solution, data)
        best_reward = max(best_reward, reward)
        advantage = reward - baseline
        baseline = (1.0 - BETA) * baseline + BETA * reward

        for candidate, probability in chosen:
            ranks[candidate] += ALPHA * advantage * (1.0 - probability)

        if VERBOSE and episode % 10000 == 0:
            print(f"  Episode {episode:,}/{EPISODES:,}", flush=True)

    runtime = perf_counter() - start
    return ranks, best_reward, len(seen), runtime


def save_probabilities(path, probabilities):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for candidate, probability in enumerate(probabilities):
            file.write(f"{candidate} {probability:.17g}\n")


def save_summary(row):
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if SUMMARY.exists():
        with SUMMARY.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

    keys = ("test_case", "k", "seed", "behavior")
    rows = [old for old in rows if any(old[key] != str(row[key]) for key in keys)]
    rows.append(row)
    rows.sort(key=lambda item: (item["test_case"], int(item["k"]), int(item["seed"]), item["behavior"]))

    with SUMMARY.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not BEHAVIOR_MODELS or any(model not in MODELS for model in BEHAVIOR_MODELS):
        raise ValueError("Invalid behavior model selection")
    if not K_VALUES or not TEST_CASES or not SEEDS:
        raise ValueError("Select at least one K value, test case, and seed")
    if EPISODES <= 0 or ALPHA <= 0 or not 0 < BETA <= 1 or EXPORT_TEMPERATURE <= 0:
        raise ValueError("Invalid learning parameters")

    for test_case in TEST_CASES:
        data = load_data(test_case)
        for k in K_VALUES:
            if not 1 <= k <= data.qualities.size:
                raise ValueError(f"Invalid K={k} for {test_case}")
            for seed in SEEDS:
                directory = DATA_OUTPUT / f"k{k}" / test_case / f"seed_{seed}"

                for behavior in BEHAVIOR_MODELS:
                    evaluator, agent_id = MODELS[behavior]
                    learning_seed = seed * 100 + agent_id

                    ranks, best, unique, runtime = train(
                        data, k, learning_seed, evaluator
                    )

                    probabilities = softmax(
                        ranks, np.arange(len(ranks)), EXPORT_TEMPERATURE
                    )

                    path = directory / f"ranked_candidates_{behavior}.txt"
                    save_probabilities(path, probabilities)

                    save_summary({
                        "test_case": test_case,
                        "k": k,
                        "seed": seed,
                        "learning_seed": learning_seed,
                        "behavior": behavior,
                        "episodes": EPISODES,
                        "alpha": ALPHA,
                        "beta": BETA,
                        "export_temperature": EXPORT_TEMPERATURE,
                        "best_reward": f"{best:.17g}",
                        "unique_solutions": unique,
                        "duplicate_solutions": EPISODES - unique,
                        "scalar_evaluations": EPISODES,
                        "runtime_seconds": f"{runtime:.6f}",
                    })

                    print(
                        f"{test_case} | K={k} | seed={seed} | {behavior} | "
                        f"unique={unique:,} | {runtime:.2f}s"
                    )


if __name__ == "__main__":
    main()