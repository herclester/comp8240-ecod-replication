from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

project_folder = Path(__file__).resolve().parent
data_folder = project_folder / "data" / "synthetic"
figure_folder = project_folder / "results" / "figures"
figure_folder.mkdir(parents=True, exist_ok=True)

fig, axes = plt.subplots(
    1, 2, figsize=(11, 4.5), sharex=True, sharey=True
)

scenarios = [
    ("extreme", "Extreme-value anomalies"),
    ("relationship", "Relationship anomalies"),
]

for ax, (scenario, title) in zip(axes, scenarios):
    df = pd.read_csv(
        data_folder / f"synthetic_{scenario}_10pct.csv"
    )

    normal = df[df["label"] == 0]
    anomalies = df[df["label"] == 1]

    ax.scatter(
        normal["feature_1"],
        normal["feature_2"],
        s=12,
        alpha=0.35,
        color="#2563eb",
        label="Normal (900)",
    )

    ax.scatter(
        anomalies["feature_1"],
        anomalies["feature_2"],
        s=25,
        alpha=0.8,
        color="#dc2626",
        marker="x",
        label="Generated anomaly (100)",
    )

    ax.set_title(title)
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")
    ax.grid(alpha=0.2)
    ax.legend()

fig.suptitle("Constructed synthetic data: 10% anomalies")
fig.tight_layout()

output_file = figure_folder / "synthetic_scenarios.png"
fig.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Plot saved to: {output_file}")