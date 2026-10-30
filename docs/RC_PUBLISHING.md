# Controlled experimental RC procedure / Контролируемая подготовка и публикация

**Preparation is authorized; publication is not. / Разрешена подготовка, но не публикация.** Version `0.10.0rc2`, Python package `sedrava`, future tag name `v0.10.0rc2` (not created). The RC is not a stable 0.10 release.

## Read-only preparation / Подготовка без записи в реестр

Use the existing release branch/PR. The [preparation workflow](../.github/workflows/rc-prepare.yml) runs on pull requests and can be started manually with an exact source SHA. For a manual dispatch, select a workflow ref whose head is the checked source SHA; an input SHA cannot silently mix a different workflow/source revision. It has only `contents: read` and `actions: read`, no stored checkout credentials, no package/release/token-write permissions, no secrets and no publication steps. Every action is pinned in [the reviewed pin inventory](../.github/action-pins.json). The old 0.9 attachment workflow is now an audit-only workflow; its historical publication remains documented in history.

Eight mandatory same-SHA workflows, plus every additional applicable PR/push gate, must succeed: alpha (Python matrix/Chromium/distribution), CI, Compose, navigation, records, text, 0.9 reference, distribution verification. The collector verifies repository, SHA, successful jobs, immutable input artifact IDs and actual ZIP SHA-256 digests. It rejects expired/mismatched artifacts, dangerous paths/links, duplicate members, bounded archive expansion, local/private filenames and high-confidence secret patterns. It does not execute downloaded scripts. Wheel RECORD/metadata/source and sdist/source are checked; tested Web bytes must match generation from that checkout. APK signature, ID, version, development code 10002 and permissions are checked again.

The kit contains wheel, sdist, two **debug** APKs, Web ZIP, actual test evidence, tool/dependency records, registry availability results, machine/human manifests and SHA256SUMS. After upload the workflow really downloads the kit and compares the ZIP digest and every file. The separate delivery artifact is emitted only after this round trip, with the actual kit ID, URL and Actions ZIP digest. No guessed links/checksums or moving `latest` are used. Registry checks are observations at a recorded UTC time, not a reservation. TestPyPI is not a target and was unavailable from the local managed environment.

Сборщик проверяет успешные прогоны именно того же SHA, затем использует неизменяемые проверенные байты, а не пересобирает их перед публикацией. В манифесте — реальные CI run/artifact ID, хеши файлов, результаты и инструменты. Отдельный delivery-файл связывает комплект с настоящим внешним digest после загрузки. Физическое устройство не проверялось; production-подписи нет.

## Reproduce / Воспроизведение

```sh
git checkout --detach REVIEWED_FULL_SHA
git status --short                 # must be clean
python -m venv .venv-rc-tools
. .venv-rc-tools/bin/activate
python -m pip install -r requirements-rc.txt
python -m unittest discover -s tests -v
python scripts/audit_release_security.py
python scripts/check_docs.py
python -m build
python -m twine check dist/*
python scripts/audit_dist.py
python scripts/check_reproducible_dist.py
python scripts/check_installed_dist.py
python scripts/check_upgrade_rollback.py --output dist/UPGRADE_ROLLBACK.json
```

Start the read-only Actions preparation workflow for that SHA after review. It records actual run IDs and tool versions; main CI builds from a fresh checkout. Android steps and same-key baseline update are in [navigation workflow](../.github/workflows/navigation-010.yml). Direct Python backend/test tool versions are pinned in `requirements-rc.txt` and `pyproject.toml`; actual installed Python dependencies and Android dependency tree are recorded. Transitive Android dependencies, hosted runner image and timestamp/compression metadata are not locked: archive payload/source reproducibility is checked, byte-identical APK/archive reproducibility is not promised.

## Verify an immutable delivery / Проверка комплекта

Replace `RUN_ID` and `ARTIFACT_ID` below only with the actual successful final-SHA values in PR/report/Actions. These are instruction placeholders, not links to fictional builds. Obtain the delivery JSON and independently inspect the Actions API metadata (using your normal read-only `gh` access); compare repository, source SHA, run conclusion, artifact ID and digest.

```sh
gh api repos/VasiliiBabkin/sedrava/actions/artifacts/ARTIFACT_ID
gh api repos/VasiliiBabkin/sedrava/actions/artifacts/ARTIFACT_ID/zip > candidate.zip
sha256sum candidate.zip             # must match the API digest and delivery JSON
# Inspect/unpack into a new directory, rejecting links/unsafe paths.
# From a trusted checkout of the reviewed source:
python scripts/verify_rc_bundle.py /absolute/path/to/unpacked-kit
cd /absolute/path/to/unpacked-kit
sha256sum --check SHA256SUMS
```

GitHub metadata must come independently from the actual repository/run, not solely from a supplied ZIP. SHA256SUMS checks payloads and both manifests; the external artifact digest binds SHA256SUMS itself. A manifest cannot include its own SHA-256 recursively. Hashes detect substitution relative to a trusted digest; they are **not** a production publisher signature. Keep the original immutable ZIP, delivery JSON and API metadata. Do not rebuild, edit files, merge artifacts from different commits or replace assets after checking. Do not run scripts from downloaded test evidence.

## Owner approval — separate required decision / Отдельное решение владельца

Before any publication the owner must explicitly approve **version + exact SHA + immutable kit artifact ID/digest + target**. Review GO/NO-GO, limits, failed/retried checks, debug signing and lack of physical-device coverage. Re-run availability checks immediately before publication. An absent PyPI project/version does not establish ownership or a right to claim a protected name. Publishing identity/credentials are outside this preparation; no OIDC trust or secret was installed.

Публикация возможна только после отдельного решения владельца с версией, SHA, ID/digest комплекта и выбранной площадкой. Технический GO не является разрешением. Если любой файл изменился или нужен новый исходный SHA, подготовьте новый комплект и повторите проверки. Не используйте `--clobber` и не подменяйте опубликованные байты.

The following are **documented future manual commands**, not an automated workflow and not executed during preparation. The owner should use a reviewed source checkout and the exact verified kit, with the public release notes copied from that same SHA:

```sh
# ONLY AFTER explicit owner approval; do not execute as preparation.
python /trusted/reviewed/source/scripts/verify_rc_bundle.py /absolute/path/to/kit
python /trusted/reviewed/source/scripts/check_rc_availability.py --output /tmp/rechecked-availability.json
# Owner verifies manifest.git_sha, then (only after separate tag approval):
git tag -a v0.10.0rc2 APPROVED_FULL_SHA -m 'Sedrava 0.10.0rc2 experimental RC'
git rev-parse 'v0.10.0rc2^{}'         # must equal manifest.git_sha
git push origin refs/tags/v0.10.0rc2
# Only after the approved tag is verified:
gh release create v0.10.0rc2 --repo VasiliiBabkin/sedrava --verify-tag --prerelease \
  --title 'Sedrava 0.10.0rc2 — experimental RC' \
  --notes-file /trusted/reviewed/source/docs/RELEASE_NOTES_0_10_0rc1.en.md \
  /absolute/path/to/kit/sedrava-0.10.0rc2-py3-none-any.whl \
  /absolute/path/to/kit/sedrava-0.10.0rc2.tar.gz \
  /absolute/path/to/kit/task_manager_navigation-0.10.0rc2-debug.apk \
  /absolute/path/to/kit/task_manager-0.10.0rc2-debug.apk \
  /absolute/path/to/kit/web-examples.zip /absolute/path/to/kit/SHA256SUMS \
  /absolute/path/to/kit/manifest.json /absolute/path/to/kit/manifest.md
# ONLY if PyPI publication is separately approved and identity/name access confirmed:
python -m twine check /absolute/path/to/kit/sedrava-0.10.0rc2-py3-none-any.whl /absolute/path/to/kit/sedrava-0.10.0rc2.tar.gz
python -m twine upload /absolute/path/to/kit/sedrava-0.10.0rc2-py3-none-any.whl /absolute/path/to/kit/sedrava-0.10.0rc2.tar.gz
```

No `twine upload`, Git tag, GitHub release, TestPyPI upload, PR merge or site deployment is part of any preparation workflow. TestPyPI would require a new explicit target approval and a fresh availability check; it is not included above. [Installation/rollback EN](UPGRADE_0_10_0rc1.en.md) · [RU](UPGRADE_0_10_0rc1.ru.md).

## Current RC2 / Текущий RC2

For version 0.10.0rc2 use the **new** kit and delivery receipt for PR #20 final SHA, not the historical rc1 IDs/hashes. [Notes](RELEASE_NOTES_0_10_0rc2.en.md), [upgrade/rollback](UPGRADE_0_10_0rc2.en.md), [report](RC2_010_REPORT.md). The immutable kit now also includes records-test-evidence.zip and RC2_010_REPORT.md. No publication is performed by preparation.
