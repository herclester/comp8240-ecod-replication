from pathlib import Path
from time import perf_counter
from importlib.metadata import version
import hashlib
import json
import platform

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.sparse import issparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score
from pyod.models.ecod import ECOD

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "original_benchmarks"
OUT = ROOT / "results" / "original_benchmarks"
OUT.mkdir(parents=True, exist_ok=True)

manifest = json.loads(
    (ROOT / "results" / "original_benchmark_manifest.json")
    .read_text(encoding="utf-8")
)

# Published ECOD ROC-AUC values: paper, Table IV.
# These are reference values, not targets used to tune our results.
PAPER_AUC = {
    "arrhythmia": 0.802,
    "breastw": 0.994,
    "cardio": 0.897,
    "ionosphere": 0.831,
    "lympho": 0.994,
    "mammography": 0.894,
    "optdigits": 0.733,
    "pima": 0.664,
    "satellite": 0.661,
    "satimage-2": 0.985,
    "shuttle": 0.998,
    "speech": 0.485,
    "wbc": 0.975,
    "wine": 0.949,
}

metadata = {
    "python": platform.python_version(),
    "packages": {
        name: version(name)
        for name in ["pyod", "numpy", "scipy", "scikit-learn", "pandas"]
    },
    "test_fraction": 0.4,
    "split_seeds": list(range(42, 52)),
    "stratified": True,
    "preprocessing": "No scaling or feature removal",
    "ecod": {"contamination": 0.1, "n_jobs": 1},
    "shuttle_sampling": "Uniform sample of 10000 rows; seed 2026",
    "scoring_note": (
        "Current PyOD ECOD scores the test batch using empirical "
        "distributions computed from combined training and test features."
    ),
    "paper_reference": "https://arxiv.org/abs/2201.00382",
    "comparison_table": "Table IV, ECOD column",
}

(OUT / "experiment_metadata.json").write_text(
    json.dumps(metadata, indent=2), encoding="utf-8"
)

runs = []

for entry in manifest:
    name = entry["dataset"]

    if entry["status"] != "loaded":
        raise RuntimeError(f"{name}: dataset was not loaded successfully.")

    path = DATA / entry["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    if digest != entry["sha256"]:
        raise RuntimeError(f"{name}: file has changed since download.")

    data = loadmat(path)
    X = data["X"]
    if issparse(X):
        X = X.toarray()

    X = np.asarray(X, dtype=float)
    y = np.asarray(data["y"]).ravel().astype(int)

    if not np.isfinite(X).all():
        raise ValueError(f"{name}: non-finite feature values.")

    if set(np.unique(y)) != {0, 1}:
        raise ValueError(f"{name}: expected binary labels 0 and 1.")

    source_rows = np.arange(len(y))

    if name == "shuttle":
        rng = np.random.default_rng(2026)
        selected = rng.choice(len(y), size=10000, replace=False)
        X, y = X[selected], y[selected]
        source_rows = source_rows[selected]

        pd.DataFrame({"source_row": source_rows}).to_csv(
            OUT / "shuttle_selected_rows.csv", index=False
        )

    print(
        f"\n{name}: {len(y)} rows, {X.shape[1]} features, "
        f"{int(y.sum())} anomalies",
        flush=True,
    )

    for seed in range(42, 52):
        train_idx, test_idx = train_test_split(
            np.arange(len(y)),
            test_size=0.4,
            random_state=seed,
            stratify=y,
        )

        model = ECOD(contamination=0.1, n_jobs=1)

        start = perf_counter()
        model.fit(X[train_idx])
        fit_seconds = perf_counter() - start

        start = perf_counter()
        scores = model.decision_function(X[test_idx])
        score_seconds = perf_counter() - start

        auc = roc_auc_score(y[test_idx], scores)
        ap = average_precision_score(y[test_idx], scores)

        runs.append({
            "dataset": name,
            "seed": seed,
            "rows": len(y),
            "features": X.shape[1],
            "anomalies": int(y.sum()),
            "train_rows": len(train_idx),
            "test_rows": len(test_idx),
            "test_anomaly_fraction": float(y[test_idx].mean()),
            "roc_auc": float(auc),
            "average_precision": float(ap),
            "fit_seconds": fit_seconds,
            "score_seconds": score_seconds,
        })

        # Save progress after every trial.
        pd.DataFrame(runs).to_csv(
            OUT / "individual_runs.csv", index=False
        )

        if seed == 42:
            pd.DataFrame({
                "source_row": source_rows[test_idx],
                "actual_label": y[test_idx],
                "anomaly_score": scores,
            }).sort_values(
                "anomaly_score", ascending=False
            ).to_csv(OUT / f"{name}_seed42_scores.csv", index=False)

        print(
            f"  seed {seed}: AUC={auc:.4f}, AP={ap:.4f}",
            flush=True,
        )

results = pd.DataFrame(runs)

summary = results.groupby("dataset", sort=False).agg(
    trials=("seed", "count"),
    rows=("rows", "first"),
    features=("features", "first"),
    anomalies=("anomalies", "first"),
    auc_mean=("roc_auc", "mean"),
    auc_std=("roc_auc", "std"),
    ap_mean=("average_precision", "mean"),
    ap_std=("average_precision", "std"),
    test_anomaly_fraction_mean=("test_anomaly_fraction", "mean"),
    fit_seconds_mean=("fit_seconds", "mean"),
    score_seconds_mean=("score_seconds", "mean"),
).reset_index()

summary["paper_auc_table_IV"] = summary["dataset"].map(PAPER_AUC)
summary["auc_difference"] = (
    summary["auc_mean"] - summary["paper_auc_table_IV"]
)
summary["dataset_note"] = summary["dataset"].map({
    "shuttle": "New random 10000-row subset; original subset unavailable",
    "wbc": "Downloaded 378 rows; paper Table I lists 278",
}).fillna("Dimensions match paper Table I")

summary.to_csv(OUT / "summary_results.csv", index=False)

print("\nCOMPLETED:", len(runs), "trials")
print(summary[
    ["dataset", "auc_mean", "auc_std", "ap_mean", "auc_difference"]
].round(4).to_string(index=False))
print("\nResults saved to:", OUT)