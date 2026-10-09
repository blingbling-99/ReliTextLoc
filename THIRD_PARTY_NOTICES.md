# Third-party sources and retained notices

This public package contains author evaluation utilities adapted from the research project and an existing author Matplotlib style utility. It contains no vendored inference backbone, benchmark data, checkpoint, cache, or third-party model implementation. Dependencies are installed from their publishers and retain their own licenses.

## Benchmark and baseline sources

- [Text2Loc++ official code](https://github.com/anslt/Text2LocPP), inspected at revision `93287a2540fa20cd2809ba3e28255e81519b278d`. Its original MIT copyright notice (2026 Letian Shi) is preserved without modification in [licenses/Text2LocPP-MIT.txt](licenses/Text2LocPP-MIT.txt). Its evaluation coordinate convention is acknowledged in the public interface documentation.
- [Text2Loc++ publisher data/checkpoint landing page](https://huggingface.co/datasets/sltttt/Text2Loc). Follow the publisher's current access conditions. Downloading files may require login and acceptance of access terms. We do not upload or mirror these assets.
- [Text2Pos official code and KITTI360Pose benchmark](https://github.com/mako443/Text2Pos-CVPR2022).
- [KITTI-360 official source](https://www.cvlibs.net/datasets/kitti-360/). The original source specifies CC BY-NC-SA 3.0, registration, and an intended-purpose declaration. Those terms remain applicable to the source data; a label on a downstream host does not replace the original owners' terms.
- [Text2Loc official code](https://github.com/Yan-Xia/Text2Loc) and [CMMLoc official code](https://github.com/kevin301342/CMMLoc) are baseline references, not bundled implementations.

All example identifiers, text, scene labels, and coordinates in this repository are synthetic. They do not reproduce third-party dataset records or unpublished experimental outputs. Official source landing pages were checked on 2026-10-09; their providers control future availability and access terms.
