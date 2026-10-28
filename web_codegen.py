"""Intent web backend: generate self-contained HTML + JS from the shared AST."""
import argparse
import ast
import html
import json
from pathlib import Path
from intent_core import Assign, If, parse, run

def js_expr(node, names):
    if isinstance(node, ast.Constant):
        return json.dumps(node.value)
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
        if isinstance(stmt, Assign):
            result.append(f"{pad}{names[stmt.name]} = {js_expr(stmt.expr, names)};")
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

def generate(source):
    program = parse(source)
    run(program)
    if not program.widgets:
        raise ValueError("Missing screen main")
    initial = json.dumps(program.states, ensure_ascii=False)
    names = {key: "nextState[" + json.dumps(key) + "]" for key in program.states}
    for key, expr in (program.derived or {}).items():
        names[key] = js_expr(expr, names)
    rules = " && ".join(js_expr(rule, names) for rule in program.rules) or "true"
    actions = []
    for name, body in program.actions.items():
        actions.extend([
            f"  {json.dumps(name)}: (state) => {{",
            "    const nextState = { ...state };",
            *statements(body, names),
            f"    return ({rules}) ? nextState : state;",
            "  },",
        ])
    render_names = {key: "derivedState[" + json.dumps(key) + "]" for key in program.states}
    derived_lines = []
    for key, expr in (program.derived or {}).items():
        derived_lines.append("  derivedState[" + json.dumps(key) + "] = " + js_expr(expr, render_names) + ";")
        render_names[key] = "derivedState[" + json.dumps(key) + "]"
    widgets = []
    for widget in program.widgets:
        if widget[0] == "text":
            widgets.append(f'<h1>{html.escape(widget[1])}</h1>')
        elif widget[0] == "value":
            key = html.escape(widget[1], quote=True)
            widgets.append(f'<p>{key}: <output data-state="{key}"></output></p>')
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
        "<style>body{font:18px system-ui;max-width:38rem;margin:3rem auto;padding:0 1rem}button{padding:.7rem 1rem;margin:.25rem;border-radius:.5rem;cursor:pointer}input[aria-invalid="true"]{outline:2px solid #b42318}small[role="alert"]{display:block;color:#b42318}small[hidden]{display:none}</style>",
        "</head><body>",
        *widgets,
        "<script>",
        f"const initialState = {initial};",
        "const storageKey = 'intent:' + (typeof location !== 'undefined' ? location.pathname : '/') + ':' + " + json.dumps(program.name) + ";",
        "const persistentKeys = " + json.dumps(list(program.persistent)) + ";",
        "let state = { ...initialState };",
        "try { const saved = JSON.parse((typeof localStorage !== 'undefined' ? localStorage.getItem(storageKey) : null) || '{}'); if (saved && typeof saved === 'object' && !Array.isArray(saved)) { for (const key of persistentKeys) { if (Object.hasOwn(saved, key) && typeof saved[key] === typeof initialState[key] && (typeof saved[key] !== 'number' || (Number.isInteger(saved[key]) && saved[key] >= -2147483648 && saved[key] <= 2147483647))) state[key] = saved[key]; } } } catch (_) { /* unavailable or corrupt storage */ }",
        "function checkedInt(n) { if (!Number.isInteger(n) || n < -2147483648 || n > 2147483647) throw new RangeError('Intent integer overflow'); return n; }",
        "const actions = {",
        *actions,
        "};",
        "function render() {",
        "  const derivedState = { ...state };",
        *derived_lines,
        '  document.querySelectorAll("[data-state]").forEach(el => { el.textContent = String(derivedState[el.dataset.state]); });',
        '  document.querySelectorAll("[data-show]").forEach(el => { el.hidden = !derivedState[el.dataset.show]; });',
        '  document.querySelectorAll("[data-input]").forEach(el => { if (document.activeElement !== el) el.value = String(state[el.dataset.input]); });',
        "}",
        'document.querySelectorAll("[data-action]").forEach(el => {',
        "  el.addEventListener('click', () => {",
        "    const action = actions[el.dataset.action];",
        "    if (!action) throw new Error('Unknown action');",
        "    state = action(state);",
        "    try { const saved = {}; for (const key of persistentKeys) saved[key] = state[key]; localStorage.setItem(storageKey, JSON.stringify(saved)); } catch (_) { /* storage is optional */ }",
        "    render();",
        "  });",
        "});",
        "function validateInput(el) {",
        "  const key = el.dataset.input; const raw = el.value.trim();",
        "  const parsed = Number(raw);",
        "  let accepted = false;",
        "  if (raw !== '' && /^-?[0-9]+$/.test(raw) && Number.isInteger(parsed) && parsed >= -2147483648 && parsed <= 2147483647) {",
        "    const nextState = { ...state, [key]: parsed };",
        "    accepted = ; + rules + ;",
        "    if (accepted) { state = nextState; try { const saved = {}; for (const name of persistentKeys) saved[name] = state[name]; if (typeof localStorage !== 'undefined') localStorage.setItem(storageKey, JSON.stringify(saved)); } catch (_) {} render(); }",
        "  }",
        "  const invalid = raw !== '' && !accepted;",
        "  el.setAttribute('aria-invalid', String(invalid));",
        "  const error = document.getElementById('error-' + key);",
        "  if (error) error.hidden = !invalid;",
        "}",
        "document.querySelectorAll('[data-input]').forEach(el => {",
        "  el.addEventListener('input', () => validateInput(el));",
        "  el.addEventListener('blur', () => { if (el.value.trim() === '') el.value = String(state[el.dataset.input]); validateInput(el); });",
        "}",
        "render();",
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
