from pathlib import Path
import numpy as np

# Dataset settings
n_candidates = 283
quality_range = (1, 5)
beta_params = (2, 5)

seeds = {
    "NU01": 260170,
    "NU02": 260171,
    "NU03": 260172,
    "NU04": 260173,
}

# Generate quality files
for case, seed in seeds.items():
    rng = np.random.default_rng(seed)

    values = rng.beta(*beta_params, size=n_candidates)
    qualities = quality_range[0] + (
        quality_range[1] - quality_range[0]
    ) * values

    output_dir = Path("data") / case
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "cityQualities.dat"
    with output_file.open("w", newline="") as f:
        f.write("\r\n".join(str(q) for q in qualities) + "\r\n")

    print(f"{case}: generated {len(qualities)} quality values (seed={seed})")