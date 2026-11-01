from pathlib import Path
import numpy as np
from scipy.special import ndtr

# Dataset settings
n_candidates = 283
quality_range = (1, 5)

seeds = {
    "SC01": 260215,
    "SC02": 260216,
    "SC03": 260217,
    "SC04": 260218,
}

# Load candidate-to-candidate road distances (km)
base_dir = Path(__file__).resolve().parent
distance_file = base_dir / "cityDistances100_clean.dat"
distances = np.loadtxt(distance_file)

if distances.shape != (n_candidates, n_candidates):
    raise ValueError("Expected a 283 x 283 distance matrix")

if not np.isfinite(distances).all() or (distances < 0).any():
    raise ValueError("Distance matrix contains invalid values")

# Average road distances in both directions
D = (distances + distances.T) / 2
np.fill_diagonal(D, 0)

# Correlation length: 3 times median nearest-neighbor distance
D_nearest = D.copy()
np.fill_diagonal(D_nearest, np.inf)

correlation_length = 3 * np.median(D_nearest.min(axis=1))

# Spatial correlation matrix
C = np.exp(-D / correlation_length)
L = np.linalg.cholesky(C)

# Generate quality files
for case, seed in seeds.items():
    rng = np.random.default_rng(seed)

    spatial_values = L @ rng.standard_normal(n_candidates)
    uniform_values = ndtr(spatial_values)

    qualities = quality_range[0] + (
        quality_range[1] - quality_range[0]
    ) * uniform_values

    output_dir = base_dir / "data" / case
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "cityQualities.dat"

    with output_file.open("w", newline="") as f:
        f.write("\r\n".join(str(q) for q in qualities) + "\r\n")

    print(f"{case}: generated {len(qualities)} quality values (seed={seed})")

print(f"Correlation length: {correlation_length:.3f} km")