"""pymoo-based MOEA/D baseline for the MAS4FLP two-objective benchmark.
References: Zhang & Li (2007), DOI 10.1109/TEVC.2007.892759;
            Blank & Deb (2020), DOI 10.1109/ACCESS.2020.2990567.
Dependency: pymoo==0.6.1.6.
"""

import csv
import sys
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from objectives.attractiveness import load_data
from objectives.binary import binary_utility
from objectives.proportional import proportional_utility
from established_algorithms.moead import settings

OUTPUT = ROOT / "outputs" / "established_algorithms" / settings.OUTPUT_NAME
MODELS = {"binary": binary_utility, "proportional": proportional_utility}


def dominates(a, b):
    """Strict Pareto dominance for maximization."""
    return all(x >= y for x, y in zip(a, b)) and any(
        x > y for x, y in zip(a, b)
    )


def update_archive(archive, solution, values):
    """Unbounded non-dominated archive; distinct tied solutions are retained."""
    if solution in archive:
        return
    if any(dominates(v, values) for v in archive.values()):
        return
    for x, v in list(archive.items()):
        if dominates(values, v):
            del archive[x]
    archive[solution] = values


def canonical(x, n, k):
    """Check and canonicalize a fixed-cardinality integer location subset."""
    a = np.asarray(x).reshape(-1)
    if len(a) != k or not np.all(np.isfinite(a)):
        raise ValueError("Infeasible fixed-k solution")
    b = a.astype(int)
    if not np.array_equal(a, b) or np.any(b < 0) or np.any(b >= n):
        raise ValueError("Facility indices must be valid integers")
    if len(set(b.tolist())) != k:
        raise ValueError("Facility indices must be distinct")
    return tuple(sorted(int(v) for v in b))


def sample_subset(n, k, rng):
    return np.sort(rng.choice(n, size=k, replace=False).astype(int))


def crossover_subset(a, b, k, rng):
    """Older operator: keep common facilities, fill from symmetric difference."""
    common = np.intersect1d(a, b)
    different = np.setxor1d(a, b)
    needed = k - len(common)
    if needed:
        common = np.concatenate([
            common, rng.choice(different, size=needed, replace=False)
        ])
    return np.sort(common.astype(int))


def mutate_subset(x, n, rng, per_facility_probability=None):
    """Older operator: independently replace each selected facility at 1/k."""
    child = np.asarray(x, dtype=int).copy()
    k = len(child)
    rate = (1.0 / k) if per_facility_probability is None else per_facility_probability
    indices = np.flatnonzero(rng.random(k) < rate)
    if len(indices):
        selected = set(child.tolist())
        available = [j for j in range(n) if j not in selected]
        replacements = rng.choice(available, size=len(indices), replace=False)
        child[indices] = replacements
    return np.sort(child)


def make_pymoo_classes():
    """Load pymoo only when executing optimization, not when testing helpers."""
    try:
        import pymoo
        from pymoo.algorithms.moo.moead import MOEAD
        from pymoo.core.problem import ElementwiseProblem
        from pymoo.core.sampling import Sampling
        from pymoo.core.crossover import Crossover
        from pymoo.core.mutation import Mutation
        from pymoo.core.repair import Repair
    except ImportError as e:
        raise ModuleNotFoundError(
            "Install pymoo: python -m pip install pymoo==0.6.1.6"
        ) from e

    # Pin the dependency: pymoo's internal MOEA/D generator is subclassed.
    if pymoo.__version__ != "0.6.1.6":
        raise RuntimeError(
            f"Expected pymoo==0.6.1.6; installed {pymoo.__version__}. "
            "Install the pinned version or validate this adapter again."
        )

    class FacilityProblem(ElementwiseProblem):
        def __init__(self, data, k, functions):
            self.facility_data = data  # do not use self.data: pymoo reserves it
            self.k = k
            self.n_candidates = int(data.qualities.size)
            self.functions = functions
            self.seen = set()
            self.history = {}
            self.archive = {}
            self.checkpoints = {}
            super().__init__(
                n_var=k, n_obj=len(functions), n_ieq_constr=0,
                xl=np.zeros(k, dtype=int),
                xu=np.full(k, self.n_candidates - 1, dtype=int),
                vtype=int,
            )

        def _evaluate(self, x, out, *args, **kwargs):
            solution = canonical(x, self.n_candidates, self.k)
            if solution in self.seen:
                raise RuntimeError(f"Duplicate candidate reached evaluator: {solution}")
            values = tuple(float(fn(solution, self.facility_data)) for fn in self.functions)
            if not np.all(np.isfinite(values)):
                raise ArithmeticError("Non-finite objective utility")
            self.seen.add(solution)
            self.history[solution] = values
            update_archive(self.archive, solution, values)
            scalar_calls = len(self.history) * len(self.functions)
            if scalar_calls in settings.CHECKPOINT_SCALAR_EVALUATIONS:
                self.checkpoints[scalar_calls] = self.archive.copy()
            out["F"] = -np.asarray(values, dtype=float)  # pymoo minimizes

    class UniqueSampling(Sampling):
        def _do(self, problem, n_samples, *args, random_state=None, **kwargs):
            rng = random_state if random_state is not None else np.random
            rows, seen = [], set()
            while len(rows) < n_samples:
                x = sample_subset(problem.n_candidates, problem.k, rng)
                key = tuple(x.tolist())
                if key not in seen:
                    rows.append(x)
                    seen.add(key)
            return np.asarray(rows, dtype=int)

    class SubsetCrossover(Crossover):
        def __init__(self):
            super().__init__(n_parents=2, n_offsprings=2, prob=settings.P_CROSSOVER)

        def _do(self, problem, X, *args, random_state=None, **kwargs):
            rng = random_state if random_state is not None else np.random
            Y = np.empty((2, X.shape[1], problem.k), dtype=int)
            for j in range(X.shape[1]):
                Y[0, j] = crossover_subset(X[0, j], X[1, j], problem.k, rng)
                Y[1, j] = crossover_subset(X[0, j], X[1, j], problem.k, rng)
            return Y

    class SubsetMutation(Mutation):
        def __init__(self):
            super().__init__(prob=settings.P_MUTATION)

        def _do(self, problem, X, *args, random_state=None, **kwargs):
            rng = random_state if random_state is not None else np.random
            return np.asarray([
                mutate_subset(x, problem.n_candidates, rng,
                              settings.REPLACEMENT_PROBABILITY) for x in X
            ], dtype=int)

    class SubsetRepair(Repair):
        def _do(self, problem, X, *args, random_state=None, **kwargs):
            # The operators already preserve k distinct indices.
            return np.asarray([
                canonical(x, problem.n_candidates, problem.k) for x in X
            ], dtype=int)

    class HistoricalMOEAD(MOEAD):
        """Older pymoo MOEA/D: only its duplicate-prevention loop is adapted."""
        def __init__(self, problem, ref_dirs, budget_candidates):
            self.history_problem = problem
            self.max_candidates = budget_candidates
            self.duplicate_proposals = 0
            self.offspring_evaluations = 0
            super().__init__(
                ref_dirs=ref_dirs,
                n_neighbors=settings.NEIGHBORHOOD_SIZE,
                prob_neighbor_mating=settings.NEIGHBORHOOD_MATING_PROBABILITY,
                decomposition=None,  # pymoo's 2D default = Tchebicheff
                sampling=UniqueSampling(),
                crossover=SubsetCrossover(),
                mutation=SubsetMutation(),
                repair=SubsetRepair(),
            )

        def _setup(self, problem, **kwargs):
            if problem is not self.history_problem:
                raise RuntimeError("MOEA/D must use the same problem/history object")
            return super()._setup(problem, **kwargs)

        def _initialize_advance(self, infills=None, **kwargs):
            result = super()._initialize_advance(infills=infills, **kwargs)
            if len(self.history_problem.history) != len(self.pop):
                raise RuntimeError("Initial MOEA/D population was not unique")
            return result

        def _next(self):
            pop = self.pop
            for index in self.random_state.permutation(len(pop)):
                # Supports non-generation-aligned budgets (e.g. 5,119).
                if len(self.history_problem.history) >= self.max_candidates:
                    return

                # As in the earlier code, choose parents ONCE per subproblem.
                parents = self.selection.do(
                    self.problem, pop, 1, self.mating.crossover.n_parents,
                    neighbors=[self.neighbors[index]],
                    random_state=self.random_state,
                )
                offspring = None
                for _ in range(settings.DUPLICATE_LIMIT):
                    generated = self.mating.do(
                        self.problem, pop, 1, parents=parents,
                        n_max_iterations=1, random_state=self.random_state,
                    )
                    if generated is None or len(generated) == 0:
                        continue
                    proposed = self.random_state.choice(generated)
                    solution = canonical(
                        proposed.X, self.problem.n_candidates, self.problem.k
                    )
                    if solution in self.history_problem.seen:
                        self.duplicate_proposals += 1
                        continue
                    offspring = proposed
                    break

                if offspring is None:
                    raise RuntimeError(
                        "MOEA/D exceeded its duplicate retry limit without "
                        "finding a new candidate. No uniform-random fallback "
                        "is used (matching the earlier implementation). "
                        f"subproblem={index}; evaluated={len(self.history_problem.history)}"
                    )

                offspring = yield offspring
                self.offspring_evaluations += 1
                self.ideal = np.min(np.vstack((self.ideal, offspring.F)), axis=0)
                self._replace(index, offspring)  # standard pymoo MOEA/D update

    return FacilityProblem, HistoricalMOEAD


def load_reference(label, k, case):
    path = (ROOT / "outputs" / "complete_enumeration" / label
            / f"k{k}" / case / "pareto_front.csv")
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return {
            tuple(int(row[f"facility_{i + 1}"]) for i in range(k))
            for row in csv.DictReader(f)
        }


def save_front(archive, directory, models, k):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "pareto_front.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            *(f"facility_{i + 1}" for i in range(k)),
            *(f"{model}_utility" for model in models),
        ])
        for x, values in sorted(archive.items()):
            writer.writerow([*x, *(format(v, ".17g") for v in values)])


def run_one(case, k, seed, budget, Problem=None, Algorithm=None):
    """Execute one independent trial with a fresh optimizer and history."""
    Problem, Algorithm = (Problem, Algorithm) if Problem is not None else make_pymoo_classes()
    from pymoo.optimize import minimize
    data = load_data(case)
    models = tuple(settings.BEHAVIOR_MODELS)
    functions = [MODELS[model] for model in models]
    n = int(data.qualities.size)
    m = len(models)
    if m != 2 or budget % m or not 1 <= k < n:
        raise ValueError("Only 2BM and divisible scalar budgets are supported")
    target = budget // m
    if target < settings.POP_SIZE or target > comb(n, k):
        raise ValueError("Invalid candidate evaluation budget")
    problem = Problem(data, k, functions)
    # A uniform simplex lattice in two objectives, including both endpoints.
    weights = np.asarray([
        (i / (settings.POP_SIZE - 1), 1.0 - i / (settings.POP_SIZE - 1))
        for i in range(settings.POP_SIZE)
    ], dtype=float)
    algorithm = Algorithm(problem, weights, target)
    start = perf_counter()
    result = minimize(
        problem, algorithm, termination=("n_eval", target),
        seed=int(seed), verbose=settings.VERBOSE,
        copy_algorithm=False, save_history=False,
    )
    runtime = perf_counter() - start

    if len(problem.history) != target or result.algorithm.evaluator.n_eval != target:
        raise RuntimeError(
            f"Evaluation accounting failed: target={target}, "
            f"unique={len(problem.history)}, pymoo={result.algorithm.evaluator.n_eval}"
        )
    reference = load_reference("2BM", k, case)
    recovered = set(problem.archive) == reference
    directory = (OUTPUT / "2BM" / f"k{k}" / case
                 / f"budget_{budget}" / f"seed_{seed}")
    save_front(problem.archive, directory, models, k)
    for checkpoint, snapshot in problem.checkpoints.items():
        save_front(snapshot, directory / "checkpoints" / f"scalar_{checkpoint}",
                   models, k)
    return {
        "behavior_models": "2BM", "k": k, "test_case": case,
        "seed": seed, "scalar_budget": budget,
        "population_size": settings.POP_SIZE,
        "pymoo_version": "0.6.1.6",
        "reference_directions": settings.POP_SIZE,
        "reference_direction_method": "uniform_simplex_2d",
        "decomposition": "pymoo_Tchebicheff",
        "replacement_rule": "standard_pymoo_neighbor_only_unlimited",
        "generations": int(result.algorithm.n_gen),
        "neighborhood_size": settings.NEIGHBORHOOD_SIZE,
        "neighborhood_mating_probability": settings.NEIGHBORHOOD_MATING_PROBABILITY,
        "p_crossover": settings.P_CROSSOVER,
        "p_mutation": settings.P_MUTATION,
        "per_facility_mutation_probability": 1.0/k if settings.REPLACEMENT_PROBABILITY is None else settings.REPLACEMENT_PROBABILITY,
        "duplicate_limit": settings.DUPLICATE_LIMIT,
        "duplicate_policy": "same_parents_retries_no_fallback",
        "duplicate_proposals": algorithm.duplicate_proposals,
        "uniform_fallbacks": 0,
        "candidate_evaluations": len(problem.history),
        "scalar_evaluations": len(problem.history) * m,
        "pareto_solutions": len(problem.archive),
        "reference_solutions": len(reference),
        "reference_recovered": len(set(problem.archive) & reference),
        "exact_recovery": int(recovered),
        "runtime_seconds": f"{runtime:.6f}",
    }


def save_summary(rows):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "summary.csv"
    keys = ("behavior_models", "k", "test_case", "seed", "scalar_budget")
    existing = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    merged = {tuple(str(row[k]) for k in keys): row for row in existing}
    for row in rows:
        merged[tuple(str(row[k]) for k in keys)] = row
    combined = list(merged.values())
    combined.sort(key=lambda r: (int(r["scalar_budget"]), r["test_case"], int(r["seed"])))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(combined)


def main():
    if settings.BEHAVIOR_MODELS != ["binary", "proportional"]:
        raise ValueError("Use Binary and Proportional objectives")
    if settings.DECOMPOSITION != "tchebycheff":
        raise ValueError("This adapter uses pymoo's original Tchebicheff")
    if settings.POP_SIZE < 2 or not 2 <= settings.NEIGHBORHOOD_SIZE <= settings.POP_SIZE:
        raise ValueError("Invalid MOEA/D population/neighborhood")
    if settings.DUPLICATE_LIMIT < 1:
        raise ValueError("Invalid retry limit")
    if any(not 0 <= p <= 1 for p in [
        settings.P_CROSSOVER, settings.P_MUTATION,
        settings.NEIGHBORHOOD_MATING_PROBABILITY,
    ]):
        raise ValueError("Invalid probability")
    if not settings.SEEDS or not settings.TEST_CASES or not settings.K_VALUES:
        raise ValueError("Empty test configuration")
    Problem, Algorithm = make_pymoo_classes()
    total, exact = 0, 0
    for case in settings.TEST_CASES:
        case_rows = []
        for k in settings.K_VALUES:
            for seed in settings.SEEDS:
                row = run_one(case, k, seed, settings.SCALAR_BUDGET, Problem, Algorithm)
                case_rows.append(row)
                total += 1
                exact += row["exact_recovery"]
        save_summary(case_rows)
        print(f"{case}: exact {sum(x['exact_recovery'] for x in case_rows)}/{len(case_rows)}; "
              f"scalar budget {settings.SCALAR_BUDGET}", flush=True)
    print(f"COMPLETED: exact {exact}/{total}")


if __name__ == "__main__":
    main()
