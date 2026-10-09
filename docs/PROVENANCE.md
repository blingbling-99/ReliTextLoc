# Provenance of this partial release

The public localization metric logic is adapted from the author's existing FullBenchmark-v1 evaluation functions `classify` and `aggregate`. The original evaluator file has SHA256 `626decce65d8d2bd715f6bb28a0eb23a91ef429ca925d834951736189d546d33`. The public adapter removes private workflow configuration and applies the same scene-aware XY error, inclusive distance thresholds, and full-denominator success rules. It adds explicit input validation and missing-prediction accounting.

The figure style comes from the author's existing `tools/figure_style.py`. JSONL interfaces, command-line adapters, and synthetic examples make these public utilities independent of the withheld research modules.

This is a newly initialized public history assembled from an explicit file allowlist. No research-project Git history, model weights, internal caches, full prediction files, or third-party datasets are included.

The recorded research environment used Python 3.10.21, NumPy 1.26.4, and Matplotlib 3.7.1. The public CPU-only dependency set and its tested environment are documented separately in [VALIDATION.md](VALIDATION.md); these versions do not constitute a complete inference environment.
