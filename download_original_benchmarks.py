import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.sparse import issparse

ROOT = Path(__file__).resolve().parent
DATA_FOLDER = ROOT / "data" / "original_benchmarks"
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

RESULTS_FOLDER = ROOT / "results"
RESULTS_FOLDER.mkdir(exist_ok=True)

# Paper-listed ODDS .mat benchmarks.
DATASETS = [
    "arrhythmia", "breastw", "cardio", "ionosphere",
    "lympho", "mammography", "optdigits", "pima",
    "satellite", "satimage-2", "shuttle", "speech",
    "wbc", "wine",
]

# Mirror in a paper author's supplementary repository.
BASE_URL = "https://raw.githubusercontent.com/winstonll/COPOD/master/data"

manifest = []

for name in DATASETS:
    filename = f"{name}.mat"
    path = DATA_FOLDER / filename
    url = f"{BASE_URL}/{filename}"

    try:
        if not path.exists():
            print(f"Downloading {filename}...", flush=True)
            request = urllib.request.Request(
                url, headers={"User-Agent": "COMP8240-replication"}
            )
            with urllib.request.urlopen(request, timeout=90) as response:
                content = response.read()

            # Validate before retaining the download.
            temporary_path = path.with_suffix(".download")
            temporary_path.write_bytes(content)
            try:
                data = loadmat(temporary_path)
                assert "X" in data and "y" in data
                temporary_path.replace(path)
            finally:
                temporary_path.unlink(missing_ok=True)

        data = loadmat(path)
        X = data["X"]
        if issparse(X):
            X = X.toarray()
        y = np.asarray(data["y"]).ravel()

        assert X.ndim == 2
        assert len(X) == len(y)
        assert set(np.unique(y)) == {0, 1}

        entry = {
            "dataset": name,
            "file": filename,
            "download_source": url,
            "rows": int(X.shape[0]),
            "features": int(X.shape[1]),
            "anomalies": int((y == 1).sum()),
            "anomaly_percentage": float((y == 1).mean() * 100),
            "nonfinite_feature_values": int(
                (~np.isfinite(X)).sum()
            ),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "status": "loaded",
        }
        manifest.append(entry)

        print(
            f"Loaded {name}: {entry['rows']} rows, "
            f"{entry['features']} features, "
            f"{entry['anomalies']} anomalies",
            flush=True,
        )

    except Exception as error:
        manifest.append({
            "dataset": name,
            "download_source": url,
            "status": "failed",
            "error": str(error),
        })
        print(f"FAILED {name}: {error}", flush=True)

manifest_path = RESULTS_FOLDER / "original_benchmark_manifest.json"
manifest_path.write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)

loaded = sum(item["status"] == "loaded" for item in manifest)
print(f"\nLoaded {loaded}/{len(DATASETS)} datasets.")
print(f"Manifest saved to: {manifest_path}")