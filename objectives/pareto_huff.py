import numpy as np


def pareto_huff_utility(solution, data):
    locations = list(solution)
    if not locations:
        raise ValueError("Solution cannot be empty")

    distances = data.distances[:, locations]
    qualities = data.qualities[locations]
    a = data.attractiveness[:, locations].copy()

    for j in range(len(locations)):
        dominated = (
            (distances <= distances[:, [j]])
            & (qualities >= qualities[j])
            & ((distances < distances[:, [j]]) | (qualities > qualities[j]))
        ).any(axis=1)
        a[dominated, j] = 0.0

    total = a.sum(axis=1)
    utility = np.divide((a * a).sum(axis=1), total,
                        out=np.zeros_like(total), where=total > 0)
    return float(np.dot(data.demands, utility) / data.demands.sum())