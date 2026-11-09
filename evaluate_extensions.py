from pathlib import Path
from time import perf_counter
from importlib.metadata import version
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score
from pyod.models.ecod import ECOD

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "extensions"
OUT.mkdir(parents=True, exist_ok=True)

datasets = []

for rate in [5, 10, 20]:
    datasets.append((
        ROOT / "data" / "processed" / f"banknote_{rate}pct.csv",
        "banknote",
        rate,
    ))

for scenario in ["extreme", "relationship"]:
    for rate in [5, 10, 20]:
        datasets.append((
            ROOT / "data" / "synthetic"
            / f"synthetic_{scenario}_{rate}pct.csv",
            scenario,
            rate,
        ))

# Check all inputs before starting.
missing = [str(path) for path, _, _ in datasets if not path.exists()]
if missing:
    raise FileNotFoundError(
        "These input files were not found:\n" + "\n".join(missing)
    )

metadata = {
    "pyod_version": version("pyod"),
    "test_fraction": 0.4,
    "split_seeds": list(range(42, 52)),
    "stratified": True,
    "ecod": {"contamination": 0.1, "n_jobs": 1},
    "preprocessing": "No scaling; labels and identifiers excluded",
    "scoring": (
        "Released PyOD ECOD implementation; test scores use "
        "combined training and test feature distributions."
    ),
    "limitations": [
        "Rate versions share observations and are not independent datasets.",
        "Trials vary the split, not the synthetic generation seed.",
        "Banknote class 1 is treated as the target anomaly class.",
    ],
}
(OUT / "experiment_metadata.json").write_text(
    json.dumps(metadata, indent=2), encoding="utf-8"
)

runs = []

for path, scenario, rate in datasets:
    name = path.stem
    df = pd.read_csv(path)

    # Banknote uses 'class'; synthetic files use 'label'.
    label_column = next(
        (col for col in ["label", "class", "y"] if col in df.columns),
        None,
    )
    if label_column is None:
        raise ValueError(f"{name}: no label column found.")

    feature_columns = [
        col for col in df.columns
        if col not in {
            "label", "class", "y", "source_row",
            "source_id", "row_id", "id"
        }
        and not col.startswith("Unnamed:")
    ]

    if len(feature_columns) != 4:
        raise ValueError(
            f"{name}: expected 4 features, found {feature_columns}"
        )

    X = df[feature_columns].to_numpy(dtype=float)
    y_raw = df[label_column].to_numpy(dtype=float)

    if not np.isfinite(X).all():
        raise ValueError(f"{name}: missing or infinite feature values.")
    if not np.isin(y_raw, [0, 1]).all():
        raise ValueError(f"{name}: labels must be 0 or 1.")

    y = y_raw.astype(int)
    if len(np.unique(y)) != 2:
        raise ValueError(f"{name}: both label classes are required.")

    if len(y) * rate != int(y.sum()) * 100:
        raise ValueError(f"{name}: anomaly percentage does not match.")

    print(
        f"\n{name}: {len(y)} rows, {X.shape[1]} features, "
        f"{int(y.sum())} target anomalies",
        flush=True,
    )

    for seed in range(42, 52):
        train_idx, test_idx = train_test_split(
            np.arange(len(y)),
            test_size=0.4,
            random_state=seed,
            stratify=y,
        )
        y_test = y[test_idx]

        model = ECOD(contamination=0.1, n_jobs=1)

        start = perf_counter()
        model.fit(X[train_idx])
        fit_seconds = perf_counter() - start

        start = perf_counter()
        scores = model.decision_function(X[test_idx])
        score_seconds = perf_counter() - start

        order = np.argsort(-scores, kind="stable")
        anomaly_count = int(y_test.sum())

        runs.append({
            "dataset": name,
            "scenario": scenario,
            "anomaly_percentage": rate,
            "seed": seed,
            "rows": len(y),
            "features": X.shape[1],
            "train_rows": len(train_idx),
            "test_rows": len(test_idx),
            "test_anomalies": anomaly_count,
            "roc_auc": roc_auc_score(y_test, scores),
            "average_precision": average_precision_score(y_test, scores),
            "test_anomaly_fraction": float(y_test.mean()),
            "precision_at_n": float(
                y_test[order[:anomaly_count]].mean()
            ),
            "precision_at_5": float(y_test[order[:5]].mean()),
            "fit_seconds": fit_seconds,
            "score_seconds": score_seconds,
        })

        # Preserve progress after every trial.
        pd.DataFrame(runs).to_csv(
            OUT / "individual_runs.csv", index=False
        )

        if seed == 42:
            # PyOD stores contributions for train + test observations.
            contributions = np.asarray(model.O)[-len(test_idx):]

            if not np.allclose(contributions.sum(axis=1), scores):
                raise RuntimeError("Feature contributions do not sum to scores.")

            details = pd.DataFrame({
                "input_row": test_idx,
                "actual_label": y_test,
                "anomaly_score": scores,
            })

            if "source_row" in df.columns:
                details["source_row"] = (
                    df.iloc[test_idx]["source_row"].to_numpy()
                )

            for j, feature in enumerate(feature_columns):
                details[f"value_{feature}"] = X[test_idx, j]
                details[f"contribution_{feature}"] = contributions[:, j]

            details["largest_contributing_feature"] = [
                feature_columns[j]
                for j in contributions.argmax(axis=1)
            ]

            details = details.iloc[order].copy()
            details.insert(0, "rank", np.arange(1, len(details) + 1))
            details.to_csv(
                OUT / f"{name}_seed42_scores.csv", index=False
            )
            details.head(5).to_csv(
                OUT / f"{name}_worked_example.csv", index=False
            )

        print(
            f"  seed {seed}: "
            f"AUC={runs[-1]['roc_auc']:.4f}, "
            f"AP={runs[-1]['average_precision']:.4f}",
            flush=True,
        )

results = pd.DataFrame(runs)

summary = results.groupby(
    ["dataset", "scenario", "anomaly_percentage"], sort=False
).agg(
    trials=("seed", "count"),
    rows=("rows", "first"),
    features=("features", "first"),
    auc_mean=("roc_auc", "mean"),
    auc_std=("roc_auc", "std"),
    ap_mean=("average_precision", "mean"),
    ap_std=("average_precision", "std"),
    test_anomaly_fraction_mean=("test_anomaly_fraction", "mean"),
    precision_at_n_mean=("precision_at_n", "mean"),
    precision_at_5_mean=("precision_at_5", "mean"),
    fit_seconds_mean=("fit_seconds", "mean"),
    score_seconds_mean=("score_seconds", "mean"),
).reset_index()

summary.to_csv(OUT / "summary_results.csv", index=False)

print("\nCOMPLETED:", len(runs), "trials")
print(summary[
    ["dataset", "auc_mean", "auc_std", "ap_mean"]
].round(4).to_string(index=False))
print("\nResults saved to:", OUT)