# Agent Learning

## 1. Overview

This program trains candidate-selection probabilities for the facility location problem using independent learning agents based on Binary, Proportional, and Pareto-Huff behavior models.

Each agent learns candidate preferences through repeated solution generation, utility evaluation, and rank updates. The resulting probabilities are used by the Multi-Agent System (MAS) to generate facility-location proposals.

## 2. Requirements and Execution

**Requirements:** Python 3 and NumPy.

Install NumPy if needed:

```bash
pip install numpy
```

Run the program from the **repository root directory**:

```bash
python -m agent_learning.main
```

## 3. Configuration

Learning parameters are defined in `agent_learning/settings.py`.

| Setting | Description |
|---|---|
| `BEHAVIOR_MODELS` | Select Binary, Proportional, and/or Pareto-Huff |
| `K_VALUES` | Number of facilities to select |
| `TEST_CASES` | Test cases to execute |
| `SEEDS` | Master random seeds |
| `EPISODES` | Learning episodes per behavior |
| `ALPHA` | Rank learning rate |
| `BETA` | Reward baseline learning rate |
| `EXPORT_TEMPERATURE` | Softmax temperature for exported probabilities |
| `VERBOSE` | Display learning progress |

Example configuration:

```python
BEHAVIOR_MODELS = ["binary", "proportional"]
K_VALUES = [3]
TEST_CASES = ["TC1"]
SEEDS = [110]

EPISODES = 48000
ALPHA = 0.008
BETA = 0.035
EXPORT_TEMPERATURE = 1.3

VERBOSE = False
```

Multiple test cases, facility counts, and seeds can be selected.

## 4. Output Files

**Learned probabilities**

Saved under `data/learned_probabilities/`.

Example:

```text
data/learned_probabilities/k3/TC1/seed_110/
    ranked_candidates_binary.txt
    ranked_candidates_proportional.txt
```

Each file contains candidate IDs and their learned softmax selection probabilities, not raw rank values. These probabilities are used by MAS during proposal generation.

**Learning summary**

Saved at:

```text
outputs/agent_learning/summary.csv
```

Contains learning parameters, best reward, unique and duplicate solutions, scalar objective evaluations, and execution time for each behavior.

## 5. Learning Procedure and Reproducibility

- Each behavior model learns independently using its corresponding objective function.
- solutions are generated using softmax sampling.
- Final probabilities are calculated using `EXPORT_TEMPERATURE`.
- Each learning episode performs one scalar objective evaluation, including repeated solutions.
- For master seed 110, Binary, Proportional, and Pareto-Huff use independent seeds 11001, 11002, and 11003, respectively.
- The generated probabilities can be reused by MAS without repeating the learning stage.