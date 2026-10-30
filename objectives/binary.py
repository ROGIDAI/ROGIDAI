import numpy as np


def binary_utility(solution, data):
    best = np.max(data.attractiveness[:, list(solution)], axis=1)
    return float(np.dot(data.demands, best) / data.demands.sum())