from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class ProblemData:
    demands: np.ndarray
    distances: np.ndarray
    qualities: np.ndarray
    offset: float
    attractiveness: np.ndarray


def load_data(test_case, data_dir=None):
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
    else:
        data_dir = Path(data_dir)

    demands = np.loadtxt(data_dir / "regionDemands.dat", dtype=float)
    distances = np.loadtxt(data_dir / "regionDistancesToCity.dat", dtype=float)
    qualities = np.loadtxt(data_dir / test_case / "cityQualities.dat", dtype=float)

    if distances.ndim != 2 or distances.shape != (demands.size, qualities.size):
        raise ValueError(f"Invalid data dimensions for {test_case}")

    max_distance = float(distances.max())
    if max_distance <= 0:
        raise ValueError("Maximum distance must be positive")

    offset = 1.0 / max_distance
    distances = distances / max_distance

    min_quality = float(qualities.min())
    max_quality = float(qualities.max())
    if max_quality > min_quality:
        qualities = (qualities - min_quality) / (max_quality - min_quality)
    else:
        qualities = np.zeros_like(qualities)

    attractiveness = qualities[None, :] / (distances + offset)
    return ProblemData(demands, distances, qualities, offset, attractiveness)