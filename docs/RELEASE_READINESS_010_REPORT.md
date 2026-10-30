# Sedrava 0.10 — release readiness / Подготовка релиз-кандидата

Дата: 2026-10-30. PR: [#16](https://github.com/VasiliiBabkin/sedrava/pull/16), ветка `feature/010-release-readiness`, база `main` после #15. **0.10 не выпущена.**

Проверенная реализация: `a72388cb36694b0ed4f47d651010f357dce8603a`. Последующий коммит фиксирует только этот отчёт/документацию; его итоговый SHA и повторные проверки указаны в PR #16. Все активные workflow используют точный head SHA PR, а не неявный merge checkout.

## Изменения и исправления

1. Внутренний компонент `sedrava_android_identity.py` задаёт единые ID, namespace и Kotlin package. Default: `org.sedrava.app.a` + первые 32 hex-символа SHA-256 точного UTF-8 названия. Нет случайности, нормализации, зависимости от пути, времени или содержимого действий. Одинаковые названия намеренно обозначают одну идентичность; разные приложения с одинаковым названием требуют разных явных ID. Хеш не является глобальным реестром.
2. `build android --application-id com.example.daybook` отделяет идентичность от отображаемого названия. Проверка: минимум два сегмента, строчные ASCII-буквы/цифры/`_`, первая буква в каждом сегменте, до 255 символов, без ключевых слов Java/Kotlin. Gradle, package, пути исходников, manifest, тесты и аудит APK согласованы. Старый `org.sedrava.generated` доступен только явным выбором.
3. Метаданные `sedrava-android.json` ограничены по размеру; проверяются схема, типы, Unicode, неизвестные и дублирующиеся ключи. Повреждение и конфликт ID отклоняются до изменения проекта, с понятной ошибкой вместо traceback. Старые каталоги без метаданных пересоздаются в новом output. Для безопасного обновления нужны прежние ID, сертификат и совместимая схема данных.
4. Название лаунчера — экранированный Android string resource. Unicode, кавычки, `@`, `?`, `$`, пробелы и переводы строк не превращаются в ресурсы/код. Специальное название и явный namespace собираются в scalar-фикстуре. XML-недопустимые Unicode-скаляры кодируются как `\uXXXX`; все управляющие U+0000..U+001F и U+FFFE/U+FFFF проверены ресурсным тестом. Дополнительный локальный APK с U+0000/U+0001/U+FFFE в названии успешно собран.
5. Web: единый заголовок для старых экранов, читаемые поля/кнопки, видимый клавиатурный фокус; навигационные карточки и сетка корректно переносят длинный текст на узком экране, вторичный текст контрастнее, статус связан с кнопкой через `aria-describedby`. Compose: безопасные системные/IME-отступы, растущие по содержимому кнопки, поля во всю ширину, иерархия заголовков, `heading`, `stateDescription` и live-region ошибок.
6. В навигационных UI действия, меняющие данные, и выбор карточек недоступны при видимом недопустимом черновике. Чистые переходы и Back остаются доступны и отбрасывают черновики, как ранее. Принятые данные не меняются. Ошибки Compose учитываются отдельно для каждого редактора, в том числе двух редакторов одного поля. Legacy single-screen поведение сохранено.
7. CLI Web сначала полностью проверяет/генерирует результат, затем создаёт output; ошибочная программа не оставляет пустой каталог. Проверены `check`, `test`, `run`, обе сборки, неверный UTF-8, отсутствующий файл, ошибки флагов и недопустимые ID. Коды: 0 — успех, 1 — ошибка программы/файла/генерации, 2 — неверные аргументы argparse.
8. Wheel содержит модули, документацию, `.sdr`-примеры и лицензию (`sys.prefix/share/sedrava`); sdist содержит также тесты и инженерные скрипты. Оба устанавливаются в отдельные venv, запускаются вне checkout и в путях с пробелами. Проверяется воспроизводимость содержимого wheel/sdist между двумя сборками, без сравнения временных меток/сжатия. Шаблоны встроены в поставляемые Python-модули.

Ядро типов, int32/Unicode, действия/инварианты, стабильные ID записей и семантика стека не переписаны. Совместимые старые программы не требуют изменения `.sdr`. Обновлены README, Quick Start, Build, справочники, Roadmap, Changelog, ограничения, русские и английские инструкции по ID. Исторические отчёты помечены историческими, текущие руководства больше не утверждают, что примеры всегда заменяют друг друга.

## Фактические проверки

| Проверка | Результат |
| --- | --- |
| Python 3.10 / 3.12 / 3.13 | **141 / 141 / 141**, включая всю прежнюю регрессию и новые позитивные/негативные проверки |
| Настоящий Chromium | **23** сценария: CRUD, история/Back/Forward/reload, клавиатура/фокус, повреждённые данные, Unicode/int32, invalid drafts, длинная запись 1024 символа при 320 px и шрифте 200% |
| JVM, основной navigation workflow | **7**: task navigation 2, empty-domain pages 1, scalar/escaping 1, second task manager 3; Python-эталон и канонический JSON/стек |
| JVM, регрессионные workflow | records **4**, text **4**, reference 0.9 **2**; всего **17 выполнений JVM-тестов**, из них 3 records повторены в основном workflow |
| APK / Android Lint | Оба менеджера: APK и Lint без ошибок; дополнительные фикстуры: APK/JVM и компиляция инструментальных тестов |
| Подпись / identity / permissions | `apksigner verify`, application ID против метаданных, `aapt`: только собственное signature-разрешение AndroidX; нет Internet/storage/camera/location |
| Эмулятор Android API 35, x86_64, Pixel 2 | **3** Compose-сценария основного workflow: navigation lifecycle, duplicate scalar editors, second task manager; не замена компиляцией |
| Wheel / sdist | Метаданные Apache-2.0, состав архивов, Twine, чистые установки и `check/test/run/build web/build android` проходят |
| Воспроизводимость | Генерируемые файлы в разных каталогах совпадают; содержимое архивов совпадает при повторной сборке |
| Документация | 30 текущих файлов и локальные ссылки проверены |
| Физический Android | **Не проверено**: устройство недоступно; старые результаты 0.9 не переносятся на новые APK |

Compose lifecycle проверяет добавление, выбор, принятое переименование перед Save, поворот, `scenario.recreate()`, сохранение изменений, завершение задачи, системный Back, удаление выбранной записи, отказы ввода/действий и новый запуск процесса. Основной сценарий выполняется при системном `font_scale=1.3`. Отдельный scalar-сценарий проверяет, что второй редактор с тем же принятым значением не снимает ошибку первого и не разрешает действие со скрытым старым вводом.

Локально также прошли Python/Chromium, APK/JVM/Lint/instrumentation compilation и проверки дистрибутива; локального KVM нет, эмулятор выполнялся в GitHub Actions. Два оставшихся предупреждения Lint основного приложения — `ApplySharedPref` и `UseKtx`: синхронный ограниченный `commit()` сохранён намеренно, чтобы сообщать о неудаче записи; проверка Lint не отключена.

При реализации обнаруженная регрессия, блокировавшая чистый переход после неверного ввода, исправлена с сохранением прежнего Chromium-теста. Первоначальные тесты фиксированного namespace обновлены на проверку разрешённой идентичности и реального возвращённого пути; они не удалены. Неуспешные промежуточные прогоны не используются как доказательство готовности. В records workflow на предыдущем SHA `b343bd1` был сбой разрешения пяти существующих Maven Central test-зависимостей (Could not find); повторён весь неуспешный job, включая JVM, APK, Lint и эмулятор, без отключения проверок.

## Две одновременно установленные программы

- `task_manager_navigation.sdr` / Daybook · Tasks: `org.sedrava.app.af44c2608593529f9c803c46e60a5a99d`.
- `task_manager.sdr` / Sedrava Tasks: `org.sedrava.app.ae42ed66f07aefa1c223e4fbcec5fa57b`.

В одном эмуляторе установлены оба APK; `pm path` подтверждает обе установки. Первый содержит `next_id=3`, запись `{id:2,title:"Second",done:true}`; второй — независимую `{id:2,title:"restart persisted",done:false}`. После `adb install -r` первого APK оба сохранения проверены повторно через настоящий `run-as`/SharedPreferences. Первый холодный запуск возвращается на main с сохранённой задачей; второй сценарий также проверяет восстановленную задачу в интерфейсе. XML, screenshots, package paths, font scale и SHA256SUMS приложены к артефакту. Сгенерированный application Kotlin/HTML вручную не изменяется; тестовые скрипты добавляют только тесты и зависимости тестирования.

## Воспроизведение

```sh
python -m pip install '.[test]' build twine playwright==1.62.0
python -m unittest discover -s tests -v
python -m playwright install --with-deps chromium
python scripts/test_web_browser.py
python scripts/check_docs.py
python -m build
python -m twine check dist/*
python scripts/audit_dist.py
python scripts/check_reproducible_dist.py
python scripts/check_installed_dist.py

sedrava build web examples/task_manager_navigation.sdr --output build/navigation-web/index.html
sedrava build android examples/task_manager_navigation.sdr --output build/navigation-android
python scripts/prepare_navigation_android_tests.py build/navigation-android
python scripts/prepare_navigation_ui_tests.py build/navigation-android
gradle -p build/navigation-android --no-daemon :app:assembleDebug :app:testDebugUnitTest :app:lintDebug :app:assembleDebugAndroidTest
# Full two-app/fixture/emulator sequence:
# .github/workflows/navigation-010.yml
```

Инструменты Android: JDK 17, Gradle 8.11.1, AGP 8.9.2, Kotlin 2.0.21, SDK/build-tools 35, Compose BOM 2024.12.01. Runtime приложений автономен; первая сборка требует загрузки зависимостей. SDK и test dependencies не поставляются в wheel.

## CI и артефакты

Проверенная реализация `a72388cb36694b0ed4f47d651010f357dce8603a`:

- [Navigation / две установки / APK / JVM / Lint / эмулятор](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699984).
- [Python 3.10/3.12/3.13 / Chromium / wheel / sdist](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699967).
- [Records](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699931), [text](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699917), [0.9 reference](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699941), [Compose](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699921), [distribution](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699946), [CI](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699962).
- [Два APK, Web, JVM/Lint/emulator evidence и SHA256SUMS](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699984/artifacts/12970208621).
- [Все автономные Web-примеры](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699967/artifacts/12969199521), [Chromium traces](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699967/artifacts/12970137552), [wheel/sdist](https://github.com/VasiliiBabkin/sedrava/actions/runs/41040699967/artifacts/12969897495).

В ZIP основного артефакта: `navigation-android/app/build/outputs/apk/debug/app-debug.apk`, `tasks-android/app/build/outputs/apk/debug/app-debug.apk`, `navigation-web/index.html`, отчёты JVM/Lint/instrumentation, XML/PNG после рестарта и сведения совместной установки. Дополнительные Web-примеры и дистрибутивы — в alpha-артефактах. Для итогового коммита отчёта PR #16 содержит отдельные ссылки на повторно проверенные CI и артефакты именно его SHA.

## Ограничения и решение

[Полные ограничения](KNOWN_LIMITATIONS.md); [ID EN](ANDROID_ID.en.md), [ID RU](ANDROID_ID.ru.md).

Нет миграций/шифрования, глубоких ссылок, параметров маршрутов, вкладок, модулей и общей системы вёрстки. Идентичные названия требуют разных явных ID для независимых приложений. Генерируемый versionCode=1/debug-подпись — для разработки; ключи разных машин могут отличаться. Нет Gradle wrapper, lockfiles, SBOM и обещания побитно одинакового APK; сравнение содержимого архивов не гарантирует одинаковые timestamps/compression или неизменность транзитивных зависимостей. Не выполнена полная сертификация доступности и физическое тестирование новых APK. Пределы языка и ресурсов сохранены.

**GO — техническая подготовка первого экспериментального релиз-кандидата.** Все 8 применимых PR-workflow и 5 push-workflow реализации завершились успешно; оба автономных приложения получены из `.sdr`, одновременно установлены и проверены. Исправимых блокирующих проблем в проверенном объёме не осталось. Это не выпуск Sedrava 0.10 и не разрешение публикации. Физическое устройство недоступно и остаётся явным ограничением; полной production/доступностной сертификации не заявляем. PR не объединён, релиз/тег не созданы, пакет и сайт не опубликованы.

## English summary

Technical RC readiness is measured for one-source offline Web/Android applications. Deterministic title-derived identity and validated explicit overrides allow the two generated task managers to coexist with independent private data; a same-package debug update retains accepted state. Namespace/package paths, launcher resource escaping, permission/signature verification and harnesses agree. UI improvements cover semantic hierarchy, scalable/wrapping text, keyboard focus, native status/error semantics and per-editor invalid-draft action states. Pure navigation and core language semantics remain compatible.

The measured suite is 141 Python tests on each of 3.10/3.12/3.13, 23 Chromium scenarios, 17 JVM test executions across relevant workflows (including 3 repeated records tests), and 3 main-workflow Compose emulator scenarios. Clean wheel and sdist installations exercise all CLI commands outside the checkout; source/Web generation and archive payload reproducibility are checked. New 0.10 APKs have not been tested on a physical device. No merge, tag, release, package publication or site deployment was performed. The recommendation concerns a first experimental RC review, not a stable production release.
