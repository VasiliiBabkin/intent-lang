"""Intent 0.3 Android backend: compile shared AST, reuse v0.2 Gradle scaffold."""
import argparse
import ast
from pathlib import Path
from intent_core import parse, run, Assign, If
from android_codegen import generate as scaffold

def kt(node, names):
    if isinstance(node, ast.Constant):
        return str(node.value).lower() if type(node.value) is bool else str(node.value)
    if isinstance(node, ast.Name): return names[node.id]
    if isinstance(node, ast.UnaryOp):
        return ("!(" + kt(node.operand, names) + ")" if isinstance(node.op, ast.Not) else "Math.negateExact(" + kt(node.operand, names) + ")")
    if isinstance(node, ast.BinOp):
        return f"Math.{ {ast.Add: 'addExact', ast.Sub: 'subtractExact', ast.Mult: 'multiplyExact'}[type(node.op)] }({kt(node.left,names)}, {kt(node.right,names)})"
    if isinstance(node, ast.BoolOp):
        op = " && " if isinstance(node.op, ast.And) else " || "
        return "(" + op.join(kt(v,names) for v in node.values) + ")"
    if isinstance(node, ast.Compare):
        op = {ast.Eq:"==", ast.NotEq:"!=", ast.Gt:">", ast.GtE:">=", ast.Lt:"<", ast.LtE:"<="}[type(node.ops[0])]
        return f"({kt(node.left,names)} {op} {kt(node.comparators[0],names)})"
    raise ValueError("Unsupported AST")

def quoted(s):
    return '"' + s.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n") + '"'

def generate(source, output):
    program = parse(source)
    run(program)
    if not program.widgets: raise ValueError("Missing screen main")
    output = Path(output)
    # Temporary scaffolding reuse; semantics below depend solely on Intent AST.
    scaffold('app "Scaffold"\nstate ready = false\naction start: ready = true\nscreen main:\n    text "Scaffold"\n    button "Start" -> start\n', output)
    target = output / "app/src/main/java/org/intentlang/generated/MainActivity.kt"
    lines = [
        "package org.intentlang.generated",
        "import android.os.Bundle",
        "import androidx.activity.ComponentActivity",
        "import androidx.activity.compose.setContent",
        "import androidx.compose.foundation.layout.*",
        "import androidx.compose.material3.*",
        "import androidx.compose.runtime.*",
        "import androidx.compose.ui.Modifier",
        "import androidx.compose.ui.unit.dp",
        "import androidx.compose.ui.platform.LocalContext",
        "import androidx.compose.foundation.text.KeyboardOptions",
        "import androidx.compose.ui.text.input.KeyboardType",
        "class MainActivity : ComponentActivity() {",
        "  override fun onCreate(savedInstanceState: Bundle?) {",
        "    super.onCreate(savedInstanceState)",
        "    setContent { MaterialTheme { IntentScreen() } }",
        "  }",
        "}",
        "@Composable fun IntentScreen() {",
    ]
    if program.persistent:
        lines.append("  val context = LocalContext.current")
        lines.append("  val prefs = remember { context.getSharedPreferences(\"intent_state\", android.content.Context.MODE_PRIVATE) }")
    for key, val in program.states.items():
        initial = str(val).lower()
        if key in program.persistent:
            method = "getBoolean" if type(val) is bool else "getInt"
            initial = f"prefs.{method}({quoted(key)}, {initial})"
        lines.append(f"  var {key} by remember {{ mutableStateOf({initial}) }}")
    for key, expr in (program.derived or {}).items():
        display_names = {name: name for name in program.states}
        display_names.update({name: name for name in program.derived if name != key})
        lines.append(f"  val {key} = {kt(expr, display_names)}")
    lines.append("  Column(modifier = Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {")
    names = {key:"next_"+key for key in program.states}
    for key, expr in (program.derived or {}).items():
        names[key] = "(" + kt(expr, names) + ")"
    def emit(stmts, pad):
        for stmt in stmts:
            if isinstance(stmt, Assign):
                lines.append(" "*pad + names[stmt.name] + " = " + kt(stmt.expr,names))
            elif isinstance(stmt, If):
                lines.append(" "*pad + "if (" + kt(stmt.condition,names) + ") {")
                emit(stmt.yes,pad+2)
                if stmt.no:
                    lines.append(" "*pad + "} else {")
                    emit(stmt.no,pad+2)
                lines.append(" "*pad + "}")
    for widget in program.widgets:
        if widget[0] == "text":
            lines.append(f"    Text({quoted(widget[1])}, style = MaterialTheme.typography.headlineMedium)")
        elif widget[0] == "value":
            lines.append(f"    Text({quoted(widget[1]+': ')} + {widget[1]}.toString())")
        elif widget[0] == "input_int":
            key = widget[1]
            lines.append(f"    OutlinedTextField(value = {key}.toString(), onValueChange = {{ raw ->")
            lines.append("      val parsed = raw.toIntOrNull()")
            lines.append("      if (parsed != null) {")
            for state_key in program.states:
                lines.append(f"        val next_{state_key} = " + ("parsed" if state_key == key else state_key))
            guard = " && ".join(kt(rule, names) for rule in program.rules) or "true"
            lines.append(f"        if ({guard}) {{")
            lines.append(f"          {key} = parsed")
            if key in program.persistent:
                lines.append(f"          prefs.edit().putInt({quoted(key)}, parsed).apply()")
            lines.append("        }")
            lines.append("      }")
            lines.append(f"    }}, label = {{ Text({quoted(key)}) }}, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))")
        elif widget[0] == "show_text":
            lines.append(f"    if ({widget[1]}) {{ Text({quoted(widget[2])}) }}")
        else:
            _, label, action = widget
            lines.append("    Button(onClick = {")
            for key in program.states: lines.append(f"      var next_{key} = {key}")
            emit(program.actions[action],6)
            guard = " && ".join(kt(rule,names) for rule in program.rules) or "true"
            lines.append("      if (" + guard + ") {")
            for key in program.states: lines.append(f"        {key} = next_{key}")
            if program.persistent:
                lines.append("        prefs.edit().apply {")
                for key in program.persistent:
                    method = "putBoolean" if type(program.states[key]) is bool else "putInt"
                    lines.append(f"          {method}({quoted(key)}, next_{key})")
                lines.append("        }.apply()")
            lines.append("      }")
            lines.append(f"    }}) {{ Text({quoted(label)}) }}")
    lines += ["  }","}"]
    target.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return target

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("source")
    cli.add_argument("--output",default="build/generated-android")
    args = cli.parse_args()
    print(generate(Path(args.source).read_text(encoding="utf-8"),args.output))
