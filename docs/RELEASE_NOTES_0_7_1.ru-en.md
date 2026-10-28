# Sedrava v0.7.1a1 — First Sedrava GitHub Alpha

**Pre-release / Experimental. Not published on PyPI.**

## English

Sedrava Programming Language is an experimental declarative language for application state, actions, transitions, invariants and executable tests. This is the first GitHub alpha candidate under the Sedrava name, succeeding the former project identity without backwards-compatible aliases.

- Python interpreter, typed AST, state machine and invariant validation.
- Command-line tool `sedrava` for checking, testing and generating applications.
- Self-contained HTML/JavaScript Web generator and Android/Jetpack Compose project generator.
- Source file extension `.sdr`.
- Automated Python, Web and Android build checks.

**Requirements:** Python 3.10+; Android builds additionally need Java, Android SDK and Gradle.

**Install from source (no PyPI release):**

```bash
git clone https://github.com/VasiliiBabkin/sedrava.git
cd sedrava
python -m pip install .
sedrava --version
sedrava check examples/workflow.sdr
sedrava test examples/workflow.sdr
sedrava build web examples/workflow.sdr --output build/web/index.html
sedrava build android examples/workflow.sdr --output build/generated-android
```

**Limitations:** alpha-stage syntax and APIs; incomplete diagnostics and conformance coverage; generated Android APK is a demo, not an IDE or language runtime. No stability or backward-compatibility guarantees. No official website has been announced.

## Русский

**Sedrava (Седрава)** — экспериментальный декларативный язык для описания состояния приложения, действий, переходов, инвариантов и исполняемых тестов. Это первый кандидат на публичный GitHub-релиз под новым названием.

В составе: интерпретатор Python, типизированное AST, CLI `sedrava`, генераторы Web (HTML/JavaScript) и Android/Jetpack Compose. Файлы программ имеют расширение `.sdr`.

Установка из исходников приведена выше. Публикация пакета в PyPI **не выполнялась**. Версия предварительная, стабильность интерфейсов и полная совместимость пока не гарантируются. Android APK демонстрирует сгенерированное приложение, а не среду разработки языка.

## GitHub release checklist

1. Confirm CI and Android build pass for the final commit.
2. Create GitHub Release with tag `v0.7.1a1` targeting `main`, title `Sedrava v0.7.1 Alpha — First Public Release`, and mark it **Pre-release**.
3. Paste these notes. GitHub automatically provides source archives. Attach tested wheel/sdist and Android demo APK only if they were built from this exact commit and verified.
4. Do **not** enable PyPI/TestPyPI publishing workflows.
