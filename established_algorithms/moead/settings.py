"""Reproducible 2-objective pymoo MOEA/D benchmark settings.

Original reference: Zhang and Li (2007), MOEA/D.
Implementation dependency: pymoo 0.6.1.6.
"""

BEHAVIOR_MODELS = ["binary", "proportional"]
K_VALUES = [3]
TEST_CASES = [
    "TC1", "TC2", "TC3", "TC4", "TC5", "TC6",
    "U02", "U03", "U04", "NU02", "NU03", "NU04",
    "SC01", "SC02", "SC03", "SC04",
]
SEEDS = list(range(95, 125))

# Two objectives: 50 evenly spaced weight vectors on the 2D simplex.
POP_SIZE = 50
NEIGHBORHOOD_SIZE = 20
NEIGHBORHOOD_MATING_PROBABILITY = 0.90
DECOMPOSITION = "tchebycheff"  # pymoo Tchebicheff; NOT normalized

# Retained from the older pymoo-based fixed-k MOEA/D implementation.
P_CROSSOVER = 0.90
P_MUTATION = 1.00
REPLACEMENT_PROBABILITY = None  # per selected facility: 1/k
DUPLICATE_LIMIT = 1000  # retry same parents; raise if exhausted

# Change ONLY this value between experiments: 12000, 10238, 31504.
SCALAR_BUDGET = 10238

# New output folder to avoid overwriting existing custom MOEA/D V1/V2.
OUTPUT_NAME = "moead_pymoo"
VERBOSE = False

# Objective-count checkpoints for reviewer-requested IGD/HV convergence plots.
# Recording these snapshots does not change the MOEA/D search.
CHECKPOINT_SCALAR_EVALUATIONS = (
    1000, 2000, 4000, 6000, 8000, 10000, 10238, 12000,
    16000, 20000, 24000, 28000, 31504,
)
