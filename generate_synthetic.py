import json
from pathlib import Path

import numpy as np
import pandas as pd

project_folder = Path(__file__).resolve().parent
output_folder = project_folder / "data" / "synthetic"
output_folder.mkdir(parents=True, exist_ok=True)

results_folder = project_folder / "results"
results_folder.mkdir(exist_ok=True)

SEED = 42
TOTAL_ROWS = 1000
FEATURES = ["feature_1", "feature_2", "feature_3", "feature_4"]
CORRELATION = 0.95

rng = np.random.default_rng(SEED)


def make_observations(number, correlation):
    """Generate four features; the first two have a set correlation."""
    values = rng.normal(size=(number, 4))
    values[:, 1] = (
        correlation * values[:, 0]
        + np.sqrt(1 - correlation**2) * values[:, 1]
    )
    return values


# Normal observations: features 1 and 2 tend to move together.
normal_pool = make_observations(TOTAL_ROWS, CORRELATION)

# Extreme anomalies: shift the first two features by +4 or -4.
extreme_pool = make_observations(200, CORRELATION)
directions = rng.choice([-1, 1], size=(200, 1))
extreme_pool[:, :2] += 4.0 * directions

# Relationship anomalies: features 1 and 2 tend to move oppositely.
# Each individual feature still has the same theoretical distribution.
relationship_pool = make_observations(200, -CORRELATION)

scenarios = {
    "extreme": extreme_pool,
    "relationship": relationship_pool,
}

metadata = {
    "source": "Constructed by the project generation script",
    "seed": SEED,
    "rows_per_file": TOTAL_ROWS,
    "features": FEATURES,
    "labels": {"0": "normal", "1": "generated anomaly"},
    "normal_distribution": (
        "Four standard-normal features; correlation between "
        "features 1 and 2 is +0.95; features 3 and 4 are independent."
    ),
    "extreme_anomalies": (
        "Same base distribution, with a shared +4 or -4 shift "
        "applied to features 1 and 2."
    ),
    "relationship_anomalies": (
        "Standard-normal marginal distributions, with correlation "
        "between features 1 and 2 changed to -0.95."
    ),
    "sampling": (
        "Fixed pools reused across proportions. Files overlap "
        "and represent related experimental conditions."
    ),
}

summaries = []

for scenario, anomaly_pool in scenarios.items():
    for percentage in [5, 10, 20]:
        anomaly_count = TOTAL_ROWS * percentage // 100
        normal_count = TOTAL_ROWS - anomaly_count

        X = np.vstack([
            normal_pool[:normal_count],
            anomaly_pool[:anomaly_count],
        ])
        y = np.concatenate([
            np.zeros(normal_count, dtype=int),
            np.ones(anomaly_count, dtype=int),
        ])

        df = pd.DataFrame(X, columns=FEATURES)
        df["label"] = y

        # Shuffle to avoid placing all anomalies at the end.
        df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

        assert np.isfinite(df[FEATURES].to_numpy()).all()
        assert len(df) == TOTAL_ROWS
        assert int(df["label"].sum()) == anomaly_count

        filename = f"synthetic_{scenario}_{percentage}pct.csv"
        df.to_csv(output_folder / filename, index=False)

        summaries.append({
            "file": filename,
            "scenario": scenario,
            "rows": len(df),
            "features": len(FEATURES),
            "normal_rows": normal_count,
            "anomaly_rows": anomaly_count,
            "anomaly_percentage": percentage,
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        })

(output_folder / "generation_metadata.json").write_text(
    json.dumps(metadata, indent=2), encoding="utf-8"
)

summary_table = pd.DataFrame(summaries)
summary_table.to_csv(
    results_folder / "synthetic_data_summary.csv", index=False
)

print(summary_table.to_string(index=False))
print(f"\nDatasets and generation metadata saved to: {output_folder}")