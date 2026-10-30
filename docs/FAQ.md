> This checkout includes the [unreleased text increment](LANGUAGE_0_10_TEXT.md). Historical 0.9 restrictions below apply to the published baseline; text state/input is now supported on this development branch. Records, bounded lists and navigation are also implemented in the unreleased development increment; see [navigation](NAVIGATION_010_CONTRACT.md).

# FAQ and troubleshooting / Вопросы и устранение ошибок

**What can I build?** Small integer/boolean state applications with explicit user actions, validation, persistence and a single screen. See [examples](../examples/README.md). Sedrava is an alpha learning/experimentation tool.

**Does `run` open the application?** It prints interpreter state as JSON after the specified actions. Use `build web` or `build android` for a UI. It starts from defaults and does not load browser/Android data.

**Does `check` run my tests?** It parses/types/checks initial values and invariants. `test` and `build` execute embedded tests. Each test starts fresh. Runtime overflows in actions only appear when the action executes.

**Why is an action rejected?** Final candidate violates a `rule`, or an arithmetic/derived intermediate overflows. The accepted state remains unchanged. Test failures exit 1; invalid command-line arguments exit 2. See [semantics](LANGUAGE_0_9.md).

**Why does an invalid input stay visible?** It is an editable draft, separate from accepted state. Correct it to an admissible number. Accepted changes persist only for fields marked `persist`. Rejected drafts are not durable data.

**Can I divide or use strings/lists?** No division, string state, automatic timers, collections or multiple screens in 0.9. String labels are static literals. These restrictions describe 0.9 only; text, bounded record lists and named screens are implemented in the unreleased 0.10 development branch. Division and automatic timers remain unsupported.

**`sedrava: command not found`** Activate the virtual environment used for `python -m pip install .`. Check `python -m pip show sedrava`. The source fallback is `python sedrava_cli.py --help`.

**Paths with spaces?** Quote each argument: `sedrava check "My project/app.sdr"` and `--output "My build/index.html"`. Never concatenate untrusted shell arguments yourself.

**Gradle says JAVA_COMPILER is missing?** You have a JRE. Install a full JDK and set `JAVA_HOME` to it. Verify `javac -version`; Java 17 is recommended.

**SDK not found / licenses missing?** Set `ANDROID_HOME` correctly and run `sdkmanager --licenses`. Install SDK 35 and build-tools 35.0.0. Do not commit machine-specific `local.properties`.

**Gradle cannot download dependencies?** Verify network/proxy/CA configuration for the JVM as well as the shell. Do not disable TLS verification. First builds need Google/Maven/Gradle repositories. Generated projects can later build with cached dependencies; offline success is not guaranteed on a fresh machine.

**Android example unexpectedly has old state?** Current builds use deterministic title-derived IDs. Identical titles deliberately share an ID; use distinct `--application-id` values for independent apps. Older binaries used a shared ID. Data migrations remain unavailable. See [Android identity](ANDROID_ID.en.md).

**No data after browser reload?** Serve via HTTP at the same origin/path/name. Browser privacy settings, storage quota and private browsing can prevent persistence. No durability promise is made for blocked storage.

**Are historical Intent releases Sedrava releases?** No. Intent 0.7 and abandoned Sedrava 0.7.1 proposals are historical. Current candidate is Sedrava 0.9.0a1; no PyPI publication is authorized or performed.

**Как начать?** Выполните [Quick Start](QUICKSTART.md). Ошибка `rule` означает отказ от всего действия; некорректный ввод не меняет принятое состояние. Если сборка Android не находит компилятор, установите полный JDK, а не JRE. Если пропало состояние, проверьте `persist`, адрес Web-приложения или идентификатор Android-приложения.
