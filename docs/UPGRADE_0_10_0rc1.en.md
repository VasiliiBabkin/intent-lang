# Upgrade to 0.10.0rc1 and rollback (not published)

The actual distribution/CLI is **sedrava**. Published baseline: [GitHub v0.9.0a1](https://github.com/VasiliiBabkin/sedrava/releases/tag/v0.9.0a1), package version `0.9.0a1`. It is not a PyPI `sedrava==0.9` install; do not install the historical `intent-lng` project as a substitute. The RC kit is currently an Actions artifact, not a PyPI/TestPyPI release.

1. Keep the old environment. Record its interpreter path, `python -m pip show sedrava` and `sedrava --version`. Back up `.sdr` projects, generated files you need and persistent state/storage separately. Use a copy of each project for RC; no migration is promised.
2. Download the kit for the exact reviewed SHA, verify the external artifact digest and the internal file inventory as in [the procedure](RC_PUBLISHING.md). Keep the original kit and SHA256SUMS as immutable rollback/diagnostic evidence.
3. Create a **separate** environment, then install only the checked wheel:

```sh
python -m venv .venv-sedrava-rc1
. .venv-sedrava-rc1/bin/activate
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc1-py3-none-any.whl
sedrava --version
python -m pip show sedrava
sedrava check /path/to/copied/project.sdr
sedrava test /path/to/copied/project.sdr
sedrava run /path/to/copied/project.sdr
sedrava build web /path/to/copied/project.sdr --output build/rc-web/index.html
sedrava build android /path/to/copied/project.sdr --output build/rc-android
```

4. Validate bundled `reference_09.sdr`, `text_profile.sdr`, `task_manager.sdr`, `task_manager_navigation.sdr` too. They live at `sys.prefix/share/sedrava/examples`. Run real Web/Android scenarios before relying on accepted data. See [release notes](RELEASE_NOTES_0_10_0rc1.en.md).
5. Roll back by leaving the RC environment and reactivating the original one. Windows activation uses `ENV\Scripts\activate`; POSIX uses `ENV/bin/activate`.

```sh
deactivate
. /absolute/path/to/original-09-environment/bin/activate
sedrava --version
# Expected: sedrava 0.9.0a1
sedrava check /path/to/original-09-project.sdr
sedrava test /path/to/original-09-project.sdr
```

If the original environment is unavailable, create another venv and install the verified historical wheel from the GitHub release. Its actual name is `sedrava-0.9.0a1-py3-none-any.whl`; SHA-256 **b6e3a54df2355803fa1e47b5e7e849ba242bfd6437f226534db13aabc4210339**. Download its release `SHA256SUMS`, verify the wheel before `pip install --no-index /path/to/that-wheel`. The automated `scripts/check_upgrade_rollback.py` downloads this published wheel, checks its digest/release inventory, exercises check/test/run/Web/Android in old and RC environments outside the checkout, compares the 0.9 reference action result, returns to the unchanged old environment and verifies project bytes were not modified. It never installs from an invented package name/version on an index.

## Data and Android boundaries

0.9 cannot parse new text/record/navigation syntax. Switching interpreters back does not translate a new project. Keep original sources under version control. Never feed new collection snapshots to the old runtime or overwrite the only original state backup. Collection/navigation snapshot schema/signature changes are rejected in full; no automatic data migration/downgrade exists. Accepted 0.9 scalar programs are regression-tested, not every possible external app/data format.

Android identity and signing certificate must remain unchanged for an update; `versionCode` must be accepted by Android. Earlier 0.9 generators used `org.sedrava.generated`; current defaults hash the exact title. Use `--application-id org.sedrava.generated` **only for the same old application**, with its original signing key and compatible data schema. Otherwise the new ID creates a separate app. Debug keys from different machines/jobs may differ. Do not uninstall/clear data as an upgrade recipe: that deletes data. The RC's development code is 10001; Android may reject installing older code 1 over it. Keep the old APK/data separately; `adb install -d` is not a guaranteed safe data downgrade. The kit does not provide a production backup/migration tool.

The emulator verifies an actual same-key update from main `2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1` (`0.10.0.dev0`, code 1) to RC (code 10001), with UI-created tasks and unchanged stable IDs. It does **not** claim an upgrade over the published 0.9 APK's unrelated debug key or general schema migration. Web storage is scoped by URL pathname plus title; changing either starts another snapshot. Browser data is not automatically imported into another generated HTML file.

[Русский](UPGRADE_0_10_0rc1.ru.md).
