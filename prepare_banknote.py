import json
from pathlib import Path

import pandas as pd

project_folder = Path(__file__).resolve().parent
source_file = (
    project_folder / "data" / "banknote"
    / "data_banknote_authentication.txt"
)

features = ["variance", "skewness", "kurtosis", "entropy"]
df = pd.read_csv(source_file, header=None, names=features + ["class"])

# Check whether identical features have conflicting labels.
label_counts = df.groupby(features)["class"].nunique()
if (label_counts > 1).any():
    raise ValueError("Identical feature values have conflicting labels.")

# Remove exact duplicates before any later train/test split.
original_rows = len(df)
clean = df.drop_duplicates().copy()
clean["source_row"] = clean.index

output_folder = project_folder / "data" / "processed"
output_folder.mkdir(parents=True, exist_ok=True)
clean.to_csv(output_folder / "banknote_clean.csv", index=False)

class_zero = clean[clean["class"] == 0]
class_one = clean[clean["class"] == 1]

summary = {
    "original_rows": original_rows,
    "clean_rows": len(clean),
    "duplicates_removed": original_rows - len(clean),
    "seed": 42,
    "target_class": 1,
    "versions": [],
}

# Use the same sample size for all three proportions.
total_rows = 500

for percentage in [5, 10, 20]:
    target_rows = total_rows * percentage // 100
    other_rows = total_rows - target_rows

    selected = pd.concat([
        class_zero.sample(n=other_rows, random_state=42),
        class_one.sample(n=target_rows, random_state=42),
    ])

    selected = selected.sample(
        frac=1, random_state=42
    ).reset_index(drop=True)

    filename = f"banknote_{percentage}pct.csv"
    selected.to_csv(output_folder / filename, index=False)

    summary["versions"].append({
        "file": filename,
        "rows": len(selected),
        "class_0_rows": other_rows,
        "class_1_rows": target_rows,
        "class_1_percentage": percentage,
    })

results_folder = project_folder / "results"
results_folder.mkdir(exist_ok=True)
(results_folder / "banknote_preparation.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8",
)

print(json.dumps(summary, indent=2))
print(f"\nPrepared datasets saved to: {output_folder}")