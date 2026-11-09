# Input data (not bundled)

All input data files are omitted. Downloaded and regenerated files under this directory are ignored by Git.

## Original benchmarks

Run `python download_original_benchmarks.py` from the project root. It obtains 14 ODDS-format `.mat` files from `https://raw.githubusercontent.com/winstonll/COPOD/master/data/` and places them in `data/original_benchmarks/`. It validates X/y fields and saves a manifest with SHA-256 hashes. The bundled manifest records the files used for the report; preserve it or compare hashes before trusting newly downloaded files. The mirror uses a mutable master branch, so future downloads are not guaranteed to retain identical content. Check that the downloader reports **14/14 loaded**; it records failures rather than exiting with an error.

## Banknote

Download Banknote Authentication from https://archive.ics.uci.edu/dataset/267/banknote+authentication (DOI https://doi.org/10.24432/C55P57, CC BY 4.0). Extract the download and place `data_banknote_authentication.txt` in `data/banknote/`. It is a comma-separated file without a header (four features and class). Then run `python prepare_banknote.py`. This removes exact duplicates before sampling and writes the clean and 5/10/20% versions to `data/processed/`. The original has 1,372 rows; 24 exact duplicates are removed. Class 1 is the target anomaly class in this extension, not a claim about anomaly ground truth for all uses of this classification dataset.

## Synthetic

Run `python generate_synthetic.py`. It creates six reproducible CSVs and `generation_metadata.json` under `data/synthetic/`, using generation seed 42. No download is required. The two scenarios change extreme values or correlation; files at different prevalences share observations.

## Exact omitted input-file inventory

This inventory includes raw downloads, an unused feasibility input, and reproducible processed/generated data. None was copied into the public folder.

- `data/banknote/data_banknote_authentication.txt`
- `data/banknote_authentication.zip`
- `data/breastw.mat`
- `data/original_benchmarks/arrhythmia.mat`
- `data/original_benchmarks/breastw.mat`
- `data/original_benchmarks/cardio.mat`
- `data/original_benchmarks/ionosphere.mat`
- `data/original_benchmarks/lympho.mat`
- `data/original_benchmarks/mammography.mat`
- `data/original_benchmarks/optdigits.mat`
- `data/original_benchmarks/pima.mat`
- `data/original_benchmarks/satellite.mat`
- `data/original_benchmarks/satimage-2.mat`
- `data/original_benchmarks/shuttle.mat`
- `data/original_benchmarks/speech.mat`
- `data/original_benchmarks/wbc.mat`
- `data/original_benchmarks/wine.mat`
- `data/processed/banknote_10pct.csv`
- `data/processed/banknote_20pct.csv`
- `data/processed/banknote_5pct.csv`
- `data/processed/banknote_clean.csv`
- `data/synthetic/generation_metadata.json`
- `data/synthetic/synthetic_extreme_10pct.csv`
- `data/synthetic/synthetic_extreme_20pct.csv`
- `data/synthetic/synthetic_extreme_5pct.csv`
- `data/synthetic/synthetic_relationship_10pct.csv`
- `data/synthetic/synthetic_relationship_20pct.csv`
- `data/synthetic/synthetic_relationship_5pct.csv`

`data/breastw.mat` is the earlier feasibility input; the main evaluation uses `data/original_benchmarks/breastw.mat` downloaded by the benchmark script. `data/banknote_authentication.zip` is the UCI download archive; only the extracted text file is needed. Processed banknote CSVs are rebuilt by `prepare_banknote.py`, and synthetic CSVs/metadata by `generate_synthetic.py`.
