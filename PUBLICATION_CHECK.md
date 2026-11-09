# Preparation checks

- All seven report-named scripts found and copied unchanged; optional inspection and plotting helpers included.
- Explicit file allowlist used; no wholesale copy of the source project.
- No original `.git`, `.venv`, upstream package tree, caches, credentials, raw inputs, or convenor_followup experiments copied.
- Private judge case key and working per-case audit excluded. The public judge summary was adapted to describe the public artifacts.
- Original copied-file hashes and Git remote verified unchanged.
- Python syntax checked for every included `.py` file without importing or executing experiment scripts.
- Public PyPI PyOD 3.6.5 wheel source checked against the local implementation; seed-42 scores matched across all 23 datasets, including extension contributions, at absolute tolerance 1e-10.
- This wheel check reused the existing dependencies; a fully fresh environment and seeds 43–51 were not rerun. Package installation needs internet access.
- Copied text scanned for local Windows user paths, editable file URLs, common token patterns, and private-key headers; none found. This is a scoped scan, not a guarantee about arbitrary secret formats.
- Input data omitted and exact inventory/retrieval instructions provided in `data/README.md`.
- Existing report figures and relevant result summaries retained. No experiment outputs in the original were overwritten, and the report was not edited.
- A new empty local Git repository was initialized only in the export, with no commits or remote. No GitHub repository was created and nothing was uploaded.

The release manifest hashes all public files except itself. `FILE_LIST.txt` lists all public files including the manifest and itself. Fresh `.git` internals are local metadata and are not part of either public inventory.
