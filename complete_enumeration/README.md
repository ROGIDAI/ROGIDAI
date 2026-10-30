# Complete Enumeration

## 1. Overview

This program performs Complete Enumeration (CE) to identify the exact Pareto-optimal solutions for the facility location problem.

It evaluates all combinations of \(k\) facilities from \(n\) candidate locations using the selected behavior models: Binary, Proportional, and Pareto-Huff.

The resulting exact Pareto fronts serve as reference solutions for verifying the performance and solution quality of MAS, NSGA-II, MOEA/D, and other optimization algorithms.

The program runs sequentially using Python.

## 2. Requirements and Execution

**Requirements:** Python 3 and NumPy.

Install NumPy if needed:

```bash
pip install numpy
```

Run the program from the **repository root directory**:

```bash
python -m complete_enumeration.main
```

## 3. Configuration

Experiment settings are defined in `complete_enumeration/settings.py`.

| Setting | Description | Example |
|---|---|---|
| `BEHAVIOR_MODELS` | Select behavior models | `["binary", "proportional"]` |
| `K_VALUES` | Number of facilities to select | `[2, 3, 4]` |
| `TEST_CASES` | Test cases to execute | `["TC1", "TC2"]` |
| `VERBOSE` | Display execution progress | `False` |

**2BM configuration:**
```python
BEHAVIOR_MODELS = ["binary", "proportional"]
```

**3BM configuration:**
```python
BEHAVIOR_MODELS = ["binary", "proportional", "pareto_huff"]
```

Multiple values of \(k\) and test cases can be selected by modifying their lists.

## 4. Output Files

Results are saved automatically under `outputs/complete_enumeration/`.

**`pareto_front.csv`**

Contains the exact Pareto-optimal facility combinations and their objective utility values.

Example:
```text
outputs/complete_enumeration/2BM/k3/TC1/pareto_front.csv
```

**`summary.csv`**

Contains the test case, behavior models, \(k\), number of candidates, total combinations, scalar objective evaluations, Pareto-front size, and execution time.

Location:
```text
outputs/complete_enumeration/summary.csv
```

## 5. Verification and Notes

- Different facility combinations with identical objective values are retained.
- The generated Pareto fronts can be used to verify solutions obtained by MAS and other optimization algorithms.
- Execution time includes enumeration, objective evaluations, and Pareto-front updates. Data loading and CSV writing are excluded.
- Computation time increases considerably for larger values of k.
