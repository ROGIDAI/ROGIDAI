import csv
import random
from pathlib import Path

from objectives.attractiveness import load_data
from mas.binary_agent import BinaryAgent
from mas.proportional_agent import ProportionalAgent
from mas.pareto_huff_agent import ParetoHuffAgent
from mas.base_agent import BaseAgent
from mas.settings import (
    BEHAVIOR_MODELS, K_VALUES, TEST_CASES, PROBABILITY_SEED,
    SEEDS, MAX_ITERS, DUPLICATE_LIMIT, PARETO_EPSILON, VERBOSE,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "mas"

AGENTS = {
    "binary": BinaryAgent,
    "proportional": ProportionalAgent,
    "pareto_huff": ParetoHuffAgent,
}


def save_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def save_summary(row):
    path = OUTPUT / "summary.csv"
    rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

    keys = ("behavior_models", "k", "test_case", "seed", "probability_seed",
            "max_iters", "duplicate_limit", "pareto_epsilon")
    rows = [old for old in rows if any(old[key] != str(row[key]) for key in keys)]
    rows.append(row)

    save_csv(path, row.keys(), ([item[key] for key in row] for item in rows))


def save_results(base, agents, models, k, directory):
    header = [*(f"facility_{i + 1}" for i in range(k)),
              *(f"{model}_utility" for model in models)]

    def front_rows(front):
        return [[*solution, *(f"{value:.17g}" for value in values)]
                for solution, values in sorted(front)]

    save_csv(directory / "mas_archive.csv", header, front_rows(base.archive))
    save_csv(directory / "strict_front.csv", header, front_rows(base.strict_front()))
    save_csv(directory / "evaluated_solutions.csv", ["iteration", *header],
             ([iteration + 1, *solution, *(f"{value:.17g}" for value in values)]
              for iteration, solution, values in base.evaluated))

    stat_names = list(agents[0].statistics())
    save_csv(directory / "agent_statistics.csv",
             ["agent_id", "behavior", *stat_names, "global_duplicates"],
             ([agent.agent_id, model, *agent.statistics().values(),
               base.global_duplicates[agent.agent_id]]
              for model, agent in zip(models, agents)))


def main():
    if BEHAVIOR_MODELS not in (["binary", "proportional"],
                               ["binary", "proportional", "pareto_huff"]):
        raise ValueError("Select Binary/Proportional or all three behavior models")
    if not K_VALUES or not TEST_CASES or not SEEDS or MAX_ITERS <= 0:
        raise ValueError("Invalid MAS experiment settings")
    if PARETO_EPSILON < 0:
        raise ValueError("Pareto epsilon must be nonnegative")

    label = f"{len(BEHAVIOR_MODELS)}BM"

    for test_case in TEST_CASES:
        data = load_data(test_case)
        for k in K_VALUES:
            if not 1 <= k <= data.qualities.size:
                raise ValueError(f"Invalid K={k} for {test_case}")

            probability_dir = (ROOT / "data" / "learned_probabilities" /
                               f"k{k}" / test_case / f"seed_{PROBABILITY_SEED}")

            for seed in SEEDS:
                rng = random.Random(seed)
                agents = [
                    AGENTS[model](data, probability_dir / f"ranked_candidates_{model}.txt",
                                  k, rng, DUPLICATE_LIMIT)
                    for model in BEHAVIOR_MODELS
                ]
                base = BaseAgent(agents, MAX_ITERS, PARETO_EPSILON, VERBOSE)
                base.run()

                directory = (OUTPUT / label / f"k{k}" / f"prob_seed_{PROBABILITY_SEED}" /
                             f"limit_{DUPLICATE_LIMIT}" / f"eps_{PARETO_EPSILON:g}" /
                             f"iters_{MAX_ITERS}" / test_case / f"seed_{seed}")
                save_results(base, agents, BEHAVIOR_MODELS, k, directory)

                evaluations = sum(agent.evaluation_count for agent in agents)
                save_summary({
                    "behavior_models": label,
                    "k": k,
                    "test_case": test_case,
                    "seed": seed,
                    "probability_seed": PROBABILITY_SEED,
                    "max_iters": MAX_ITERS,
                    "duplicate_limit": DUPLICATE_LIMIT,
                    "pareto_epsilon": PARETO_EPSILON,
                    "completed_iterations": base.completed_iterations,
                    "unique_solutions": len(base.evaluated),
                    "scalar_evaluations": evaluations,
                    "mas_archive_size": len(base.archive),
                    "strict_front_size": len(base.strict_front()),
                    "local_duplicates": sum(agent.local_duplicate_count for agent in agents),
                    "global_duplicates": sum(base.global_duplicates.values()),
                    "fallback_activations": sum(agent.fallback_activations for agent in agents),
                    "proposal_requests": base.proposal_requests,
                    "evaluation_requests": base.evaluation_requests,
                    "message_count": 2 * (base.proposal_requests + base.evaluation_requests) + len(agents),
                    "search_seconds": f"{base.search_seconds:.6f}",
                    "proposal_seconds": f"{base.proposal_seconds:.6f}",
                    "evaluation_seconds": f"{base.evaluation_seconds:.6f}",
                    "archive_seconds": f"{base.archive_seconds:.6f}",
                })

                print(f"{test_case} | {label} | K={k} | seed={seed} | "
                      f"Pareto={len(base.archive)} | {base.search_seconds:.2f}s")


if __name__ == "__main__":
    main()