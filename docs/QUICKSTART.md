# Quick Start / Быстрый старт

**Describe the application; get the application. / Опиши приложение — получи приложение.**

Sedrava describes local application state, rules, actions and a small UI. The 0.9 alpha targets learning and experimental offline applications; it is not a production framework. No accounts, cloud service or runtime Python dependencies are required.

## Install / Установка

Install Python 3.10+ and Git. From a terminal:

```sh
git clone https://github.com/VasiliiBabkin/sedrava.git
cd sedrava
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
sedrava --version
sedrava --help
```

For this unpublished candidate, checkout the alpha PR branch if it has not been merged. Do not `pip install sedrava` from PyPI: no Sedrava package has been published there. On Windows `py -3` may be needed instead of `python`; quote paths containing spaces.

Create `hello.sdr` (plain UTF-8):

```sedrava
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

Open http://localhost:8000. `run` prints `{"count": 2}`; it is a deterministic interpreter, with no UI or event loop. `check` checks declarations, types, initial values and rules; `test` executes embedded tests. Builds also execute embedded tests. Ctrl+C stops the HTTP server.

Next: [language syntax and semantics](LANGUAGE_0_9.md), [complete examples](../examples/README.md), [Web/Android build guide](BUILD.md), [FAQ](FAQ.md), [known limitations](KNOWN_LIMITATIONS.md).

Русский: установите Python и Git, создайте виртуальное окружение и установите проект командой `python -m pip install .`. Сохраните пример в UTF-8, проверьте его командами `check` и `test`. `run` выводит состояние после указанных действий; `build web` создаёт HTML, а `build android` — исходный Gradle-проект. Для APK нужны дополнительные инструменты из инструкции сборки. Синтаксис языка остаётся английским.
