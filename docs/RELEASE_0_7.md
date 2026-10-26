# Intent 0.7 — Release candidate / Кандидат на выпуск

## RU

Это экспериментальная версия, **не опубликованная в PyPI или TestPyPI**.

Установка из ветки разработки (в виртуальном окружении):

```bash
python -m pip install --upgrade "git+https://github.com/VasiliiBabkin/intent-lang.git@feature/intent-0.7-diagnostics-release"
intent --version
intent check examples/workflow.intent
intent test examples/workflow.intent
```

Файлы `examples/workflow.intent` нужно предварительно скачать или выполнять команды из клона репозитория.

Порядок публикации:
1. Убедиться, что все шесть комбинаций ОС и Python прошли CI.
2. Скачать артефакт `intent-07-release-candidate` из GitHub Actions.
3. Проверить, что имя `intent-lang` доступно в реестре, и утвердить лицензию.
4. Настроить аккаунт TestPyPI и Trusted Publishing для этого репозитория.
5. Опубликовать артефакт в TestPyPI отдельным контролируемым действием.
6. Установить пакет из TestPyPI в чистое окружение и выполнить smoke-тест.
7. Только после этого решать вопрос о публикации в основном PyPI.

Никакие токены или пароли реестра не должны сохраняться в исходном коде.

Ограничения: диагностические сообщения ещё не содержат координаты для всех ошибок выражений; тесты Python/JavaScript не доказывают эквивалентность для произвольных программ и чисел.

## EN

This is an experimental release candidate and is **not published to PyPI or TestPyPI**.

Install from the development branch in a virtual environment:

```bash
python -m pip install --upgrade "git+https://github.com/VasiliiBabkin/intent-lang.git@feature/intent-0.7-diagnostics-release"
intent --version
```

Before publishing, verify all CI matrix jobs, inspect the built artifacts, confirm the package name and license, configure TestPyPI Trusted Publishing, and test installation from TestPyPI in a clean environment. Do not commit publishing credentials.
