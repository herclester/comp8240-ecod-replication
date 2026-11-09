# Third-party attribution

This is a COMP8240 replication project, not the upstream PyOD library.

PyOD: https://github.com/yzhao062/pyod (BSD 2-Clause, copyright Yue Zhao).
`results/original_benchmarks/ecod_source_used.py` is a historical ECOD class snapshot retained as implementation evidence, not an executable dependency. The upstream license is preserved in `licenses/PyOD-LICENSE.txt`. The public wheel is installed using `pyod==3.6.5`.

ECOD paper: Li et al., *ECOD: Unsupervised Outlier Detection Using Empirical Cumulative Distribution Functions*, https://arxiv.org/abs/2201.00382. Published comparison values in the scripts refer to Table IV.

ODDS benchmark input files are downloaded separately from the COPOD supplementary mirror: https://github.com/winstonll/COPOD/tree/master/data. Per-file source URLs and SHA-256 hashes are retained in `results/original_benchmark_manifest.json`. Dataset rights remain with their respective owners; inclusion of derived results does not relicense the input data.

Banknote Authentication: Lohweg, V. (2012), UCI Machine Learning Repository, https://doi.org/10.24432/C55P57. UCI lists CC BY 4.0: https://archive.ics.uci.edu/dataset/267/banknote+authentication. The extension score tables contain derived banknote feature values; credit applies to those values as well. The raw dataset is not bundled.

No new blanket license is imposed on student-authored material by this packaging step. The upstream PyOD license applies to the retained third-party snapshot. Public visibility alone is not a software license.
