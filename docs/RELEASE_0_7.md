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

## TestPyPI: настройка / setup

1. Дождитесь успешного запуска **Intent packaging and provenance audit** на ветке `feature/intent-0.7-testpypi-prep`. В GitHub Actions должен появиться артефакт `intent-07-audited-dist`.
2. Проверьте доступность имени `intent-lang` в TestPyPI и PyPI. Имена могут быть заняты независимо; **доступность ещё не подтверждена**.
3. Создайте GitHub Environment с именем **`testpypi`**. Рекомендуется включить required reviewers, чтобы публикация требовала ручного подтверждения.
4. В TestPyPI создайте *pending trusted publisher* с параметрами:
   - GitHub owner: `VasiliiBabkin`
   - Repository: `intent-lang`
   - Workflow: `intent07-testpypi.yml`
   - Environment: `testpypi`
5. Workflow с `workflow_dispatch` должен находиться в **default branch** GitHub, иначе кнопка ручного запуска может быть недоступна. Сначала слейте проверенные изменения через pull request. Не запускайте публикацию до подтверждения владельцем.
6. В GitHub Actions вручную запустите **Publish Intent to TestPyPI (manual)**. Публикация использует OIDC Trusted Publishing; секрет API-токена не нужен.
7. После публикации установите в новом окружении:

```bash
python3 -m venv /tmp/intent-testpypi
/tmp/intent-testpypi/bin/python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ intent-lang==0.7.0a1
/tmp/intent-testpypi/bin/intent --version
```

При использовании двух индексов возможна dependency confusion: для релизной проверки предпочтительнее `--index-url https://test.pypi.org/simple/` без дополнительного индекса, поскольку текущий пакет не объявляет runtime-зависимостей.

**Публикация пока не выполнялась.** Нужна отдельная проверка прав на сторонний код, графику и название проекта. Автоматическая проверка архивов не доказывает юридическую чистоту всех файлов.

## EN: publication gate

The TestPyPI workflow is manual and uses GitHub OIDC Trusted Publishing, restricted to the `testpypi` environment. Configure a matching pending publisher on TestPyPI and review environment protection rules. GitHub manual dispatch requires the workflow to be present on the default branch. Publishing is a separate, explicitly authorized action after CI passes.
