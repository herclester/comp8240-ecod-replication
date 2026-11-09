import json
from pathlib import Path

import numpy as np
import pandas as pd

project_folder = Path(__file__).resolve().parent
data_file = (
    project_folder / "data" / "banknote"
    / "data_banknote_authentication.txt"
)

# The original file has no header.
columns = ["variance", "skewness", "kurtosis", "entropy", "class"]
df = pd.read_csv(data_file, header=None, names=columns)

# Check the structure before using the data.
assert df.shape[1] == 5, "Expected four features and one label."
assert set(df["class"].unique()) == {0, 1}, "Unexpected class labels."
assert np.isfinite(df.to_numpy()).all(), "Missing or non-finite values found."

summary = {
    "dataset": "UCI Banknote Authentication",
    "source": "https://archive.ics.uci.edu/dataset/267/banknote+authentication",
    "rows": int(len(df)),
    "features": columns[:-1],
    "missing_values": int(df.isna().sum().sum()),
    "duplicate_rows": int(df.duplicated().sum()),
    "class_counts": {
        str(label): int(count)
        for label, count in df["class"].value_counts().sort_index().items()
    },
}

output_folder = project_folder / "results"
output_folder.mkdir(exist_ok=True)

summary_file = output_folder / "banknote_data_summary.json"
summary_file.write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8",
)

df.describe().to_csv(output_folder / "banknote_descriptive_statistics.csv")

print(json.dumps(summary, indent=2))
print("\nFirst five observations:")
print(df.head().to_string(index=False))
print(f"\nSummary saved to: {summary_file}")