from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.sparse import issparse
from scipy.stats import skew
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score
from pyod.models.ecod import ECOD

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "original_benchmarks"

manifest = json.loads(
    (ROOT / "results" / "original_benchmark_manifest.json")
    .read_text(encoding="utf-8")
)

rows = []

for entry in manifest:
    name = entry["dataset"]
    data = loadmat(
        ROOT / "data" / "original_benchmarks" / entry["file"]
    )

    X = data["X"]
    if issparse(X):
        X = X.toarray()
    X = np.asarray(X, dtype=float)
    y = np.asarray(data["y"]).ravel().astype(int)

    # Reuse exactly the Shuttle subset from the previous experiment.
    if name == "shuttle":
        selected = pd.read_csv(
            OUT / "shuttle_selected_rows.csv"
        )["source_row"].to_numpy(dtype=int)
        X, y = X[selected], y[selected]

    for seed in range(42, 52):
        train_idx, test_idx = train_test_split(
            np.arange(len(y)),
            test_size=0.4,
            random_state=seed,
            stratify=y,
        )

        model = ECOD(contamination=0.1, n_jobs=1)
        model.fit(X[train_idx])
        code_scores = model.decision_function(X[test_idx])

        # Diagnostic: implement Equation 6's aggregation.
        # Keep the same ECDF arrays and batch-scoring setup.
        combined = np.vstack([X[train_idx], X[test_idx]])
        feature_skew = np.nan_to_num(skew(combined, axis=0))

        auto_contributions = np.where(
            feature_skew < 0,
            model.U_l,
            model.U_r,
        )

        equation6_all = np.maximum.reduce([
            model.U_l.sum(axis=1),
            model.U_r.sum(axis=1),
            auto_contributions.sum(axis=1),
        ])
        equation6_scores = equation6_all[-len(test_idx):]

        for method, scores in [
            ("released_code", code_scores),
            ("equation6_diagnostic", equation6_scores),
        ]:
            rows.append({
                "dataset": name,
                "seed": seed,
                "method": method,
                "roc_auc": roc_auc_score(y[test_idx], scores),
                "average_precision": average_precision_score(
                    y[test_idx], scores
                ),
            })

    print("Checked:", name, flush=True)

runs = pd.DataFrame(rows)
runs.to_csv(OUT / "aggregation_diagnostic_runs.csv", index=False)

summary = runs.groupby(["dataset", "method"], sort=False).agg(
    trials=("seed", "count"),
    auc_mean=("roc_auc", "mean"),
    auc_std=("roc_auc", "std"),
    ap_mean=("average_precision", "mean"),
    ap_std=("average_precision", "std"),
).reset_index()

summary.to_csv(
    OUT / "aggregation_diagnostic_summary.csv", index=False
)

print("\n", summary.round(4).to_string(index=False))
print("\nDiagnostic comparison completed.")