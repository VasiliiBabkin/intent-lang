# Sedrava 0.10 — experimental release candidate preparation

**Status:** preparation only; no RC published, tagged or uploaded.

Baseline: merged PR #16, main commit `2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1`.

## Release gates

1. Choose an explicit PEP 440 compatible prerelease version (for example `0.10.0rc1`); ensure package metadata, CLI version, docs, examples and artifact names agree. Do not overwrite an existing published version.
2. Confirm that clean wheel/sdist installations support check, test, run, build web and build android, including records and navigation examples.
3. Audit GitHub Actions permissions, dependency versions, secrets exposure, provenance, SHA256 checksums and downloadable artifact integrity. Distinguish source reproducibility from byte-identical APK reproducibility.
4. Produce release notes in Russian and English with supported features, migration caveats, known limitations, and explicit experimental status.
5. Document installation and rollback to the last published 0.9 baseline. Android debug builds must not be presented as production signed artifacts.
6. Verify physical-device behavior if available; otherwise mark unavailable and avoid claims of hardware validation.
7. Define exact publication commands and a manual approval gate; do not execute tag, GitHub release, PyPI upload or site deployment.
8. Preserve 0.9/0.10 regression coverage; require green CI on final RC candidate commit.
9. Report GO/NO-GO for **publication** separately from GO for technical preparation.

## Deliverables

- Bilingual release notes and upgrade/rollback guidance.
- RC manifest: version, source SHA, build commands, checksums, CI run URLs, artifact links, known limits.
- Clean-install test results and final-head CI evidence.
- Clear human approval checklist for publishing.

No merge, tag, release, package publication or deployment is authorized by this contract.
