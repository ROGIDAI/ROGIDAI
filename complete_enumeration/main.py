import csv
from itertools import combinations
from math import comb
from pathlib import Path
from time import perf_counter

from objectives.attractiveness import load_data
from objectives.binary import binary_utility
from objectives.proportional import proportional_utility
from objectives.pareto_huff import pareto_huff_utility
from complete_enumeration.settings import BEHAVIOR_MODELS, K_VALUES, TEST_CASES, VERBOSE


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "complete_enumeration"

MODELS = {
    "binary": binary_utility,
    "proportional": proportional_utility,
    "pareto_huff": pareto_huff_utility,
}


def dominates(a, b):
    return a != b and all(x >= y for x, y in zip(a, b))


def update_front(front, solution, values):
    if any(dominates(old_values, values) for _, old_values in front):
        return

    front[:] = [
        (old_solution, old_values)
        for old_solution, old_values in front
        if not dominates(values, old_values)
    ]
    front.append((solution, values))


def save_front(front, directory, models, k):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "pareto_front.csv"
    temp = path.with_suffix(".tmp")

    with temp.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([*(f"facility_{i + 1}" for i in range(k)),
                         *(f"{model}_utility" for model in models)])

        for solution, values in sorted(front):
            writer.writerow([*solution, *(format(value, ".17g") for value in values)])

    temp.replace(path)


def save_summary(row):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "summary.csv"
    rows = []

    if path.exists():
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

    keys = ("behavior_models", "k", "test_case")
    rows = [old for old in rows if any(old[key] != row[key] for key in keys)]
    rows.append(row)
    rows.sort(key=lambda item: (item["behavior_models"], int(item["k"]), item["test_case"]))

    temp = path.with_suffix(".tmp")

    with temp.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(rows)

    temp.replace(path)


def main():
    if BEHAVIOR_MODELS not in (["binary", "proportional"],
                               ["binary", "proportional", "pareto_huff"]):
        raise ValueError("Select Binary/Proportional or all three behavior models")

    if not TEST_CASES or not K_VALUES:
        raise ValueError("Select at least one test case and K value")

    functions = [MODELS[name] for name in BEHAVIOR_MODELS]
    label = f"{len(functions)}BM"

    for test_case in TEST_CASES:
        data = load_data(test_case)
        n = data.qualities.size

        for k in K_VALUES:
            if not 1 <= k <= n:
                raise ValueError(f"Invalid K={k} for {test_case}")

            total = comb(n, k)
            front = []
            start = perf_counter()

            for count, solution in enumerate(combinations(range(n), k), start=1):
                values = tuple(function(solution, data) for function in functions)
                update_front(front, solution, values)

                if VERBOSE and count % 100000 == 0:
                    print(f"{test_case}, K={k}: {count:,}/{total:,}", flush=True)

            runtime = perf_counter() - start
            directory = OUTPUT / label / f"k{k}" / test_case

            save_front(front, directory, BEHAVIOR_MODELS, k)

            save_summary({
                "behavior_models": label,
                "k": k,
                "test_case": test_case,
                "candidates": n,
                "combinations": total,
                "scalar_evaluations": total * len(functions),
                "pareto_solutions": len(front),
                "runtime_seconds": f"{runtime:.6f}",
            })

            print(f"{test_case} | {label} | K={k} | Pareto={len(front)} | {runtime:.2f}s")


if __name__ == "__main__":
    main()