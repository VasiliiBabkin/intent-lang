# Codex implementation task: Sedrava 0.10 text core

Work in branch `feature/010-string-core` and existing PR #12. Do not open a duplicate PR. Read `docs/DESCRIBE_GET_010.md`, `docs/STRING_010_CONTRACT.md`, `docs/LANGUAGE_0_9.md`, source generators and existing tests before editing.

Goal: deliver first-class text state end-to-end. **Describe → Get:** a concise Sedrava program with text input must produce a working Web app and Android APK without modifying generated code.

Implement the proposed contract across `sedrava_core.py`, `web_codegen.py`, `android_codegen_v03.py`, CLI, tests, examples and docs. Do not limit work to parser-only support. Preserve all 0.9 behavior and do not change published 0.9.0a1 tag or artifacts. Keep package version unreleased until full 0.10 milestones are accepted.

Key engineering issues to resolve:
1. Source grammar currently uses regex for `app`, `text`, `show` and Python AST for expressions. Add escape-aware parsing for quoted text without breaking 0.9 literal labels; reject invalid escapes and unpaired surrogates.
2. Use exact scalar-sequence equality. JavaScript strings use UTF-16; enforce 1024 Unicode scalar values via code-point iteration, not JS `.length`. Define handling of unpaired surrogates at browser input and persistence boundaries.
3. Core `checked_int`, `type_of`, `evaluate`, `resolve` and `transition` must support strings with exact type checks. Preserve atomic rejection and validate derived values after each assignment.
4. Web generated code: safe script serialization, validated text drafts, visible accessible errors, accepted-state persistence and corrupt-snapshot fallback.
5. Android Compose generated code: text state and input, correct escaping, persistence type validation, atomic actions and activity recreation. Build a real APK, run Lint and JVM tests. Use emulator/ADB if available; otherwise disclose lack of UI runtime test.
6. Add `examples/text_profile.sdr` with embedded tests; choose initial default that satisfies any nonempty rule (e.g. `state name = "Guest"`), then exercise valid rename and rejected blank input.
7. Run full existing CI and expanded conformance, browser and Android tests. Add regression cases for `</script>`, `$\{...}`, quotes, slash, newline, Unicode, emoji, long text, malformed persisted data and action atomicity.
8. Update language reference, Quick Start and roadmap to distinguish published 0.9 from unreleased 0.10. No PyPI, tag or release.

Finish with exact commits, workflow links, actual test counts, generated APK artifact and honest remaining limitations. If a design contract conflicts with implementation realities, document the deviation and add a conformance test rather than silently changing semantics.
