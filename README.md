# MAS4FLP - Multi-Agent System for Facility Location Problem

This Python project selects solution of **k number of facilities from 283 candidate locations** for **440 demand regions**. Solutions are evaluated using **Binary**, **Proportional**, and optionally **Pareto-Huff** customer-behavior models. The project supports two objectives (2BM) or three objectives (3BM).

## 1. Project structure

```text
ROGIDAI/
├── data/                     # Demand, distances, quality cases, learned probabilities
├── data_set_preparation/     # Scripts for generating additional quality cases
├── objectives/              # Binary, Proportional and Pareto-Huff utilities
├── complete_enumeration/    # Exact Pareto-front calculation
├── agent_learning/          # Learn candidate-selection probabilities
├── mas/                     # Multi-agent system
├── established_algorithms/
│   ├── nsga2/               # NSGA-II baseline
│   └── moead/               # MOEA/D baseline
└── outputs/                 # Saved results
```

## 2. Datasets

`data/` contains `regionDemands.dat`, `regionDistancesToCity.dat`, and a `cityQualities.dat` file for each test case:

- **TC1–TC6:** Original quality datasets.
- **U01–U04:** Independent uniform qualities in the range [1, 5].
- **NU01–NU04:** Nonuniform qualities from a Beta(2, 5) distribution scaled to [1, 5].
- **SC01–SC04:** Spatially correlated qualities based on candidate-to-candidate road distances.

To regenerate U, NU and SC cases, run the three `generate_*.py` scripts from inside `data_set_preparation/`. They write to `data_set_preparation/data/`; copy the generated case folders into the main `data/` directory before running the algorithms. The original TC1-TC6 - and shared demand/distance files are supplied separately.

## 3. Implemented algorithms

| Algorithm | Purpose |
|---|---|
| **Complete Enumeration (CE)** | Evaluates every feasible k number of candidate locations solution and saves the exact Pareto front. |
| **Agent Learning** | Independently learns candidate-selection probabilities for each behavior model. |
| **MAS4FLP** | Agents propose solutions using learned probabilities; a base agent checks duplicates, cross-evaluates proposals, and maintains a set of non-dominated solutions. |
| **NSGA-II** | Evolutionary baseline using non-dominated sorting, crowding distance, crossover, and mutation. |
| **MOEA/D** | Decomposition-based evolutionary baseline implemented with `pymoo`; currently supports 2BM. |

MAS4FLP uses **in-process, custom FIPA-ACL-style messages**; it is not a distributed/networked implementation. The `DUPLICATE_LIMIT` setting triggers uniform sampling after repeated local duplicates; `None` disables this fallback.

## 4. Install and run

Use **Python 3**. From the repository root, install dependencies:

```bash
python -m pip install numpy scipy pymoo==0.6.1.6
```

Run the required modules from the **repository root**:

```bash
python -m complete_enumeration.main
python -m agent_learning.main
python -m mas.main
python -m established_algorithms.nsga2.main
python -m established_algorithms.moead.main
```

**Suggested workflow:** Prepare data → run CE for exact reference fronts → run Agent Learning → run MAS → run NSGA-II/MOEA/D for comparison. Precomputed learned probabilities and reference fronts can be reused when available.

## 5. Settings and outputs

Edit each algorithm's `settings.py` to select **behavior models, k, test cases, seeds, and evaluation limits**. MAS also uses `PROBABILITY_SEED`, `MAX_ITERS`, `DUPLICATE_LIMIT. The MAS probability seed must match a folder created by Agent Learning.

| Component | Main outputs |
|---|---|
| CE | `outputs/complete_enumeration/` - exact `pareto_front.csv` and summary |
| Agent Learning | `data/learned_probabilities/k{k}/{case}/seed_{seed}/` and `outputs/agent_learning/summary.csv` |
| MAS | `outputs/mas/` - summary, `mas_archive.csv`, `strict_front.csv`, `evaluated_solutions.csv`, `agent_statistics.csv` |
| NSGA-II | `outputs/established_algorithms/nsga2/` |
| MOEA/D | `outputs/established_algorithms/<OUTPUT_NAME>/` (`OUTPUT_NAME` is set in `moead/settings.py`) |

**Reproducibility:** Keep the same datasets and seeds for comparisons. Verify exact recovery by comparing **facility combinations and objective values**, not only Pareto-front sizes. Report **offline learning evaluations together with MAS search evaluations** when comparing total computational budgets. The scripts run only the cases currently selected in their settings files.
