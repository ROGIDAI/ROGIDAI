from pathlib import Path
import numpy as np

# Dataset settings
n_candidates = 283
quality_range = (1, 5)

seeds = {
    "U01": 260085,
    "U02": 260086,
    "U03": 260087,
    "U04": 260088,
}

# Generate quality files
for case, seed in seeds.items():
    rng = np.random.default_rng(seed)
    qualities = rng.uniform(*quality_range, size=n_candidates)

    output_dir = Path("data") / case
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "cityQualities.dat"
    with output_file.open("w", newline="") as f:
        f.write("\r\n".join(str(q) for q in qualities) + "\r\n")

    print(f"{case}: generated {len(qualities)} quality values (seed={seed})")