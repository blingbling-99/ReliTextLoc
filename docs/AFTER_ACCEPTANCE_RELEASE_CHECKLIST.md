# Complete release after manuscript acceptance

Status: pending acceptance. This list does not mean the complete implementation is already available. Expand this same repository only after acceptance is confirmed.

- [ ] Record acceptance and fix the manuscript/implementation version to release.
- [ ] Review ownership and third-party redistribution rights for each selected file. Preserve every existing license and copyright notice; choose an author-code license explicitly.
- [ ] Release author-owned ReliTextLoc modules, including C2, C2-Pre1, and OneToOne selection variants, parser/support scoring, fallback behavior, tie breaking, and their integration with the baseline.
- [ ] Audit the import chain. Replace workstation paths with user configuration; remove private file, cache, and credential dependencies.
- [ ] Publish full runtime/environment configuration with exact versions and official baseline revisions, language settings, candidate counts, coordinate conversions, scene handling, seeds, and preprocessing.
- [ ] Provide dataset acquisition and preparation instructions using official sources. Do not redistribute third-party data without permission.
- [ ] Supply checkpoint acquisition, version/hash verification, and loading instructions. Publish author-owned checkpoints only where rights permit; link third-party checkpoints to their official sources.
- [ ] Provide complete inference, reranking, evaluation, visualization, and reproduction commands with declared hardware/runtime requirements.
- [ ] Review permission to publish derived predictions/results separately from source code. Include only approved representative results; do not export internal caches by default.
- [ ] Run scientific correctness tests, clean-environment integration checks, and the promised reproduction commands. Record tested dataset/split scope, expected outputs, metrics, and limitations honestly.
- [ ] Update README, citation, provenance, and dependency documentation. Replace the pre-acceptance limitations only after the corresponding modules are actually available.
- [ ] Build a new explicit file whitelist and scan all staged files and outgoing history for credentials, private assets, and unapproved third-party content.
- [ ] Publish a versioned release in this repository; check anonymous access, commands, and links.
- [ ] Update only the relevant manuscript code-availability statement to describe the verified complete release.
