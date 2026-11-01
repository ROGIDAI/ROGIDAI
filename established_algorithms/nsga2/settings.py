BEHAVIOR_MODELS = ["binary", "proportional"]

K_VALUES = [3]

# TEST_CASES = ["TC1"]
TEST_CASES = ["TC1", "TC2", "TC3", "TC4", "TC5", "TC6",
               "U01", "U02", "U03", "U04",
               "NU01", "NU02", "NU03", "NU04",
               "SC01", "SC02", "SC03", "SC04"]

#SEEDS = [95]
SEEDS = list(range(95, 140))

POP_SIZE = 50
P_CROSSOVER = 0.8
P_MUTATION = 0.25
DUPLICATE_LIMIT = 50

SCALAR_BUDGET = 12000

VERBOSE = False