"""Sedrava web backend: generate self-contained HTML + JS from the shared AST."""
import argparse
import ast
import html
import json
from pathlib import Path
from sedrava_records import plain
from sedrava_records_codegen import js_runtime
from sedrava_core import Assign, If, Require, parse, run

def json_script(value, **kwargs):
    # HTML parses script end tags before JavaScript parses quoted strings.
    return json.dumps(value, **kwargs).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

def js_expr(node, names):
    if isinstance(node, ast.Attribute): return '(' + js_expr(node.value, names) + ')[' + json_script(node.attr) + ']'
    if isinstance(node, ast.Call):
        if hasattr(node, 'record_type'):
            fields = {k.arg: k.value for k in node.keywords}
            return '({' + ','.join('[' + json_script(k) + ']:' + js_expr(fields[k], names) for k, _ in node.record_type.fields) + '})'
        return 'collectionOp(' + json_script(node.func.id) + ',' + str(node.collection_type.capacity) + ',' + ','.join(js_expr(a, names) for a in node.args) + ')'
    if isinstance(node, ast.Constant):
        return json_script(node.value)
    if isinstance(node, ast.Name):
        return names[node.id]
    if isinstance(node, ast.UnaryOp):
        operator = "!" if isinstance(node.op, ast.Not) else "-"
        return (f"checkedInt(-({js_expr(node.operand, names)}))" if isinstance(node.op, ast.USub) else f"(!{js_expr(node.operand, names)})")
    if isinstance(node, ast.BinOp):
        op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*"}[type(node.op)]
        return f"checkedInt({js_expr(node.left, names)} {op} {js_expr(node.right, names)})"
    if isinstance(node, ast.BoolOp):
        op = " && " if isinstance(node.op, ast.And) else " || "
        return "(" + op.join(js_expr(v, names) for v in node.values) + ")"
    if isinstance(node, ast.Compare):
        op = {ast.Eq: "===", ast.NotEq: "!==", ast.Lt: "<", ast.LtE: "<=",
              ast.Gt: ">", ast.GtE: ">="}[type(node.ops[0])]
        return f"({js_expr(node.left, names)} {op} {js_expr(node.comparators[0], names)})"
    raise ValueError("Unsupported expression")

def statements(body, names, depth=4):
    result = []
    pad = " " * depth
    for stmt in body:
        if isinstance(stmt, Require):
            result.append(pad + 'if (!(' + js_expr(stmt.condition, names) + ")) throw Error('Action requirement rejected');")
        elif isinstance(stmt, Assign):
            result.append(f"{pad}{names[stmt.name]} = {js_expr(stmt.expr, names)};")
            result.append(f"{pad}checkDerivedState(nextState);")
        elif isinstance(stmt, If):
            result.append(f"{pad}if ({js_expr(stmt.condition, names)}) {{")
            result.extend(statements(stmt.yes, names, depth + 2))
            if stmt.no:
                result.append(f"{pad}}} else {{")
                result.extend(statements(stmt.no, names, depth + 2))
            result.append(f"{pad}}}")
        else:
            raise ValueError("Unsupported statement")
    return result

def generate(source, _program=None):
    program = _program or parse(source)
    if program.has_navigation and _program is None:
        from sedrava_navigation_web import generate_navigation
        return generate_navigation(source, program)
    run(program)
    if not program.widgets:
        raise ValueError("Missing screen main")
    initial = json_script({k: plain(v) for k, v in program.states.items()}, ensure_ascii=False)
    names = {key: "nextState[" + json_script(key) + "]" for key in program.states}
    for key, expr in (program.derived or {}).items():
        names[key] = js_expr(expr, names)
    rules = " && ".join(js_expr(rule, names) for rule in program.rules) or "true"
    actions = []
    for name, body in program.actions.items():
        actions.extend([
            f"  [{json_script(name)}]: (state) => {{",
            "    const nextState = { ...state };",
            *statements(body, names),
            f"    return validateState(nextState) && ({rules}) ? nextState : state;",
            "  },",
        ])
    render_names = {key: "derivedState[" + json_script(key) + "]" for key in program.states}
    derived_lines = []
    for key, expr in (program.derived or {}).items():
        derived_lines.append("  derivedState[" + json_script(key) + "] = " + js_expr(expr, render_names) + ";")
        render_names[key] = "derivedState[" + json_script(key) + "]"
    widgets = []
    for widget in program.widgets:
        if widget[0] == "list":
            widgets.append('<ul data-list="' + html.escape(widget[1], quote=True) + '" data-select="' + html.escape(widget[2], quote=True) + '"></ul>')
        elif widget[0] == "text":
            widgets.append(f'<h1>{html.escape(widget[1])}</h1>')
        elif widget[0] == "value":
            key = html.escape(widget[1], quote=True)
            widgets.append(f'<p>{key}: <output data-state="{key}"></output></p>')
        elif widget[0] == "input_text":
            key = html.escape(widget[1], quote=True)
            widgets.append(f'<label>{key}: <textarea data-input="{key}" aria-describedby="error-{key}" aria-invalid="false"></textarea></label><small id="error-{key}" role="alert" hidden>Text must contain at most 1024 Unicode scalar values and satisfy the declared rules</small>')
        elif widget[0] == "input_int":
            key = html.escape(widget[1], quote=True)
            widgets.append(f'<label>{key}: <input type="number" step="1" min="-2147483648" max="2147483647" data-input="{key}" aria-describedby="error-{key}"></label><small id="error-{key}" role="alert" hidden>Value does not satisfy the declared rules</small>')
        elif widget[0] == "show_text":
            key = html.escape(widget[1], quote=True)
            widgets.append(f'<p data-show="{key}" hidden>{html.escape(widget[2])}</p>')
        else:
            label, action = widget[1:]
            widgets.append(f'<button type="button" data-action="{html.escape(action, quote=True)}">{html.escape(label)}</button>')
    # No user-supplied text is inserted into executable JS without JSON encoding.
    return "\n".join([
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html.escape(program.name)}</title>",
        '<style>body{font:18px system-ui;max-width:38rem;margin:3rem auto;padding:0 1rem}button{padding:.7rem 1rem;margin:.25rem;border-radius:.5rem;cursor:pointer}output,h1,[data-show]{white-space:pre-wrap;overflow-wrap:anywhere}textarea{display:block;max-width:100%;width:100%;min-height:5rem}input[aria-invalid="true"],textarea[aria-invalid="true"]{outline:2px solid #b42318}small[role="alert"]{display:block;color:#b42318}small[hidden]{display:none}</style>',
        "</head><body>",
        *widgets,
        '<p id="sedrava-error" role="alert" hidden></p>',
        "<script>",
        f"const initialState = JSON.parse({json_script(initial)});",
        "const storageKey = 'sedrava:' + (typeof location !== 'undefined' ? location.pathname : '/') + ':' + " + json_script(program.name) + ";",
        "const persistentKeys = " + json_script(list(program.persistent)) + ";",
        js_runtime(program, json_script) if (program.records or program.has_navigation) else "const collectionTypes = {};",
        "let restoreError = false;",
        "let state = { ...initialState };",
        ("try { const raw = localStorage.getItem(storageKey); if (raw !== null) state = restoreSnapshot(raw); } catch (_) { restoreError = true; }" if (program.records or program.has_navigation) else "try { const saved = JSON.parse((typeof localStorage !== 'undefined' ? localStorage.getItem(storageKey) : null) || '{}'); state = restoreState(saved); } catch (_) { /* unavailable or corrupt storage */ }"),
        "function checkedInt(n) { if (!Number.isInteger(n) || n < -2147483648 || n > 2147483647) throw new RangeError('Sedrava integer overflow'); return n; }",
        "function validText(value) { if (typeof value !== 'string') return false; let count = 0; for (const char of value) { const cp = char.codePointAt(0); if ((cp >= 0xD800 && cp <= 0xDFFF) || ++count > 1024) return false; } return true; }",
        "function validValue(value, initial) { return typeof value === typeof initial && (typeof value === 'string' ? validText(value) : typeof value === 'number' ? Number.isInteger(value) && value >= -2147483648 && value <= 2147483647 : typeof value === 'boolean'); }",
        "function checkResources(nextState) { if (JSON.stringify({schema:1,signature,state:nextState}).length > 200000) throw Error('State exceeds resource limit'); }" if (program.records or program.has_navigation) else "function checkResources(_) {}",
        "function checkStateValues(nextState) { if (Object.keys(nextState).length !== Object.keys(initialState).length) throw Error('Invalid keys'); for (const key of Object.keys(initialState)) { if (!Object.hasOwn(nextState, key) || !(Object.hasOwn(collectionTypes, key) ? validCollection(nextState[key], collectionTypes[key]) : validValue(nextState[key], initialState[key]))) throw new RangeError('Invalid Sedrava value'); } }",
        "function restoreState(saved) { try { return restoreSnapshot(saved); } catch (_) { return { ...initialState }; } }" if (program.records or program.has_navigation) else "function restoreState(saved) { const restored = { ...initialState }; if (saved && typeof saved === 'object' && !Array.isArray(saved)) { for (const key of persistentKeys) { if (Object.hasOwn(saved, key) && validValue(saved[key], initialState[key])) restored[key] = saved[key]; } } return validateState(restored) ? restored : { ...initialState }; }",
        "function editState(current, key, value) { if (!Object.hasOwn(initialState, key)) return current; const next = { ...current, [key]: value }; return validateState(next) ? next : current; }",
        "const actions = {",
        *actions,
        "};",
        "function checkDerivedState(nextState) { checkStateValues(nextState); const derivedState = { __proto__: null, ...nextState };",
        *derived_lines,
        "}",
        "function validateState(nextState) {",
        "  try { checkResources(nextState); checkStateValues(nextState); const derivedState = { __proto__: null, ...nextState };",
        *derived_lines,
        "    return " + rules + "; } catch (_) { return false; }",
        "}",
        "if (!validateState(state)) state = { ...initialState };",
        "function showError(message) { const el = document.getElementById('sedrava-error'); if (el) { el.textContent = message; el.hidden = !message; } }",
        "function render(resetInputs = false) {",
        "  const derivedState = { __proto__: null, ...state };",
        *derived_lines,
        '  document.querySelectorAll("[data-state]").forEach(el => { el.textContent = String(derivedState[el.dataset.state]); });',
        '  document.querySelectorAll("[data-show]").forEach(el => { el.hidden = !derivedState[el.dataset.show]; });',
        '  document.querySelectorAll("[data-input]").forEach(el => { if (resetInputs || document.activeElement !== el) el.value = String(state[el.dataset.input]); });',
        "  renderCollections();" if (program.records or program.has_navigation) else "",
        "}",
        'document.querySelectorAll("[data-action]").forEach(el => {',
        "  el.addEventListener('click', () => {",
        "    const action = actions[el.dataset.action];",
        "    if (!action) throw new Error('Unknown action');",
        "    try { const next = action(state); showError(next === state ? 'Action rejected by declared rules' : ''); state = next; }",
        "    catch (error) { showError('Action rejected: ' + error.message); return; }" if (program.records or program.has_navigation) else "    catch (_) { showError('Action rejected: integer overflow or invalid value'); return; }",
        "    try { saveSnapshot(); } catch (_) { showError('Could not save state'); }" if (program.records or program.has_navigation) else "    try { const saved = {}; for (const key of persistentKeys) saved[key] = state[key]; localStorage.setItem(storageKey, JSON.stringify(saved)); } catch (_) { /* storage is optional */ }",
        "    render(true);",
        "  });",
        "});",
        "function validateInput(el) {",
        "  const key = el.dataset.input; const isText = typeof initialState[key] === 'string'; const raw = isText ? el.value : el.value.trim();",
        "  const parsed = Number(raw);",
        "  let accepted = false;",
        "  if (isText ? validText(raw) : (raw !== '' && /^-?[0-9]+$/.test(raw) && Number.isInteger(parsed) && parsed >= -2147483648 && parsed <= 2147483647)) {",
        "    const nextState = { ...state, [key]: isText ? raw : parsed };",
        "    accepted = validateState(nextState);",
        "    if (accepted) { state = nextState; try { saveSnapshot(); } catch (_) { showError('Could not save state'); } render(); }" if (program.records or program.has_navigation) else "    if (accepted) { state = nextState; try { const saved = {}; for (const name of persistentKeys) saved[name] = state[name]; if (typeof localStorage !== 'undefined') localStorage.setItem(storageKey, JSON.stringify(saved)); } catch (_) {} render(); }",
        "  }",
        "  const invalid = (isText || raw !== '') && !accepted;",
        "  el.setAttribute('aria-invalid', String(invalid));",
        "  const error = document.getElementById('error-' + key);",
        "  if (error) error.hidden = !invalid;",
        "}",
        "document.querySelectorAll('[data-input]').forEach(el => {",
        "  el.addEventListener('input', () => validateInput(el));",
        "  el.addEventListener('blur', () => { if (typeof initialState[el.dataset.input] !== 'string' && el.value.trim() === '') el.value = String(state[el.dataset.input]); validateInput(el); });",
        "});",
        "render();",
        "if (restoreError) showError('Saved data rejected; defaults restored');",
        "</script></body></html>",
    ]) + "\n"

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("source")
    cli.add_argument("--output", default="build/web/index.html")
    args = cli.parse_args()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generate(Path(args.source).read_text(encoding="utf-8")), encoding="utf-8")
    print(target)
