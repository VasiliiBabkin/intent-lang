"""Sedrava 0.9 Android backend using the shared AST and Gradle scaffold."""
import argparse
import ast
from pathlib import Path
from sedrava_core import parse, run, Assign, If
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
    return '"' + s.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n").replace("$", "\\$").replace("\r", "\\r").replace("\t", "\\t") + '"'

def generate(source, output):
    program = parse(source)
    run(program)
    if not program.widgets: raise ValueError("Missing screen main")
    user_names = {key: "sdr_" + key for key in (*program.states, *(program.derived or {}))}
    output = Path(output)
    # Reuse the compatible Gradle scaffold; language semantics use only the shared AST.
    scaffold('app "Scaffold"\nstate ready = false\naction start: ready = true\nscreen main:\n    text "Scaffold"\n    button "Start" -> start\n', output)
    target = output / "app/src/main/java/org/sedrava/generated/MainActivity.kt"
    lines = [
        "package org.sedrava.generated",
        "import android.os.Bundle",
        "import androidx.activity.ComponentActivity",
        "import androidx.activity.compose.setContent",
        "import androidx.compose.foundation.layout.*",
        "import androidx.compose.foundation.rememberScrollState",
        "import androidx.compose.foundation.verticalScroll",
        "import androidx.compose.material3.*",
        "import androidx.compose.runtime.*",
        "import androidx.compose.runtime.saveable.rememberSaveable",
        "import androidx.compose.ui.Modifier",
        "import androidx.compose.ui.unit.dp",
        "import androidx.compose.ui.platform.LocalContext",
        "import androidx.compose.foundation.text.KeyboardOptions",
        "import androidx.compose.ui.text.input.KeyboardType",
        "class MainActivity : ComponentActivity() {",
        "  override fun onCreate(savedInstanceState: Bundle?) {",
        "    super.onCreate(savedInstanceState)",
        "    setContent { MaterialTheme { SedravaScreen() } }",
        "  }",
        "}",
        "@Composable fun SedravaScreen() {",
    ]
    if program.persistent:
        lines.append("  val context = LocalContext.current")
        lines.append("  val prefs = remember { context.getSharedPreferences(\"sedrava_state\", android.content.Context.MODE_PRIVATE) }")
    names = {key: "next_" + key for key in program.states}
    for key, expr in (program.derived or {}).items():
        names[key] = "(" + kt(expr, names) + ")"
    params = ", ".join("next_" + key + ": " + ("Boolean" if type(val) is bool else "Int") for key, val in program.states.items())
    checks = ["    val checked_" + key + " = " + names[key] for key in (program.derived or {})]
    guard = " && ".join(kt(rule, names) for rule in program.rules) or "true"
    helper = ["internal fun checkDerivedState(" + params + ") {", *checks, "}", "internal fun validState(" + params + "): Boolean = try {", "    checkDerivedState(" + ", ".join("next_" + key for key in program.states) + ")", "    " + guard, "} catch (_: ArithmeticException) { false }"]
    lines[lines.index("class MainActivity : ComponentActivity() {"):lines.index("class MainActivity : ComponentActivity() {")] = helper
    for key, val in program.states.items():
        initial = str(val).lower()
        if key in program.persistent:
            method = "getBoolean" if type(val) is bool else "getInt"
            initial = f"try {{ prefs.{method}({quoted(key)}, {initial}) }} catch (_: ClassCastException) {{ {initial} }}"
        lines.append(f"  val restored_{key} = remember {{ {initial} }}")
    restored = ", ".join("restored_" + key for key in program.states)
    lines.append(f"  val restoredValid = remember {{ validState({restored}) }}")
    lines.append('  var actionError by remember { mutableStateOf("") }')
    for key, val in program.states.items():
        lines.append(f"  var {user_names[key]} by rememberSaveable {{ mutableStateOf(if (restoredValid) restored_{key} else {str(val).lower()}) }}")
    for key, expr in (program.derived or {}).items():
        display_names = {name: user_names[name] for name in program.states}
        display_names.update({name: user_names[name] for name in program.derived if name != key})
        lines.append(f"  val {user_names[key]} = {kt(expr, display_names)}")
    lines.append("  Column(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {")
    lines.append('    if (actionError.isNotEmpty()) Text(actionError, color = MaterialTheme.colorScheme.error)')
    names = {key:"next_"+key for key in program.states}
    for key, expr in (program.derived or {}).items():
        names[key] = "(" + kt(expr, names) + ")"
    def emit(stmts, pad):
        for stmt in stmts:
            if isinstance(stmt, Assign):
                lines.append(" "*pad + names[stmt.name] + " = " + kt(stmt.expr,names))
                lines.append(" "*pad + "checkDerivedState(" + ", ".join("next_" + key for key in program.states) + ")")
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
            lines.append(f"    Text({quoted(widget[1]+': ')} + {user_names[widget[1]]}.toString())")
        elif widget[0] == "input_int":
            key = widget[1]
            lines.append("    run {")
            lines.append(f"    var draft_{key} by remember {{ mutableStateOf({user_names[key]}.toString()) }}")
            lines.append(f"    LaunchedEffect({user_names[key]}) {{ draft_{key} = {user_names[key]}.toString() }}")
            lines.append(f'    val parsed_{key} = draft_{key}.trim().takeIf {{ it.matches(Regex("-?[0-9]+")) }}?.toIntOrNull()')
            lines.append(f"    val valid_{key} = parsed_{key} != null && run {{")
            for state_key in program.states:
                lines.append(f"      val next_{state_key} = " + (f"parsed_{key}!!" if state_key == key else user_names[state_key]))
            guard = "validState(" + ", ".join("next_" + key for key in program.states) + ")"
            lines.append(f"      {guard}")
            lines.append("    }")
            lines.append(f"    val error_{key} = draft_{key}.isNotEmpty() && !valid_{key}")
            lines.append(f"    OutlinedTextField(value = draft_{key}, onValueChange = {{ raw ->")
            lines.append(f"      draft_{key} = raw")
            lines.append('      val parsed = raw.trim().takeIf { it.matches(Regex("-?[0-9]+")) }?.toIntOrNull()')
            lines.append("      if (parsed != null) {")
            for state_key in program.states:
                lines.append(f"        val next_{state_key} = " + ("parsed" if state_key == key else user_names[state_key]))
            lines.append(f"        if ({guard}) {{")
            lines.append(f"          {user_names[key]} = parsed")
            if key in program.persistent:
                lines.append(f"          prefs.edit().putInt({quoted(key)}, parsed).apply()")
            lines.append("        }")
            lines.append("      }")
            lines.append(f"    }}, isError = error_{key}, supportingText = {{ if (error_{key}) Text(\"Value does not satisfy the declared rules\") }}, label = {{ Text({quoted(key)}) }}, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))")
            lines.append("    }")
        elif widget[0] == "show_text":
            lines.append(f"    if ({user_names[widget[1]]}) {{ Text({quoted(widget[2])}) }}")
        else:
            _, label, action = widget
            lines.append("    Button(onClick = {")
            lines.append("      try {")
            for key in program.states: lines.append(f"      var next_{key} = {user_names[key]}")
            emit(program.actions[action],6)
            guard = "validState(" + ", ".join("next_" + key for key in program.states) + ") && (" + (" && ".join(kt(rule,names) for rule in program.rules) or "true") + ")"
            lines.append("      if (" + guard + ") {")
            for key in program.states: lines.append(f"        {user_names[key]} = next_{key}")
            if program.persistent:
                lines.append("        prefs.edit().apply {")
                for key in program.persistent:
                    method = "putBoolean" if type(program.states[key]) is bool else "putInt"
                    lines.append(f"          {method}({quoted(key)}, next_{key})")
                lines.append("        }.apply()")
            lines.append('        actionError = ""')
            lines.append('      } else { actionError = "Action rejected by declared rules" }')
            lines.append('      } catch (_: ArithmeticException) { actionError = "Action rejected: integer overflow" }')
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
