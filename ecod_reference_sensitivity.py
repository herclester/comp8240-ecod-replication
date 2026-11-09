"""From the ECOD project root, run: python /path/to/ecod_reference_sensitivity.py."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.stats import skew
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

DATASETS = ('ionosphere', 'satellite', 'satimage-2')
SEEDS = range(42, 52)


def score(reference, query):
    """Apply released ECOD aggregation to inclusive empirical tail probabilities."""
    left = np.empty(query.shape)
    right = np.empty(query.shape)
    n = len(reference)
    for j, column in enumerate(reference.T):
        ordered = np.sort(column)
        left[:, j] = np.searchsorted(ordered, query[:, j], side='right')
        right[:, j] = n - np.searchsorted(ordered, query[:, j], side='left')
    # A train-only reference can assign zero mass beyond its observed extremes.
    left = -np.log(np.maximum(left, 1) / n)
    right = -np.log(np.maximum(right, 1) / n)
    sign = np.sign(skew(reference, axis=0))
    skew_tail = -left * np.sign(sign - 1) + right * np.sign(sign + 1)
    return np.maximum(np.maximum(left, right), skew_tail).sum(axis=1)


def main():
    output = Path('results/original_benchmarks')
    recorded = pd.read_csv(output / 'individual_runs.csv').set_index(['dataset', 'seed'])
    rows = []
    for dataset in DATASETS:
        source = loadmat(Path('data/original_benchmarks') / f'{dataset}.mat')
        x, y = source['X'].astype(float), source['y'].ravel()
        for seed in SEEDS:
            train, test = train_test_split(np.arange(len(y)), test_size=.4,
                                           random_state=seed, stratify=y)
            batch = score(np.vstack((x[train], x[test])), x[test])
            train_only = score(x[train], x[test])
            auc_batch = roc_auc_score(y[test], batch)
            ap_batch = average_precision_score(y[test], batch)
            baseline = recorded.loc[(dataset, seed)]
            if not np.allclose([auc_batch, ap_batch],
                               [baseline.roc_auc, baseline.average_precision],
                               atol=1e-10, rtol=0):
                raise ValueError(f'{dataset}, seed {seed}: batch metrics differ from the saved run')
            auc_train = roc_auc_score(y[test], train_only)
            rows.append({'dataset': dataset, 'seed': seed, 'batch_auc': auc_batch,
                         'train_only_auc': auc_train, 'paired_auc_change': auc_train - auc_batch,
                         'batch_ap': ap_batch,
                         'train_only_ap': average_precision_score(y[test], train_only)})
    results = pd.DataFrame(rows)
    results.to_csv(output / 'reference_sensitivity_runs.csv', index=False)
    fields = ['batch_auc', 'train_only_auc', 'paired_auc_change', 'batch_ap', 'train_only_ap']
    print(results.groupby('dataset')[fields].agg(['mean', 'std']).round(5).to_string())


if __name__ == '__main__':
    main()
