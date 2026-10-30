# Sedrava 0.10.0rc1 — RC preparation report / Отчёт подготовки RC

Date: 2026-10-30. **Technical GO for controlled experimental RC publication after a separate owner decision. Publication authorization: NOT GIVEN.** Sedrava 0.10 is not announced as released; no RC tag, GitHub Release, PyPI/TestPyPI upload, merge or deployment was performed.

## Source identity / Идентичность исходников

Repository: `VasiliiBabkin/sedrava`; existing [PR #17](https://github.com/VasiliiBabkin/sedrava/pull/17), branch `release/0.10.0-rc-preparation`; main baseline `2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1`.

**Measured implementation SHA: `64f3c7efb474d0caf91917bc4dbbfd27c9c8330e`.** All 14 applicable runs (10 PR workflows including preparation, 4 push runs) passed for this SHA. The evidence and hashes below identify that exact immutable kit. The subsequent report-only commit has its own complete repeated CI and freshly hashed kit, linked from PR #17.

**Итоговый SHA фактически выдаваемого комплекта** находится в `manifest.json.git_sha`, `rc-delivery.json.git_sha` и автоматически создаваемом `RC_010_REPORT.md` внутри самого комплекта. Этот CI-отчёт содержит точный финальный SHA, результаты и хеши именно его файлов. Репозиторный документ фиксирует измеренную реализацию; его собственный коммит неизбежно меняет Git SHA и содержимое wheel/sdist. Поэтому контрольные суммы разных коммитов не смешиваются, финальный комплект и его delivery проверяются отдельно. В итоговом PR приведены буквальный последний SHA и ссылки на его реальные артефакты.

## What changed / Что изменено

- `sedrava_version.VERSION = "0.10.0rc1"` is the one version source. Setuptools reads dynamic metadata; CLI and `sedrava.__version__` import it; generated Android versionName uses it. PEP 440 filenames and wheel/sdist metadata agree. Android development versionCode advances 1 → **10001**; the two default IDs are unchanged and regression-tested. No language/type/action/navigation/schema semantics were changed.
- Build backend versions are pinned: setuptools 84.0.0, wheel 0.48.0. Preparation tools in `requirements-rc.txt`: build 1.6.1, Twine 7.0.0, packaging 26.3, Playwright 1.62.0, PyYAML 6.0.3. Actual Python environment, JDK/Gradle/SDK properties and Android dependency tree are in the kit, not reconstructed guesses.
- Every workflow has explicit read-only permissions; all external Actions use full commit SHAs, checkout credentials are not persisted, no publication/OIDC-write permission or secret binding is introduced. The historical alpha release-attachment workflow is now audit-only; its already-published 0.9 history is preserved.
- Archive inspection bounds sizes/counts and rejects traversal, links, duplicate members, local/key filenames and high-confidence credential patterns. Wheel inventory is exact: checked modules/data, expected metadata/entry point/dependencies and valid RECORD hashes; source archives match the checkout. This is a targeted audit, not proof that every possible secret format is detectable.
- `scripts/prepare_rc.py` waits for eight mandatory gates **and every additional applicable same-SHA run**. It binds successful repository/run/SHA metadata, immutable input artifact IDs and ZIP digests; extracts data without executing downloaded code; checks source/archive/Web equality and rechecks actual APK identity/version/signature/permissions.
- The kit contains wheel, sdist, two debug APKs, Web, test evidence, toolchain/dependency records, availability observations, machine/human manifests, the final CI report and SHA256SUMS. The post-upload step downloads the immutable kit, checks its external ZIP digest and every file against the checked local directory, then emits the actual delivery artifact identity. **No rebuild happens between QA and delivery.**
- RU/EN [release notes](RELEASE_NOTES_0_10_0rc1.en.md), [upgrade/rollback](UPGRADE_0_10_0rc1.en.md) and [manual publication controls](RC_PUBLISHING.md) document installation from verified local archives, owner approval and storage/signing limits. Current README/Quick Start/Build/Roadmap/Changelog/limits are updated; historical reports remain historical.

## Results / Фактические результаты

| Gate | Measured result |
| --- | --- |
| Python 3.10 / 3.12 / 3.13 | **153 / 153 / 153** tests, including complete prior 0.9/0.10 regression and release-integrity negatives |
| Chromium | **23** real scenarios: CRUD, history/Back/Forward/reload, keyboard/focus, invalid/corrupt data, int32/Unicode, long text, 320 px and 200% font |
| JVM in main navigation workflow | **7** tests with Python oracles: task navigation 2, pages 1, scalar 1, second task manager 3 |
| Further native regression | records 4, text 4, reference 0.9 2; **17 primary-workflow JVM executions**, including 3 repeated records tests |
| APK / Lint / signature / permissions | PASS; both RC APKs versionName 0.10.0rc1 / code 10001, independent IDs, debug signatures, only expected own AndroidX signature permission |
| Android emulator API 35 x86_64 Pixel 2 | **4** native scenarios: baseline UI seed/update, navigation lifecycle, duplicate editors, second task manager; additional shell UI/storage/update assertions |
| Two installed apps | PASS: `pm path`, separate actual preferences, both relaunches and same-package update retention |
| Wheel and sdist | Built from clean checkouts; Twine, license/archive/source/RECORD audits and installation into separate venvs outside repository passed |
| Installed commands/examples | check/test/run/build web/build android on reference_09, text_profile, task_manager and task_manager_navigation; paths with spaces and CLI/metadata version agreement |
| Reproduction | Repeated generated files and wheel/sdist payloads match; timestamps/compression and APK bit identity are explicitly excluded |
| Upgrade / rollback | Actual published 0.9.0a1 wheel verified, separate RC installed, old/new reference action results agree, original environment and project bytes preserved |
| Delivered kit | Independent inventory verification + sha256sum check + actual post-upload download/digest/file equality passed |
| Documentation | 37 current documents and local links passed |
| Physical Android | **Unavailable / НЕ ПРОВЕРЕНО**; older 0.9 device results are not applied to RC APKs |

The emulator update uses the actual checked main baseline (`0.10.0.dev0`, code 1) and RC code 10001 built with the same ephemeral debug key in one job. A task **created through the baseline UI** survives `adb install -r`, same ID and a cold launch into the new actual UI. This is not a claim of compatibility with the unrelated published 0.9 APK's signing key or arbitrary schema migration. The script checks for a disposable API 35 emulator before changing an application. The normal lifecycle scenario uses font_scale=1.3 and exercises accepted edits before Save, rotation, Activity recreation, system Back, deletion and invalid input. Two-app scenarios retain independent `Second`/`restart persisted` records with stable IDs.

Local checks also built wheel/sdist from detached clean worktrees, installed each outside checkout, executed all five CLI commands, verified published baseline checksums and actual rollback, archive source checks and payload reproducibility. No local KVM/physical device was available; real Android execution was in GitHub Actions. Lint is not disabled: the main app retains 0 errors and two known ApplySharedPref/UseKtx warnings; bounded synchronous commit is intentional so write failure is observable.

## Registry / baseline observations

PyPI returned HTTP 404 for both the project and version on 2026-10-30. CI separately checks version `sedrava/0.10.0rc1` and GitHub tag/release `v0.10.0rc1` before each kit; actual UTC observations are in `availability.json`. This is not a reservation or proof of publishing/name ownership. TestPyPI was blocked by the local managed network policy, is **not checked** and is not a target of this preparation. No bypass or upload was attempted.

Actual published rollback artifact: `sedrava-0.9.0a1-py3-none-any.whl`, SHA-256 `b6e3a54df2355803fa1e47b5e7e849ba242bfd6437f226534db13aabc4210339`, from GitHub v0.9.0a1. Its release SHA256SUMS file was independently checked against `1c1dec588511c551c252b79ca3af08601d81ade57e2ad785cf50c44b8079cae2`. The name is **sedrava**, not historical intent-lng and not a fictional PyPI sedrava==0.9.

## CI / immutable measured implementation artifacts

- [Full RC kit assembly and download round trip](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712301).
- [Python matrix / Chromium / clean distributions / rollback](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712269).
- [Android / real upgrade / JVM / Lint / emulator](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712334).
- [Records](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712185), [text](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712478), [0.9 reference](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712299), [collection core](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712215), [Compose](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712380), [distribution](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712324), [CI](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712160).
- [Candidate kit for implementation SHA 64f3c7e](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712301/artifacts/12976867692), 22,773,955 bytes; actual external ZIP SHA-256 **c9cf425afd41d82fa1ac3e039a2a03af68dbc61a325f626ce4242d87c8e62867**.
- [Delivery identity](https://github.com/VasiliiBabkin/sedrava/actions/runs/41055712301/artifacts/12976957748), with `download_roundtrip_verified: true`, source SHA and real artifact ID/URL/digest.

Hashes below are **only for that measured implementation kit**, not the subsequently rebuilt documentation commit. Its internal SHA256SUMS and external artifact digest were verified before and after upload; final-head hashes are regenerated in its own kit/CI report and identified in PR #17.

| File | Verified SHA-256 (implementation 64f3c7e) |
| --- | --- |
| sedrava-0.10.0rc1-py3-none-any.whl | `9af158d0fa186bbfe525231a030ebf3c1851cbe40e0a2329ff99a6ed2a6502a3` |
| sedrava-0.10.0rc1.tar.gz | `4a3988bc0a07ea1a8b0b894ca55bfe3b3891616049e22a2f7ad16a7619d13d75` |
| task_manager_navigation-0.10.0rc1-debug.apk | `16e442d806a3233a85853ecc228602bb1f0b7344aad44350a8dbb80671d36da8` |
| task_manager-0.10.0rc1-debug.apk | `640011e27e621ffd384374360f893755e72cb2c19d8d456a92b7b0873b8137cd` |
| web-examples.zip | `3e98432d8ee713f6be61af4dfd7b37ed6d8928b2c1dd13145b24038e3f06e37a` |
| manifest.json | `6297e1c271dd32531db2bcf703b21b8cdaa52d360b2472b3e6fadf9d9128d982` |
| SHA256SUMS | `6eb1f5ddd927e32f5395c932861c3c8217d78361e0a204c1a7a5cfa655dba800` |

`manifest.json.files` covers every payload; SHA256SUMS also hashes machine/human manifests. The external immutable Actions ZIP digest binds SHA256SUMS itself. Hashes are integrity checks relative to trusted GitHub metadata, not a production publisher signature. Test evidence and tool/dependency records are included; CI constructs all URLs/IDs from real API/action results. The final generated CI report has the literal final source SHA and payload hashes; no self-referential Git hash/checksum is invented.

## Failures corrected / Исправленные неуспешные проверки

The first clean install check found that its test script could not import the new version module when started outside the checkout; its import path was fixed and real wheel/sdist tests repeated. The first candidate collector correctly refused incomplete native evidence: pages/scalar JVM XML was not uploaded despite successful test execution; raw reports were added and the unchanged minimum gate passed. No test/gate was disabled, no missing evidence was substituted by a simulated pass. Subsequent hardening rejects unexpected install-time wheel scripts, guards physical devices from the emulator-only update test, derives delivery identity from the canonical version and verifies a real post-upload download.

## Risks / GO and permission

**GO — technical readiness for a first controlled experimental RC.** Tested distributions, offline examples, independent APKs, actual upgrade/rollback, complete exact-SHA gates, hashes and immutable verified delivery exist. The owner must separately approve **version + final SHA + artifact ID/digest + publication target**, recheck availability and confirm publishing rights. Preparation does not authorize merge, tag, GitHub Release, PyPI/TestPyPI or deployment.

Remaining limitations: no physical-device validation; debug keys and development app-version defaults, no production signing; no automatic data migration/encryption, deep links/route parameters/modules/general layouts; experimental pre-1.0 compatibility. Android transitive dependencies, runner images and archive metadata are not fully locked; no byte-identical APK promise or comprehensive SBOM/accessibility certification. Name availability may change and does not confer ownership. TestPyPI remains unverified/out of scope. These limits are explicit acceptance constraints for an experimental RC, not evidence of stable production readiness.

Русский: комплект технически готов для контролируемой экспериментальной публикации. Разрешение владельца **не получено**; исходники и данные пользователя сохраняются, автоматической миграции нет. Реальные проверки Android выполнены эмулятором, физическое устройство недоступно. Все последующие действия публикации остаются отдельным решением владельца. [Notes EN](RELEASE_NOTES_0_10_0rc1.en.md) · [RU](RELEASE_NOTES_0_10_0rc1.ru.md) · [Upgrade EN](UPGRADE_0_10_0rc1.en.md) · [RU](UPGRADE_0_10_0rc1.ru.md) · [Procedure](RC_PUBLISHING.md).
