> Historical increment evidence below. Current 0.10 Android builds use [independent application IDs](ANDROID_ID.en.md); [readiness report](RELEASE_READINESS_010_REPORT.md) supersedes the old shared-package limitation.

# Sedrava 0.9 reference app / Эталонное приложение

The file [`examples/reference_09.sdr`](../examples/reference_09.sdr) is a cross-platform verification target, **not a polished consumer application**.

## Covered language features

- Three persisted integer states: `goal`, `progress`, `sessions`.
- Numeric input with a declarative range rule (`goal` 1–20).
- Derived flags (`reached`, `active`) and conditional text.
- Guarded actions, reset and restore.
- Four language-level tests; Python, Web and Android code-generation regression checks.

## Build and install / Сборка и установка

1. Open [reference APK workflow](https://github.com/VasiliiBabkin/sedrava/actions/workflows/reference-09-android.yml).
2. Select the latest **successful** run.
3. Download artifact `sedrava-09-reference-debug-apk` and install `app-debug.apk`.
4. Android launcher label is **Sedrava Demo**; the app screen is **Sedrava 0.9 Lab**. It uses the same application ID as the basic Workflow demo and may replace it on installation.

Local commands:

```bash
python sedrava_cli.py test examples/reference_09.sdr
python web_codegen.py examples/reference_09.sdr --output build/reference-web/index.html
python android_codegen_v03.py examples/reference_09.sdr --output build/reference-09-android
```

## Physical device acceptance checklist / Проверка на телефоне

1. Launch app; goal 5, progress 0, sessions 0.
2. Tap Add progress five times: progress 5, sessions 5, “Goal reached!” visible; sixth tap does not increment.
3. Tap Undo progress: progress 4 and “Keep going” visible; sessions remains 5.
4. Change goal to 3 when progress is 4: **must be rejected**, with an error message and editable draft retained. Correct goal to 6: **must be accepted**.
5. Enter 0, letters and a number outside 32-bit range: reject without changing accepted state.
6. Force-close/relaunch: only accepted values survive. Test reset and restore.
7. Compare equivalent actions and validation on generated Web page.

**Device results:** baseline `workflow.sdr` Android launch/actions were confirmed by a tester on 2026-10-29. **Reference app was installed and visually verified on a physical Android device on 2026-10-29.** User-provided screenshots show default state (goal 5, progress 0, sessions 0, reached false) and accepted goal 6 with progress 6, sessions 6, reached true and conditional success message. User confirms expected behavior. This supports basic numeric input, action updates, derived flags, conditional UI and reset/default display. Subsequent manual tests confirmed rejected edits, overflow rejection and state persistence after relaunch. See [Android acceptance](ANDROID_09_ACCEPTANCE.md).

## Limitations

This is a single-screen Android Compose example. Strings/collections, multi-screen navigation, accessibility review and real-world application design are later milestones. This document is the canonical test plan for the 0.9 reference APK.

### Additional physical-device result (2026-10-29)

Tester reports that the reference app retains the edited goal after relaunch; screenshot shows `goal: 20`, `progress: 0`, `sessions: 0`, `reached: false`. This confirms goal persistence for the tested relaunch scenario. Subsequent tests confirmed nonzero progress/sessions persistence, invalid-input rejection, overflow rejection and preservation of rejected editable draft. See [Android acceptance](ANDROID_09_ACCEPTANCE.md).

## Alpha regression follow-up (new binaries)

Historical manual Android 16 results above apply to the previously tested binary. After generator changes, additionally test: rotate with nonzero counters and an accepted goal, background/restore the Activity, force-stop/relaunch, enter a value causing arithmetic failure in a derived/rule expression, inspect `adb logcat` for `FATAL EXCEPTION`, and clear/corrupt saved fields to verify default recovery. A JVM validation test is not a replacement for these UI checks. See [current audit](ALPHA_AUDIT.md) and [build guide](BUILD.md).
