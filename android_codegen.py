"""Deterministic Sedrava -> Android Jetpack Compose project generator."""
from sedrava_version import VERSION, ANDROID_VERSION_CODE
from pathlib import Path
import argparse
import re
from sedrava_android_identity import application_id as resolve_id, prepare_identity, kotlin_path, write_title
from sedrava import parse, run

IDENT = r"[A-Za-z_][A-Za-z_0-9]*"

def kotlin_string(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

def kotlin_expression(source, states):
    """Compile the same restricted expression subset to Kotlin."""
    import ast
    def walk(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return str(node.value)
        if isinstance(node, ast.Constant) and type(node.value) is bool:
            return str(node.value).lower()
        if isinstance(node, ast.Name):
            if node.id in ("true", "false"):
                return node.id
            if node.id not in states:
                raise ValueError(f"Unknown state: {node.id}")
            return node.id
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return "(-" + walk(node.operand) + ")"
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*"}[type(node.op)]
            return "(" + walk(node.left) + " " + op + " " + walk(node.right) + ")"
        raise ValueError(f"Unsupported Kotlin expression: {source}")
    return walk(ast.parse(source, mode="eval").body)

def ui_parse(source, program):
    screen = False
    widgets = []
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if line.startswith("screen "):
            if line != "screen main:" or screen:
                raise ValueError(f"Line {number}: only one 'screen main:' supported")
            screen = True
            continue
        if not screen or not line or line.startswith("#"):
            continue
        if m := re.fullmatch(r'text "([^"]*)"', line):
            widgets.append(("text", m[1]))
        elif m := re.fullmatch(rf"value ({IDENT})", line):
            if m[1] not in program.states:
                raise ValueError(f"Line {number}: unknown state {m[1]}")
            widgets.append(("value", m[1]))
        elif m := re.fullmatch(rf'button "([^"]*)" -> ({IDENT})', line):
            if m[2] not in program.actions:
                raise ValueError(f"Line {number}: unknown action {m[2]}")
            widgets.append(("button", m[1], m[2]))
        else:
            raise ValueError(f"Line {number}: invalid UI syntax: {line}")
    if not screen:
        raise ValueError("Missing screen main:")
    return widgets

def generate(source, output, application_id=None):
    program = parse('\n'.join(line for line in source.splitlines() if not line.strip().startswith("screen ") and not line.startswith("    ")))
    run(program)
    widgets = ui_parse(source, program)
    output = Path(output)
    package = resolve_id(program.name, application_id)
    prepare_identity(output, package, program.name)
    lines = [
        f"package {package}",
        "",
        "import android.os.Bundle",
        "import androidx.activity.ComponentActivity",
        "import androidx.activity.compose.setContent",
        "import androidx.compose.foundation.layout.*",
        "import androidx.compose.material3.*",
        "import androidx.compose.runtime.*",
        "import androidx.compose.ui.Modifier",
        "import androidx.compose.ui.unit.dp",
        "",
        "class MainActivity : ComponentActivity() {",
        "  override fun onCreate(savedInstanceState: Bundle?) {",
        "    super.onCreate(savedInstanceState)",
        "    setContent { MaterialTheme { SedravaScreen() } }",
        "  }",
        "}",
        "",
        "@Composable",
        "fun SedravaScreen() {",
    ]
    for key, val in program.states.items():
        literal = str(val).lower() if isinstance(val, bool) else str(val)
        lines.append(f"  var {key} by remember {{ mutableStateOf({literal}) }}")
    lines += ["  Column(modifier = Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {"]
    for widget in widgets:
        if widget[0] == "text":
            lines.append(f"    Text({kotlin_string(widget[1])}, style = MaterialTheme.typography.headlineMedium)")
        elif widget[0] == "value":
            lines.append(f'    Text({kotlin_string(widget[1] + ": ")} + {widget[1]}.toString())')
        else:
            _, label, action = widget
            target, val = program.actions[action]
            literal = str(val).lower() if isinstance(val, bool) else str(val)
            # Invariants are enforced for every UI action, not merely checked in tests.
            candidate = {key: (literal if key == target else key) for key in program.states}
            conditions = []
            for rule in program.rules:
                m = re.fullmatch(rf"({IDENT})\s*(==|>=|<=|>|<|!=)\s*(-?\d+|true|false)", rule.strip())
                if not m:
                    raise ValueError(f"Unsupported rule: {rule}")
                name, op, expected = m.groups()
                conditions.append(f"({candidate[name]} {op} {expected})")
            guard = " && ".join(conditions) if conditions else "true"
            lines.append(f"    Button(onClick = {{ if ({guard}) {target} = {literal} }}) {{ Text({kotlin_string(label)}) }}")
    lines += ["  }", "}"]
    target = kotlin_path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = output / "app/src/main/AndroidManifest.xml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:label="@string/sedrava_app_name" android:theme="@android:style/Theme.Material.Light.NoActionBar"><activity android:name=".MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity></application></manifest>\n', encoding="utf-8")
    write_title(output, program.name)
    (output / "settings.gradle.kts").write_text('pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\ndependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\nrootProject.name = "SedravaApp"\ninclude(":app")\n', encoding="utf-8")
    (output / "build.gradle.kts").write_text('plugins { id("com.android.application") version "8.9.2" apply false; id("org.jetbrains.kotlin.android") version "2.0.21" apply false; id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false }\n', encoding="utf-8")
    (output / "gradle.properties").write_text('org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\nandroid.useAndroidX=true\n', encoding="utf-8")
    (output / "app/build.gradle.kts").write_text('plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("org.jetbrains.kotlin.plugin.compose") }\nandroid { namespace = "PACKAGE_PLACEHOLDER"; compileSdk = 35\n defaultConfig { applicationId = "PACKAGE_PLACEHOLDER"; minSdk = 26; targetSdk = 35; versionCode = CODE_PLACEHOLDER; versionName = "VERSION_PLACEHOLDER" }\n buildFeatures { compose = true }\n compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }\n kotlinOptions { jvmTarget = "17" }\n}\ndependencies { implementation(platform("androidx.compose:compose-bom:2024.12.01")); implementation("androidx.activity:activity-compose:1.9.3"); implementation("androidx.compose.material3:material3"); implementation("androidx.compose.ui:ui"); testImplementation("junit:junit:4.13.2") }\n', encoding="utf-8")
    gradle = output / "app/build.gradle.kts"
    gradle.write_text(gradle.read_text(encoding="utf-8").replace("PACKAGE_PLACEHOLDER", package).replace("CODE_PLACEHOLDER", str(ANDROID_VERSION_CODE)).replace("VERSION_PLACEHOLDER", VERSION), encoding="utf-8")
    return target

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output", default="build/generated-android")
    args = parser.parse_args()
    print(generate(Path(args.source).read_text(encoding="utf-8"), args.output))
