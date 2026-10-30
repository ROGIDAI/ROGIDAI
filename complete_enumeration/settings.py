
# can use "binary", "proportional" or "pareto_huff" as the behavior model
BEHAVIOR_MODELS = ["binary", "proportional","pareto_huff"]
# BEHAVIOR_MODELS = ["binary", "proportional"]

 # can use 2,4 etc. but the time complexity will increase exponentially with the increase of k
# K_VALUES = [3]

K_VALUES = [2, 3]


# TEST_CASES = ["TC1", "TC2", "TC3", "TC4", "TC5", "TC6"]

# TEST_CASES = ["TC1"]

TEST_CASES = [
    
     "U03", "U04",
    "NU01", "NU02", "NU03", "NU04",
    "SC01", "SC02", "SC03", "SC04",
]

#terminal show more instructions while runing the program
VERBOSE = False