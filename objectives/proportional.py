import numpy as np


def proportional_utility(solution, data):
    a = data.attractiveness[:, list(solution)]
    total = a.sum(axis=1)
    utility = np.divide((a * a).sum(axis=1), total,
                        out=np.zeros_like(total), where=total > 0)
    return float(np.dot(data.demands, utility) / data.demands.sum())