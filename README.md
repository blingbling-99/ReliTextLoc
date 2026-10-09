# ReliTextLoc

**ReliTextLoc: Reliable Text-guided 3D Localization under Attribute Ambiguity**

Shanshan Liu, Wei Wang, Tianshuo Zhang

Project repository: [blingbling-99/ReliTextLoc](https://github.com/blingbling-99/ReliTextLoc).

This is the **partial public release before manuscript acceptance**. It provides independent CPU evaluation and visualization utilities. It does not run ReliTextLoc inference or reranking, and cannot fully reproduce the paper's results. The included examples are synthetic, already specified predictions; they are neither model outputs nor benchmark measurements.

## Available now

- Scene-aware localization evaluation: R@5m, R@10m, and R@15m, with inclusive thresholds and the full ground-truth query denominator.
- Explicit accounting for invalid, unusable, missing, and wrong-scene predictions; finite-only statistics are separate diagnostics.
- Configuration templates and independent JSONL data-reading interfaces with documented input/output formats.
- A small synthetic example covering distance boundaries and failure cases, with expected results.
- Recall plotting, representative world-XY visualization, and the existing author figure style.
- Pinned CPU dependencies, installation/run commands, validation records, citation information, and third-party source notices.

## Not released yet

The C2, C2-Pre1, and OneToOne core selection modules, complete ReliTextLoc reranking implementation, baseline/model integration, full inference and reproduction configurations, internal caches, complete experimental prediction files, and model weights are not included. Third-party datasets and checkpoints are obtained from their official providers and are not redistributed here.

**Upon acceptance of the manuscript, we will release the complete ReliTextLoc modules that the authors have rights to distribute, together with full runtime configurations, reproduction commands, and checkpoint acquisition instructions in this same repository.** The [complete-release checklist](docs/AFTER_ACCEPTANCE_RELEASE_CHECKLIST.md) tracks that pending work.

## Install and run the CPU example

Use Python 3.10; the clean validation uses Python 3.10.21. Clone the repository, then run:

```bash
git clone https://github.com/blingbling-99/ReliTextLoc.git
cd ReliTextLoc
python3.10 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m unittest discover -s tests -v
python -m reli_text_loc_public.evaluate --config configs/synthetic.json
python -m reli_text_loc_public.plot --metrics outputs/synthetic/metrics.json --output outputs/synthetic/recall.png
python -m reli_text_loc_public.visualize --results outputs/synthetic/per_query.json --metrics outputs/synthetic/metrics.json --method synthetic_demo --output outputs/synthetic/xy.png
```

`requirements.txt` lists the direct dependencies; `requirements-lock.txt` pins the complete tested public runtime. No GPU, model, dataset download, workstation path, or unpublished module is required. The plotting utilities use a noninteractive Matplotlib backend. The expected synthetic result is:

| Denominator | Finite errors | Missing predictions | R@5m | R@10m | R@15m |
| --- | --- | --- | --- | --- | --- |
| 12 | 7 | 1 | 3/12 = 0.25 | 5/12 = 0.4166667 | 6/12 = 0.50 |

See [validation](docs/VALIDATION.md) and the [synthetic example](examples/synthetic/README.md) for the command record and limitations. Generated files go to ignored `outputs/`; running the example does not supply unpublished benchmark results.

## Evaluate your own already-selected predictions

```bash
python -m reli_text_loc_public.evaluate --gt your_data/ground_truth.jsonl --predictions your_data/predictions.jsonl --methods your_method --output outputs/your_evaluation
```

You can also copy [the evaluation template](configs/evaluation.template.json), configure its input paths/methods, and pass it with `--config`. Config paths are relative to the config file; explicit CLI paths are relative to your working directory. Run modules from the repository root.

The denominator is every query in the supplied GT file for each requested method. Success requires a valid finite prediction in the correct scene with Euclidean world-XY error `<=` the threshold. Wrong-scene, invalid, unusable, and missing predictions remain in that denominator as failures with error `+inf`. Unknown prediction queries and duplicate identities are rejected. Ensure the GT file contains your complete intended evaluation split; the evaluator cannot detect intentionally omitted GT queries.

See [data formats and interfaces](docs/DATA_FORMATS.md) for schemas, coordinates, and output interpretation. These interfaces consume predictions; they do not generate candidate rankings or load private pickles.

## Official third-party sources

Obtain data and baseline resources from [Text2Loc++](https://github.com/anslt/Text2LocPP), its [publisher data/checkpoint page](https://huggingface.co/datasets/sltttt/Text2Loc), [Text2Pos / KITTI360Pose](https://github.com/mako443/Text2Pos-CVPR2022), and [KITTI-360](https://www.cvlibs.net/datasets/kitti-360/). Follow the owners' access conditions and licenses. See [third-party notices](THIRD_PARTY_NOTICES.md) and [license status](LICENSE.md); the upstream MIT notice is preserved without relicensing third-party content.

## Citation

The manuscript is not assigned an invented publication venue, year, DOI, or acceptance status:

```bibtex
@unpublished{liu_relitextloc,
  title = {ReliTextLoc: Reliable Text-guided 3D Localization under Attribute Ambiguity},
  author = {Liu, Shanshan and Wang, Wei and Zhang, Tianshuo},
  note = {Manuscript; partial pre-acceptance code release}
}
```

Machine-readable authorship is in [CITATION.cff](CITATION.cff). The package's [provenance](docs/PROVENANCE.md) explains the adapted metric source and the fresh public history.
