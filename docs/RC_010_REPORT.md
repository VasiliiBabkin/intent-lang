# Sedrava 0.10.0rc1 — RC preparation report / Отчёт подготовки RC

Status: implementation and local checks in progress; final CI kit pending. **NO-GO for publication until final-SHA gates and actual manifest finish. Publication permission has not been given.** No tag, release, upload, merge or deployment is performed.

Base main: `2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1`; existing branch `release/0.10.0-rc-preparation`, PR #17. Final exact bundle SHA, build IDs, actual URLs and SHA-256 values are stamped by CI into `manifest.json`, `manifest.md` and `RC_010_REPORT.md` in the immutable kit. The repository report records the implementation evidence; the final PR identifies the subsequently checked documentation commit. No self-referential Git hash or invented checksum is used.

Implemented: single-source PEP 440 version, dynamic package metadata and CLI/Android agreement; code 10001 without ID changes; clean wheel/sdist tests and published-0.9-wheel rollback checks; read-only pinned Actions/no publishing steps; bounded archive/source/digest inspection; actual baseline-to-RC Android update scenario; same-SHA candidate collector, file hashes and post-upload delivery identity. RU/EN release notes and upgrade/rollback instructions are included.

Locally: 151 Python tests passed so far. Current final results, counts, hashes and links will be filled after actual CI. Physical Android device unavailable; no physical-device success claimed. TestPyPI unavailable locally and not a publication target. PyPI project/version returned HTTP 404 on 2026-10-30; CI rechecks current version and GitHub tag/release before kit preparation.

[Release notes EN](RELEASE_NOTES_0_10_0rc1.en.md) · [RU](RELEASE_NOTES_0_10_0rc1.ru.md) · [Upgrade EN](UPGRADE_0_10_0rc1.en.md) · [RU](UPGRADE_0_10_0rc1.ru.md) · [Publication controls](RC_PUBLISHING.md).
