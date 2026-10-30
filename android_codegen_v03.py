"""Sedrava Android backend: shared typed state semantics and Compose adapters."""
import argparse
import ast
from pathlib import Path
from sedrava_records import ListValue
from sedrava_records_codegen import kt_support, kt_persistence
from sedrava_core import parse, run, Assign, If, Require
from android_codegen import generate as scaffold

def kt(node, names):
    if isinstance(node, ast.Attribute): return '(' + kt(node.value, names) + ').sdr_' + node.attr
    if isinstance(node, ast.Call):
        if hasattr(node, 'record_type'): return 'SdrRecord_' + node.record_type.name + '(' + ','.join('sdr_'+k.arg+'='+kt(k.value,names) for k in node.keywords) + ')'
        return 'sdr_'+node.func.id+'('+','.join(kt(a,names) for a in node.args)+')'
    if isinstance(node, ast.Constant):
        if type(node.value) is str: return quoted(node.value)
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

def quoted(value):
    escapes = {"\\": "\\\\", '"': '\\"', "$": "\\$", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return '"' + "".join(escapes.get(char, "\\u%04x" % ord(char) if ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF or ord(char) in (0x2028, 0x2029) else char) for char in value) + '"'


def kind(value):
    if isinstance(value, ListValue): return 'SdrList<SdrRecord_' + value.kind.record.name + '>'
    return {int:'Int',bool:'Boolean',str:'String'}[type(value)]


def literal(value):
    if isinstance(value, ListValue): return 'SdrList<SdrRecord_' + value.kind.record.name + '>(capacity=' + str(value.kind.capacity) + ')'
    return quoted(value) if type(value) is str else str(value).lower()


def generate(source, output, _program=None):
    program = _program or parse(source)
    if program.has_navigation and _program is None:
        from sedrava_navigation_android import generate_navigation
        return generate_navigation(source, output, program)
    run(program)
    if not program.widgets:
        raise ValueError("Missing screen main")
    output = Path(output)
    scaffold('app "Scaffold"\nstate ready = false\naction start: ready = true\nscreen main:\n    text "Scaffold"\n    button "Start" -> start\n', output)
    target = output / "app/src/main/java/org/sedrava/generated/MainActivity.kt"
    # One pure state adapter supplies both Compose callbacks and JVM conformance.
    kinds = {int: "Int", bool: "Boolean", str: "String"}
    keys = list(program.states)
    user = {key: "sdr_" + key for key in (*keys, *(program.derived or {}))}
    next_names = {key: "next_" + key for key in keys}
    for key, expr in (program.derived or {}).items():
        next_names[key] = "(" + kt(expr, next_names) + ")"
    params = ", ".join("next_" + key + ": " + kind(val) for key, val in program.states.items())
    next_args = ", ".join("next_" + key for key in keys)
    user_args = ", ".join(user[key] for key in keys)
    def state_args(prefix):
        return ", ".join(prefix + "." + user[key] for key in keys)
    guard = " && ".join(kt(rule, next_names) for rule in program.rules) or "true"
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
        "internal fun validText(value: String): Boolean {",
        "  var i = 0; var count = 0",
        "  while (i < value.length) {",
        "    val cp = Character.codePointAt(value, i)",
        "    if (cp in 0xD800..0xDFFF || ++count > 1024) return false",
        "    i += Character.charCount(cp)",
        "  }",
        "  return true",
        "}",
        'internal fun checkedText(value: String): String { require(validText(value)) { "Invalid text value" }; return value }',
        *(kt_support(program, quoted) if (program.records or program.has_navigation) else []),
        "internal " + ("data " if keys else "") + "class SedravaState(" + ", ".join("val " + user[key] + ": " + kind(val) + " = " + literal(val) for key, val in program.states.items()) + ")",
        "internal fun checkDerivedState(" + params + ") {",
    ]
    for key, val in program.states.items():
        if type(val) is str:
            lines.append("  checkedText(next_" + key + ")")
        elif isinstance(val, ListValue):
            lines.append("  next_" + key + ".check(); require(next_" + key + ".capacity == " + str(val.kind.capacity) + ")")
    for key in (program.derived or {}):
        lines.append("  val checked_" + key + " = " + next_names[key])
    lines += ["}", "internal fun validState(" + params + "): Boolean = try {", "  checkDerivedState(" + next_args + ")", ("  snapshotState(SedravaState(" + next_args + "), true); " if (program.records or program.has_navigation) else "  ") + guard,
              "} catch (_: ArithmeticException) { false } catch (_: IllegalArgumentException) { false }",
              "internal fun restoreState(saved: Map<String, *>): SedravaState {"]
    if (program.records or program.has_navigation):
        lines += ['  return try { val raw=saved["snapshot"]; if(raw is String) restoreSnapshot(raw) else SedravaState() } catch (_: IllegalArgumentException) { SedravaState() }', '}',
                  'internal fun editState(state: SedravaState, key: String, value: Any?): SedravaState {', '  val next = when(key) {']
    else:
        for key, val in program.states.items():
            if key in program.persistent:
                lines.append("  val saved_" + key + " = saved[" + quoted(key) + "]")
                condition = "saved_" + key + " is " + kind(val)
                if type(val) is str:
                    condition += " && validText(saved_" + key + ")"
                lines.append("  val next_" + key + " = if (" + condition + ") saved_" + key + " else " + literal(val))
            else:
                lines.append("  val next_" + key + " = " + literal(val))
        lines += ["  return if (validState(" + next_args + ")) SedravaState(" + next_args + ") else SedravaState()", "}",
                  "internal fun editState(state: SedravaState, key: String, value: Any?): SedravaState {", "  val next = when (key) {"]
    for key, val in program.states.items():
        if isinstance(val, ListValue): continue
        lines.append("    " + quoted(key) + " -> if (value is " + kind(val) + ") state.copy(" + user[key] + " = value) else return state")
    lines += ["    else -> return state", "  }", "  return if (validState(" + state_args("next") + ")) next else state", "}",
              "internal fun transitionState(state: SedravaState, action: String): SedravaState {",
              "  if (!validState(" + state_args("state") + ")) return state"]
    for key in keys:
        lines.append("  var next_" + key + " = state." + user[key])
    lines += ["  return try {", "    when (action) {"]
    def emit(body, depth):
        for stmt in body:
            if isinstance(stmt, Require):
                lines.append(' ' * depth + 'require(' + kt(stmt.condition, next_names) + ')')
            elif isinstance(stmt, Assign):
                lines.append(" " * depth + next_names[stmt.name] + " = " + kt(stmt.expr, next_names))
                lines.append(" " * depth + "checkDerivedState(" + next_args + ")")
            else:
                lines.append(" " * depth + "if (" + kt(stmt.condition, next_names) + ") {")
                emit(stmt.yes, depth + 2)
                if stmt.no:
                    lines.append(" " * depth + "} else {")
                    emit(stmt.no, depth + 2)
                lines.append(" " * depth + "}")
    for key, body in program.actions.items():
        lines.append("      " + quoted(key) + " -> {")
        emit(body, 8)
        lines.append("      }")
    lines += ["      else -> return state", "    }", "    if (validState(" + next_args + ")) SedravaState(" + next_args + ") else state",
              "  } catch (_: ArithmeticException) { state } catch (_: IllegalArgumentException) { state }", "}"]
    if (program.records or program.has_navigation):
        lines += kt_persistence(program, quoted, literal)
    if (program.records or program.has_navigation) and program.persistent:
        lines += ['private fun persistState(prefs: android.content.SharedPreferences, state: SedravaState): Boolean = try {',
                  '  prefs.edit().putString("snapshot", snapshotState(state)).commit()',
                  '} catch (_: Exception) { false }']
    else:
        if program.persistent:
            lines += ["private fun persistState(prefs: android.content.SharedPreferences, state: SedravaState) {", "  prefs.edit().apply {"]
            if (program.records or program.has_navigation):
                lines.append('    putString("snapshot", snapshotState(state))')
            for key in (() if (program.records or program.has_navigation) else program.persistent):
                method = {int: "putInt", bool: "putBoolean", str: "putString"}[type(program.states[key])]
                lines.append("    " + method + "(" + quoted(key) + ", state." + user[key] + ")")
            lines += ["  }.apply()", "}"]
    lines += ["class MainActivity : ComponentActivity() {", "  override fun onCreate(savedInstanceState: Bundle?) {", "    super.onCreate(savedInstanceState)",
              "    setContent { MaterialTheme { SedravaScreen() } }", "  }", "}", "@Composable fun SedravaScreen() {"]
    if program.persistent:
        lines += ["  val context = LocalContext.current", '  val prefs = remember { context.getSharedPreferences("sedrava_state", android.content.Context.MODE_PRIVATE) }',
                  "  val restoredState = remember { restoreState(prefs.all) }"]
    else:
        lines.append("  val restoredState = remember { SedravaState() }")
    if (program.records or program.has_navigation):
        lines += ['  var savedSnapshot by rememberSaveable { mutableStateOf(snapshotState(restoredState, true)) }',
                  '  val recreatedState = remember { try { restoreSnapshot(savedSnapshot, true) } catch (_: IllegalArgumentException) { restoredState } }']
    for key in keys:
        if (program.records or program.has_navigation):
            lines.append("  var " + user[key] + " by remember { mutableStateOf(recreatedState." + user[key] + ") }")
            continue
        lines.append("  var " + user[key] + " by rememberSaveable { mutableStateOf(restoredState." + user[key] + ") }")
    if (program.records or program.has_navigation) and program.persistent:
        lines.append('  var actionError by remember { mutableStateOf(if (prefs.contains("snapshot") && !snapshotValid(prefs.all["snapshot"])) "Saved data rejected; defaults restored" else "") }')
    else:
        lines.append('  var actionError by remember { mutableStateOf("") }')
    for key, expr in (program.derived or {}).items():
        lines.append("  val " + user[key] + " = " + kt(expr, user))
    lines += ["  Column(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {",
              '    if (actionError.isNotEmpty()) Text(actionError, color = MaterialTheme.colorScheme.error)']
    for widget in program.widgets:
        if widget[0] == "list":
            key, selected = widget[1:]
            lines += ["    for (row in " + user[key] + ".items) {", "      key(row.id) {", '        Text(row.record.fields().entries.joinToString(" · ") { it.key + ": " + it.value.toString() })', '        Button(onClick = {', "          val current=SedravaState(" + user_args + ")", '          val next=editState(current,' + quoted(selected) + ',row.id)', '          if(next !== current) {', '            ' + user[selected] + ' = next.' + user[selected], '            savedSnapshot = snapshotState(next, true)']
            if program.persistent: lines.append('            if (!persistState(prefs,next)) actionError = "Could not save state"')
            lines += ['          } else { actionError = "Selection rejected" }', '        }) { Text("Select / Выбрать") }', '      }', '    }']
        elif widget[0] == "text":
            lines.append("    Text(" + quoted(widget[1]) + ", style = MaterialTheme.typography.headlineMedium)")
        elif widget[0] == "value":
            lines.append("    Text(" + quoted(widget[1] + ": ") + " + " + user[widget[1]] + ".toString())")
        elif widget[0] in ("input_int", "input_text"):
            key = widget[1]
            text = widget[0] == "input_text"
            parse_draft = "draft_" + key if text else 'draft_' + key + '.trim().takeIf { it.matches(Regex("-?[0-9]+")) }?.toIntOrNull()'
            parse_raw = "raw" if text else 'raw.trim().takeIf { it.matches(Regex("-?[0-9]+")) }?.toIntOrNull()'
            lines += ["    run {", "      val current = SedravaState(" + user_args + ")",
                      "      var draft_" + key + " by remember { mutableStateOf(" + user[key] + ".toString()) }",
                      "      LaunchedEffect(" + user[key] + ") { draft_" + key + " = " + user[key] + ".toString() }",
                      "      val parsed_" + key + " = " + parse_draft,
                      "      val valid_" + key + " = editState(current, " + quoted(key) + ", parsed_" + key + ") !== current",
                      "      val error_" + key + " = " + ("" if text else "draft_" + key + ".isNotEmpty() && ") + "!valid_" + key,
                      "      OutlinedTextField(value = draft_" + key + ", onValueChange = { raw ->",
                      "        draft_" + key + " = raw", "        val next = editState(current, " + quoted(key) + ", " + parse_raw + ")",
                      "        if (next !== current) {", "          " + user[key] + " = next." + user[key]]
            if (program.records or program.has_navigation):
                lines.append("          savedSnapshot = snapshotState(next, true)")
            if program.persistent:
                lines.append('          if (!persistState(prefs,next)) actionError = "Could not save state"' if (program.records or program.has_navigation) else "          persistState(prefs, next)")
            message = "Text must contain at most 1024 Unicode scalar values and satisfy the declared rules" if text else "Value does not satisfy the declared rules"
            lines += ["        }", "      }, isError = error_" + key + ", supportingText = { if (error_" + key + ") Text(" + quoted(message) + ") }, label = { Text(" + quoted(key) + ") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType." + ("Text" if text else "Number") + "))", "    }"]
        elif widget[0] == "show_text":
            lines.append("    if (" + user[widget[1]] + ") { Text(" + quoted(widget[2]) + ") }")
        else:
            _, label, action = widget
            lines += ["    Button(onClick = {", "      val current = SedravaState(" + user_args + ")", "      val next = transitionState(current, " + quoted(action) + ")",
                      "      if (next !== current) {"]
            for key in keys:
                lines.append("        " + user[key] + " = next." + user[key])
            if (program.records or program.has_navigation):
                lines.append("        savedSnapshot = snapshotState(next, true)")
            if program.persistent:
                lines.append('        actionError = if (persistState(prefs,next)) "" else "Could not save state"' if (program.records or program.has_navigation) else "        persistState(prefs, next)")
            lines += [('' if (program.records or program.has_navigation) and program.persistent else '        actionError = ""'), '      } else { actionError = "Action rejected: constraints or arithmetic/value error" }', "    }) { Text(" + quoted(label) + ") }"]
    lines += ["  }", "}"]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("source")
    cli.add_argument("--output",default="build/generated-android")
    args = cli.parse_args()
    print(generate(Path(args.source).read_text(encoding="utf-8"),args.output))
