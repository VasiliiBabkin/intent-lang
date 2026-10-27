"""Intent 0.3: restricted typed AST, interpreter and atomic transitions."""
import ast
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Assign:
    name: str
    expr: ast.expr

@dataclass(frozen=True)
class If:
    condition: ast.expr
    yes: tuple
    no: tuple

@dataclass(frozen=True)
class Program:
    name: str
    states: dict
    actions: dict
    rules: tuple
    tests: tuple
    widgets: tuple

def parse_expr(source, types):
    source = re.sub(r"\b(true|false)\b", lambda m: m[1].title(), source)
    try:
        node = ast.parse(source, mode="eval").body
    except SyntaxError as exc:
        raise ValueError("Invalid expression") from exc
    try:
        type_of(node, types)
    except ValueError as exc:
        unknown = next((item.id for item in ast.walk(node)
                        if isinstance(item, ast.Name) and item.id not in types), None)
        if unknown is not None:
            raise ValueError(f"Unknown identifier: {unknown}") from exc
        raise
    return node

def type_of(node, types):
    if isinstance(node, ast.Constant) and type(node.value) in (int, bool):
        return type(node.value)
    if isinstance(node, ast.Name) and node.id in types:
        return types[node.id]
    if isinstance(node, ast.UnaryOp):
        t = type_of(node.operand, types)
        if isinstance(node.op, ast.USub) and t is int: return int
        if isinstance(node.op, ast.Not) and t is bool: return bool
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        if type_of(node.left, types) is type_of(node.right, types) is int: return int
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        if all(type_of(x, types) is bool for x in node.values): return bool
    if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1:
        a, b = type_of(node.left, types), type_of(node.comparators[0], types)
        if a is b and (isinstance(node.ops[0], (ast.Eq, ast.NotEq)) or
                       (a is int and isinstance(node.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE)))):
            return bool
    raise ValueError("Unsupported or ill-typed expression")

def evaluate(node, state):
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, ast.Name): return state[node.id]
    if isinstance(node, ast.UnaryOp):
        x = evaluate(node.operand, state)
        return -x if isinstance(node.op, ast.USub) else not x
    if isinstance(node, ast.BinOp):
        a, b = evaluate(node.left, state), evaluate(node.right, state)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        return a * b
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return all(evaluate(x, state) for x in node.values)
        return any(evaluate(x, state) for x in node.values)
    if isinstance(node, ast.Compare):
        a, b = evaluate(node.left, state), evaluate(node.comparators[0], state)
        op = node.ops[0]
        if isinstance(op, ast.Eq): return a == b
        if isinstance(op, ast.NotEq): return a != b
        if isinstance(op, ast.Lt): return a < b
        if isinstance(op, ast.LtE): return a <= b
        if isinstance(op, ast.Gt): return a > b
        return a >= b
    raise ValueError("Unsupported expression")

def parse(source):
    lines = [(len(raw) - len(raw.lstrip(" ")), raw.strip(), i)
             for i, raw in enumerate(source.splitlines(), 1)
             if raw.strip() and not raw.lstrip().startswith("#")]
    states, actions, rules, tests, widgets = {}, {}, [], [], []
    types = {}
    name = None
    i = 0
    def expression(source, known_types, line_number, column=1):
        try:
            return parse_expr(source, known_types)
        except ValueError as exc:
            message = str(exc)
            if message.startswith("Unknown identifier: "):
                identifier = message.partition(": ")[2]
                match = re.search(r"\\b" + re.escape(identifier) + r"\\b", source)
                if match:
                    column += match.start()
            raise ValueError(f"Line {line_number}, column {column}: {message}") from exc
    def block(pos, indent):
        result = []
        while pos < len(lines):
            depth, line, number = lines[pos]
            if depth < indent or line == "else:": break
            if depth != indent: raise ValueError(f"Line {number}: indentation")
            if line.startswith("if ") and line.endswith(":"):
                condition = expression(line[3:-1], types, number, depth + 4)
                if type_of(condition, types) is not bool: raise ValueError(f"Line {number}: condition must be bool")
                if pos + 1 >= len(lines) or lines[pos+1][0] <= indent: raise ValueError(f"Line {number}: empty if")
                yes, pos = block(pos + 1, lines[pos+1][0])
                no = ()
                if pos < len(lines) and lines[pos][:2] == (indent, "else:"):
                    pos += 1
                    if pos >= len(lines) or lines[pos][0] <= indent: raise ValueError(f"Line {number}: empty else")
                    no, pos = block(pos, lines[pos][0])
                result.append(If(condition, tuple(yes), tuple(no)))
                continue
            m = re.fullmatch(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
            if not m or m[1] not in types: raise ValueError(f"Line {number}: invalid assignment")
            node = expression(m[2], types, number, depth + m.start(2) + 1)
            if type_of(node, types) is not types[m[1]]: raise ValueError(f"Line {number}: type mismatch")
            result.append(Assign(m[1], node))
            pos += 1
        return tuple(result), pos
    while i < len(lines):
        depth, line, number = lines[i]
        if depth: raise ValueError(f"Line {number}: unexpected indentation")
        if m := re.fullmatch(r'app "([^"]+)"', line):
            if name: raise ValueError(f"Line {number}: duplicate app")
            name = m[1]
        elif m := re.fullmatch(r"state ([A-Za-z_]\w*)\s*=\s*(.+)", line):
            if actions or rules or tests or widgets: raise ValueError(f"Line {number}: states must precede actions")
            if m[1] in states: raise ValueError(f"Line {number}: duplicate state")
            node = expression(m[2], {}, number, m.start(2) + 1)
            states[m[1]] = evaluate(node, {})
            types[m[1]] = type(states[m[1]])
        elif m := re.fullmatch(r"action ([A-Za-z_]\w*):(?:\s*(.+))?", line):
            if m[1] in actions: raise ValueError(f"Line {number}: duplicate action")
            if m[2]: lines.insert(i+1, (4, m[2], number))
            if i+1 >= len(lines) or lines[i+1][0] <= 0: raise ValueError(f"Line {number}: empty action")
            body, i = block(i+1, lines[i+1][0])
            actions[m[1]] = body
            continue
        elif line.startswith("rule "):
            node = expression(line[5:], types, number, 6)
            if type_of(node, types) is not bool: raise ValueError(f"Line {number}: rule must be bool")
            rules.append(node)
        elif m := re.fullmatch(r"test ([A-Za-z_]\w*):\s*(.*?)\s*->\s*(.+)", line):
            node = expression(m[3], types, number, m.start(3) + 1)
            if type_of(node, types) is not bool: raise ValueError(f"Line {number}: test must be bool")
            tests.append((m[1], tuple(x.strip() for x in m[2].split(",")), node))
        elif line == "screen main:":
            i += 1
            while i < len(lines) and lines[i][0] > 0:
                _, item, n = lines[i]
                if m := re.fullmatch(r'text "([^"]*)"', item): widgets.append(("text", m[1]))
                elif m := re.fullmatch(r"value ([A-Za-z_]\w*)", item):
                    if m[1] not in states: raise ValueError(f"Line {n}: unknown state")
                    widgets.append(("value", m[1]))
                elif m := re.fullmatch(r'button "([^"]*)" -> ([A-Za-z_]\w*)', item):
                    widgets.append(("button", m[1], m[2]))
                else: raise ValueError(f"Line {n}: invalid widget")
                i += 1
            continue
        else: raise ValueError(f"Line {number}: invalid declaration")
        i += 1
    if not name: raise ValueError("Missing app")
    for _, seq, _ in tests:
        if any(action not in actions for action in seq): raise ValueError("Unknown action")
    for widget in widgets:
        if widget[0] == "button" and widget[2] not in actions: raise ValueError("Unknown action")
    if not all(evaluate(rule, states) for rule in rules): raise ValueError("Invalid initial state")
    return Program(name, states, actions, tuple(rules), tuple(tests), tuple(widgets))

def transition(program, state, action):
    if action not in program.actions: raise ValueError("Unknown action")
    candidate = state.copy()
    def execute(stmts):
        for stmt in stmts:
            if isinstance(stmt, Assign):
                candidate[stmt.name] = evaluate(stmt.expr, candidate)
            else:
                execute(stmt.yes if evaluate(stmt.condition, candidate) else stmt.no)
    execute(program.actions[action])
    if not all(evaluate(rule, candidate) for rule in program.rules):
        return state.copy(), False
    return candidate, True

def run(program):
    for name, actions, expected in program.tests:
        state = program.states.copy()
        for action in actions:
            state, accepted = transition(program, state, action)
            if not accepted: raise AssertionError(f"{name}: invariant violated")
        if not evaluate(expected, state): raise AssertionError(f"{name}: assertion failed")
    return len(program.tests)
