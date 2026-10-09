# Validation of the partial public utilities

Validated on 2026-10-09, Linux x86_64, Python 3.10.21. This is a small CPU-only engineering check with synthetic inputs, not a rerun of the research experiments or a complete ReliTextLoc reproduction.

## Clean environment and installation

A new venv was created with `system-site-packages = false`. User packages were disabled (`PYTHONNOUSERSITE=1`) and `PYTHONPATH` was cleared. Only files selected by [the public allowlist](../PUBLIC_FILE_ALLOWLIST.txt) were copied into the validation working directory. No model, third-party dataset, research cache, private prediction file, or withheld module was available there.

The runtime used NumPy 1.26.4 and Matplotlib 3.7.1, matching the inspected versions. [requirements-lock.txt](../requirements-lock.txt) contains all 11 installed public-runtime distributions; [requirements.txt](../requirements.txt) lists the direct dependencies.

Initial online package downloads were truncated and failed integrity checks; those incomplete files were not installed. Registered package wheels were downloaded again, and all 11 complete wheels matched the official PyPI SHA256 values and passed ZIP CRC checks. They were installed into the empty venv from a local wheelhouse. Installed libraries were not copied from the research environment.

The installation and run commands below use `.venv` for the validation interpreter and `WHEELHOUSE` for the local directory of those verified wheels, in place of private staging-directory names:

```bash
python3.10 -m venv .venv
. .venv/bin/activate
python -m pip install --no-index --find-links "$WHEELHOUSE" -r requirements-lock.txt
python -m pip check
python -m unittest discover -s tests -v
python -m reli_text_loc_public.evaluate --config configs/synthetic.json
python -m reli_text_loc_public.plot --metrics outputs/synthetic/metrics.json --output outputs/synthetic/recall.png
python -m reli_text_loc_public.visualize --results outputs/synthetic/per_query.json --metrics outputs/synthetic/metrics.json --method synthetic_demo --output outputs/synthetic/xy.png
```

Installation succeeded; `pip check` returned `No broken requirements found`. All listed run commands exited with status 0. All **21 tests passed**. The normal online installation command is documented in [README](../README.md); the offline command above records the workaround actually used for the truncated downloads.

## Synthetic results

The example has 12 invented GT queries and 11 manually specified predictions. There is no model inference and no precomputed scientific result in this example.

| Quantity | Verified result |
| --- | --- |
| Full GT denominator | 12 |
| Finite-error diagnostic denominator | 7 |
| Missing predictions | 1 |
| Successes at 5 / 10 / 15m | 3 / 5 / 6 |
| R@5m | 0.25 (25%) |
| R@10m | 0.4166666666666667 (41.6667%) |
| R@15m | 0.50 (50%) |

Evaluation produced `metrics.json`, `metrics.csv`, and `per_query.json`. Both `recall.png` and `xy.png` were generated and visually inspected; each is explicitly labeled **Synthetic illustration**. The XY legend placement was checked again after avoiding overlap with query labels. Generated files are kept outside the published file allowlist.

A separate config-path check ran the evaluator from another working directory with an absolute config argument; the same expected metrics were obtained. Config-relative input paths do not depend on the research workstation.

## Metric fidelity

A separate source-parity audit compared the public metric functions with the author's existing evaluator on **5,513 invented cases**, including 4,500 non-axis vectors near the 5/10/15m boundaries. Classification fields, exact error values, and shared aggregation fields agreed in every case. This check used the original NumPy float64 norm and did not read original GT or prediction files.

Tests cover inclusive boundaries, invalid/wrong-scene/unusable/missing predictions, full denominator retention, wholly absent methods, strict query/method identity checks, and JSONL validation. The import-chain and file checks found no withheld selector/model imports, workstation paths, credentials, or private assets in the allowlisted public files. The author figure style and original upstream MIT notice are byte-identical to their sources.

## Limits

These checks verify the published utility interface and metric contract. The public package does not run C2, C2-Pre1, OneToOne, baseline inference, or the complete proposed reranking module. It cannot fully reproduce ReliTextLoc. The user must supply the complete intended GT manifest; the evaluator cannot detect GT queries omitted before its input is constructed. Finite-only recalls are diagnostics and must not replace the full-denominator headline metrics.
