# Quick Start / Быстрый старт — Sedrava 0.10.0

**Published release:** [GitHub v0.10.0](https://github.com/VasiliiBabkin/sedrava/releases/tag/v0.10.0) · [PyPI](https://pypi.org/project/sedrava/0.10.0/). Sedrava remains experimental, not a production-support guarantee.

## Install / Установка

Requires Python **3.10+**. Use a virtual environment:

```sh
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install sedrava==0.10.0
sedrava --version
```

To work from a repository checkout instead, use `python -m pip install .`. On Windows `py -3` may be needed.

## First app / Первое приложение

Create a UTF-8 file `hello.sdr`:

```text
app "Hello Sedrava"
state count = 0
action add: count = count + 1
rule count >= 0 and count <= 10
test once: add -> count == 1
screen main:
    text "Hello Sedrava"
    value count
    button "Add" -> add
```

```sh
sedrava check hello.sdr
sedrava test hello.sdr
sedrava run hello.sdr add add
sedrava build web hello.sdr --output build/web/index.html
python -m http.server 8000 --directory build/web
```

Open http://localhost:8000. The `run` command prints `{"count": 2}`; it is not a GUI. The Web generator produces a standalone HTML application.

## Text, records and navigation / Текст, записи и навигация

Included in **0.10.0**: [text](LANGUAGE_0_10_TEXT.md), [records and bounded lists](RECORDS_COLLECTIONS_010.md), [multi-screen navigation](NAVIGATION_010_CONTRACT.md). Clone the repository to use the checked-in examples:

```sh
git clone https://github.com/VasiliiBabkin/sedrava.git
cd sedrava
sedrava check examples/task_manager_navigation.sdr
sedrava test examples/task_manager_navigation.sdr
sedrava build android examples/task_manager_navigation.sdr --output build/tasks-android
```

`build android` generates Kotlin/Compose source, **not an APK**. Compile with JDK, Android SDK and Gradle per [BUILD.md](BUILD.md). Data migrations and encrypted persistence are not provided. Final 0.10 APK physical-device acceptance is not recorded.

`sedrava build site` is experimental in [draft PR #22](https://github.com/VasiliiBabkin/sedrava/pull/22), **not** part of the released CLI. [sedrava-site](https://github.com/VasiliiBabkin/sedrava-site) is a separate Astro/Starlight website.
