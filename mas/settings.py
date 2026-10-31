BEHAVIOR_MODELS = ["binary", "proportional", "pareto_huff"]

K_VALUES = [2,3]

# TEST_CASES = ["TC1"]

TEST_CASES = [
    "TC1", "TC2", "TC3", "TC4", "TC5", "TC6",
    "U01", "U02", "U03", "U04",
    "NU01", "NU02", "NU03", "NU04",
    "SC01", "SC02", "SC03", "SC04",
]

#this will select agent leaning produces folder of probability distribution.
PROBABILITY_SEED = 110

# SEEDS = [95]

# use seed as a range from 95 to 139.
SEEDS = list(range(95, 140))

MAX_ITERS = 3000

# Duplicate limit 50 60 or None for no limit
DUPLICATE_LIMIT = None

PARETO_EPSILON = 1e-6

VERBOSE = False