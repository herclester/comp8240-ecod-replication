from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / "results" / "original_benchmarks"
EXTENSIONS = ROOT / "results" / "extensions"
FIGURES = ROOT / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Figure 1: Original benchmark comparison.
original = pd.read_csv(ORIGINAL / "summary_results.csv")
positions = np.arange(len(original))

fig, ax = plt.subplots(figsize=(10, 7))

ax.errorbar(
    original["auc_mean"], positions,
    xerr=original["auc_std"],
    fmt="o", color="#1565C0", capsize=3,
    label="Our released-code result: mean ± SD",
)
ax.scatter(
    original["paper_auc_table_IV"], positions,
    marker="D", color="#E65100",
    label="Published ECOD result: Table IV",
)

ax.set_yticks(positions)
ax.set_yticklabels(original["dataset"])
ax.invert_yaxis()
ax.set_xlim(0.35, 1.03)
ax.set_xlabel("ROC-AUC")
ax.set_title("Partial replication: 14 original benchmarks")
ax.grid(axis="x", alpha=0.2)
ax.legend(loc="lower left", fontsize=9)

fig.text(
    0.02, 0.015,
    "10 stratified 60/40 splits. Error bars show split variability, "
    "not confidence intervals.\n"
    "Shuttle uses a new 10,000-row sample; WBC row count differs "
    "from the paper's Table I.",
    fontsize=9,
)
fig.tight_layout(rect=[0, 0.07, 1, 1])
fig.savefig(FIGURES / "original_benchmark_comparison.png", dpi=200)
plt.close(fig)

# Figure 2: Extension results at different anomaly percentages.
extensions = pd.read_csv(EXTENSIONS / "summary_results.csv")

styles = {
    "banknote": ("Curated Banknote", "#7B1FA2"),
    "extreme": ("Synthetic extreme", "#1565C0"),
    "relationship": ("Synthetic relationship", "#D84315"),
}

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for scenario, (label, color) in styles.items():
    subset = extensions[
        extensions["scenario"] == scenario
    ].sort_values("anomaly_percentage")

    for ax, mean_column, sd_column in [
        (axes[0], "auc_mean", "auc_std"),
        (axes[1], "ap_mean", "ap_std"),
    ]:
        ax.errorbar(
            subset["anomaly_percentage"],
            subset[mean_column],
            yerr=subset[sd_column],
            marker="o", capsize=4,
            color=color, label=label,
        )

axes[0].axhline(
    0.5, color="grey", linestyle="--",
    label="Chance-ranking reference",
)
axes[1].plot(
    [5, 10, 20], [0.05, 0.10, 0.20],
    color="grey", linestyle="--",
    label="Anomaly-prevalence reference",
)

for ax in axes:
    ax.set_xticks([5, 10, 20])
    ax.set_xlabel("Anomalies in dataset (%)")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)

axes[0].set_ylabel("ROC-AUC")
axes[1].set_ylabel("Average precision")
fig.suptitle("New-data evaluation: extreme values versus relationships")
fig.text(
    0.02, 0.015,
    "Mean ± SD across 10 splits. Rate versions share observations; "
    "synthetic generation seed is fixed.",
    fontsize=9,
)
fig.tight_layout(rect=[0, 0.06, 1, 0.94])
fig.savefig(FIGURES / "extension_results.png", dpi=200)
plt.close(fig)

# Figure 3: Explain two actual ranked observations.
extreme = pd.read_csv(
    EXTENSIONS / "synthetic_extreme_10pct_worked_example.csv"
)
relationship = pd.read_csv(
    EXTENSIONS / "synthetic_relationship_10pct_worked_example.csv"
)

examples = [
    (
        extreme.loc[extreme["input_row"] == 749].iloc[0],
        "Extreme scenario: known anomaly",
        "#1565C0",
    ),
    (
        relationship.loc[relationship["input_row"] == 89].iloc[0],
        "Relationship scenario: known normal",
        "#D84315",
    ),
]

features = [f"feature_{i}" for i in range(1, 5)]
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

for ax, (row, title, color) in zip(axes, examples):
    contributions = [
        row[f"contribution_{feature}"] for feature in features
    ]
    bars = ax.bar(["F1", "F2", "F3", "F4"], contributions, color=color)
    ax.bar_label(bars, fmt="%.2f", padding=3)

    ax.set_ylim(0, 8)
    ax.set_xlabel("Feature")
    ax.set_title(
        f"{title}\n"
        f"Test rank {int(row['rank'])}; score "
        f"{row['anomaly_score']:.3f}",
        fontsize=11,
    )

    values = ", ".join(
        f"F{i}={row[f'value_feature_{i}']:.2f}"
        for i in range(1, 5)
    )
    ax.text(
        0.5, -0.18, values,
        transform=ax.transAxes,
        ha="center", fontsize=9,
    )

axes[0].set_ylabel("Contribution to ECOD anomaly score")
fig.suptitle("Worked examples: what drives the released-code score?")
fig.tight_layout(rect=[0, 0.05, 1, 0.93])
fig.savefig(FIGURES / "worked_examples.png", dpi=200)
plt.close(fig)

print("Saved figures to:", FIGURES)
print("1. original_benchmark_comparison.png")
print("2. extension_results.png")
print("3. worked_examples.png")