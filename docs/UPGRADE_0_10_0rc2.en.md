# Upgrade to 0.10.0rc2 and rollback — not published

Distribution/CLI: **sedrava**. Published baseline is GitHub **0.9.0a1**, not an
invented PyPI `sedrava==0.9`; `intent-lng` is another historical package. rc1 and
rc2 kits are Actions artifacts, not package-index releases. Preserve the rc1 kit.

1. Record the old interpreter path, `sedrava --version`, `python -m pip show sedrava`.
   Back up source projects and saved data separately. Keep original environments
   and use project copies. Schema/data migration is not implemented.
2. Download the **exact reviewed rc2 SHA's kit**. Check the immutable Actions ZIP
   digest, then every SHA256SUMS entry and manifest inventory using
   [the controlled procedure](RC_PUBLISHING.md). Keep kit, receipt and checksums.
3. Install the verified wheel into a separate environment:

```sh
python -m venv .venv-sedrava-rc2
. .venv-sedrava-rc2/bin/activate
# Windows PowerShell: .venv-sedrava-rc2\Scripts\Activate.ps1
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc2-py3-none-any.whl
sedrava --version
# sedrava 0.10.0rc2
python -m pip show sedrava
sedrava check /path/to/copied/project.sdr
sedrava test /path/to/copied/project.sdr
sedrava run /path/to/copied/project.sdr
sedrava build web /path/to/copied/project.sdr --output build/rc2-web/index.html
sedrava build android /path/to/copied/project.sdr --output build/rc2-android
```

4. Check all bundled examples (`reference_09`, `text_profile`, `task_manager`,
   `task_manager_navigation`) in `sys.prefix/share/sedrava/examples` and real UI.
5. Interpreter rollback: `deactivate`, activate the **unchanged old environment**,
   confirm its version, check/test the original project. Do not feed 0.10-only
   syntax to 0.9. If needed create another environment with the checked historical
   `sedrava-0.9.0a1-py3-none-any.whl` from GitHub v0.9.0a1; its SHA-256 is
   `b6e3a54df2355803fa1e47b5e7e849ba242bfd6437f226534db13aabc4210339`.
   Verify the release SHA256SUMS too. The automated rollback check uses this
   actual published wheel and verifies unchanged project bytes and old behavior.

## Android rc1 → rc2

Same application ID **and signing certificate**, code **10001 → 10002** are
required. Code/source changes here do not change default IDs. For your own app,
keep a stable explicit `--application-id`; default IDs hash the exact title.
Build using the original signing key. Debug keys differ across machines/jobs.
Never uninstall or clear data as an update recipe: install the compatible,
same-key rc2 APK over rc1, e.g. `adb install -r /path/to/rc2.apk` on your test device.
Then cold launch and verify actual data, navigation and error handling.

CI rebuilds the immutable rc1 source SHA
`6ddae99fc837d67b465285f629d9f5a2ec52e870` and rc2 in one job with one debug key.
It creates data through rc1's UI and **then** performs an actual install -r update,
checks ID/cert/code, saved values/stable IDs, and a second cold restart. Separate
rc1→rc2 updates seed malformed/incompatible saved data and check visible rejection
and original retention after restart. Independent scenarios provision a fresh
old baseline **before** seeding; no uninstall/clear occurs between the seed and
its update. This is not a clean-install claim and does not modify the original
rc1 artifact or claim possession of that earlier runner's debug private key.

Android rollback is not interpreter rollback: a lower versionCode normally
cannot replace rc2. `adb install -d` is not a safe data-migration promise. Keep
old APK/source/data backups; do not erase the only copy to force a downgrade.
The older 0.9 default package `org.sedrava.generated` differs from current hashed
IDs; only reuse it for that same app with its own original key and compatible
storage. Otherwise you install an independent app, not an update.

## Storage

Read [compatibility](COMPATIBILITY_010.md): exact fingerprints, transient defaults,
final rules, legacy scalar format and local storage identities. There is no
automatic format upgrade/downgrade. Back up rejected originals before manually
removing anything; rc2 protects them from recovery writes. Accepted edits may
remain temporary when saving is blocked. Web origin/path/title changes select
another storage key; changing query/hash does not. No cross-app/device transfer,
conflict resolution, encryption or guaranteed power-cut recovery is provided.

[Русский](UPGRADE_0_10_0rc2.ru.md) · [Release notes](RELEASE_NOTES_0_10_0rc2.en.md).
