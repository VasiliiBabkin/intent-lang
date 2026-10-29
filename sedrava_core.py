"""Sedrava shared text/int32/bool core: restricted typed AST, interpreter and atomic transitions."""
import ast
import keyword
import re
from dataclasses import dataclass

MAX_SOURCE_CHARS = 100_000
MAX_TEXT_SCALARS = 1024
MAX_AST_NODES = 256
MAX_ACTION_STEPS = 10_000
MAX_BLOCK_DEPTH = 32
MAX_DERIVED_NODES = 4096

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1

def checked_int(value):
    if type(value) is int and not INT_MIN <= value <= INT_MAX:
        raise ValueError("Integer overflow: outside signed 32-bit range")
    return value


def checked_text(value):
    if type(value) is not str:
        raise ValueError("Text value required")
    if len(value) > MAX_TEXT_SCALARS:
        raise ValueError("Text exceeds 1024 Unicode scalar values")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise ValueError("Text contains an unpaired surrogate")
    return value


def checked_value(value, expected=None):
    if type(value) not in (int, bool, str) or (expected is not None and type(value) is not expected):
        raise ValueError("Value type mismatch")
    return checked_text(value) if type(value) is str else checked_int(value)


class LiteralError(ValueError):
    def __init__(self, message, offset):
        super().__init__(message)
        self.offset = offset


def read_literal(source, start=0):
    """Decode only the contract's double-quoted grammar, never Python escapes."""
    if start >= len(source) or source[start] != '"':
        raise LiteralError("Expected double-quoted text", start)
    chars = []
    i = start + 1
    escapes = {"\\": "\\", '"': '"', "n": "\n", "r": "\r", "t": "\t"}
    while i < len(source):
        char = source[i]
        if char == '"':
            try:
                return checked_text("".join(chars)), i + 1
            except ValueError as exc:
                raise LiteralError(str(exc), start) from exc
        if char in "\n\r":
            raise LiteralError("Unterminated text literal", i)
        if char == "\\":
            i += 1
            if i >= len(source) or source[i] not in escapes:
                raise LiteralError("Invalid text escape", i - 1)
            char = escapes[source[i]]
        chars.append(char)
        i += 1
    raise LiteralError("Unterminated text literal", start)


def literal_expression(source):
    """Keep booleans outside literals; placeholders prevent implicit concatenation."""
    prefix = "__sedrava_literal_"
    while prefix in source:
        prefix += "_"
    values, chunks = {}, []
    i = 0
    while i < len(source):
        if source[i] == '"':
            value, end = read_literal(source, i)
            name = prefix + str(len(values))
            values[name] = value
            chunks.append("(" + name + ")")
            i = end
        elif source[i] == "'":
            raise LiteralError("Text requires double quotes", i)
        else:
            end = source.find('"', i)
            end = len(source) if end == -1 else end
            chunk = source[i:end]
            if "'" in chunk:
                raise LiteralError("Text requires double quotes", i + chunk.index("'"))
            chunks.append(re.sub(r"\b(true|false)\b", lambda m: m[1].title(), chunk))
            i = end
    return "".join(chunks), values


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
    derived: dict = None
    persistent: tuple = ()

def parse_expr(source, types):
    source, literals = literal_expression(source)
    try:
        node = ast.parse(source, mode="eval").body
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("Invalid or excessively nested expression") from exc
    class ReplaceLiterals(ast.NodeTransformer):
        def visit_Name(self, item):
            return ast.copy_location(ast.Constant(literals[item.id]), item) if item.id in literals else item
    node = ReplaceLiterals().visit(node)
    if sum(1 for _ in ast.walk(node)) > MAX_AST_NODES:
        raise ValueError("Expression exceeds complexity limit")
    # Normalize the signed minimum before evaluating its positive AST operand.
    for parent in ast.walk(node):
        for field, value in ast.iter_fields(parent):
            if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub) and isinstance(value.operand, ast.Constant) and type(value.operand.value) is int and value.operand.value == -INT_MIN:
                setattr(parent, field, ast.Constant(INT_MIN))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant) and type(node.operand.value) is int and node.operand.value == -INT_MIN:
        node = ast.Constant(INT_MIN)
    for item in ast.walk(node):
        if isinstance(item, ast.Constant):
            checked_value(item.value)
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
    if isinstance(node, ast.Constant) and type(node.value) in (int, bool, str):
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
    if isinstance(node, ast.Constant): return checked_value(node.value)
    if isinstance(node, ast.Name): return checked_value(state[node.id])
    if isinstance(node, ast.UnaryOp):
        x = evaluate(node.operand, state)
        return checked_int(-x) if isinstance(node.op, ast.USub) else not x
    if isinstance(node, ast.BinOp):
        a, b = evaluate(node.left, state), evaluate(node.right, state)
        if isinstance(node.op, ast.Add): return checked_int(a + b)
        if isinstance(node.op, ast.Sub): return checked_int(a - b)
        return checked_int(a * b)
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
    if len(source) > MAX_SOURCE_CHARS:
        raise ValueError("Source exceeds size limit")
    for number, raw in enumerate(source.split("\n"), 1):
        for offset, char in enumerate(raw):
            if 0xD800 <= ord(char) <= 0xDFFF:
                raise ValueError(f"Line {number}: column {offset + 1}: Source contains an unpaired surrogate")
        if "\t" in raw[:len(raw) - len(raw.lstrip())]:
            raise ValueError(f"Line {number}: tabs are not allowed in indentation")
    lines = [(len(raw) - len(raw.lstrip(" ")), raw.strip(), i)
             for i, raw in enumerate(source.split("\n"), 1)
             if raw.strip() and not raw.lstrip().startswith("#")]
    states, actions, rules, tests, widgets, derived = {}, {}, [], [], [], {}
    persistent = []
    types = {}
    name = None
    screen_seen = False
    i = 0
    def expression(source, known_types, line_number, column=1):
        try:
            return parse_expr(source, known_types)
        except ValueError as exc:
            message = str(exc)
            column += getattr(exc, "offset", 0)
            if message.startswith("Unknown identifier: "):
                identifier = message.partition(": ")[2]
                match = re.search(r"\b" + re.escape(identifier) + r"\b", source)
                if match:
                    column += match.start()
            raise ValueError(f"Line {line_number}: column {column}: {message}") from exc
    def label(source, line_number, column=1):
        try:
            value, end = read_literal(source)
            if source[end:].strip():
                raise LiteralError("Unexpected text after literal", end)
            return value
        except LiteralError as exc:
            raise ValueError(f"Line {line_number}: column {column + exc.offset}: {exc}") from exc
    def statement_count(body):
        return sum(1 + (statement_count(stmt.yes) + statement_count(stmt.no) if isinstance(stmt, If) else 0) for stmt in body)
    def block(pos, indent, nesting=0):
        if nesting > MAX_BLOCK_DEPTH:
            raise ValueError(f"Line {lines[pos][2]}: block nesting limit")
        result = []
        while pos < len(lines):
            depth, line, number = lines[pos]
            if depth < indent or line == "else:": break
            if depth != indent: raise ValueError(f"Line {number}: indentation")
            if line.startswith("if ") and line.endswith(":"):
                condition = expression(line[3:-1], types, number, depth + 4)
                if type_of(condition, types) is not bool: raise ValueError(f"Line {number}: condition must be bool")
                if pos + 1 >= len(lines) or lines[pos+1][0] <= indent: raise ValueError(f"Line {number}: empty if")
                yes, pos = block(pos + 1, lines[pos+1][0], nesting + 1)
                no = ()
                if pos < len(lines) and lines[pos][:2] == (indent, "else:"):
                    pos += 1
                    if pos >= len(lines) or lines[pos][0] <= indent: raise ValueError(f"Line {number}: empty else")
                    no, pos = block(pos, lines[pos][0], nesting + 1)
                result.append(If(condition, tuple(yes), tuple(no)))
                continue
            m = re.fullmatch(r"([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.+)", line)
            if not m or m[1] not in states: raise ValueError(f"Line {number}: invalid assignment")
            node = expression(m[2], types, number, depth + m.start(2) + 1)
            if type_of(node, types) is not types[m[1]]: raise ValueError(f"Line {number}: type mismatch")
            result.append(Assign(m[1], node))
            pos += 1
        return tuple(result), pos
    while i < len(lines):
        depth, line, number = lines[i]
        if depth: raise ValueError(f"Line {number}: unexpected indentation")
        if m := re.fullmatch(r'app (.+)', line):
            if name is not None: raise ValueError(f"Line {number}: duplicate app")
            name = label(m[1], number, 5)
        elif m := re.fullmatch(r"state ([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.+)", line):
            if actions or rules or tests or widgets: raise ValueError(f"Line {number}: states must precede actions")
            if m[1] in types: raise ValueError(f"Line {number}: duplicate state")
            if keyword.iskeyword(m[1]) or m[1] in ("true", "false"):
                raise ValueError(f"Line {number}: reserved identifier {m[1]}")
            node = expression(m[2], {}, number, m.start(2) + 1)
            try:
                states[m[1]] = evaluate(node, {})
            except ValueError as exc:
                raise ValueError(f"Line {number}: column {m.start(2) + 1}: {exc}") from exc
            types[m[1]] = type(states[m[1]])
        elif m := re.fullmatch(r"persist ([A-Za-z_][A-Za-z_0-9]*)", line):
            if m[1] not in states or m[1] in persistent:
                raise ValueError(f"Line {number}: persist requires a unique declared state")
            persistent.append(m[1])
        elif m := re.fullmatch(r"derive ([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.+)", line):
            if actions or rules or tests or widgets:
                raise ValueError(f"Line {number}: derives must precede actions")
            if m[1] in types:
                raise ValueError(f"Line {number}: duplicate identifier")
            node = expression(m[2], types, number, m.start(2) + 1)
            if keyword.iskeyword(m[1]) or m[1] in ("true", "false"):
                raise ValueError(f"Line {number}: reserved identifier {m[1]}")
            derived[m[1]] = node
            types[m[1]] = type_of(node, types)
        elif m := re.fullmatch(r"action ([A-Za-z_][A-Za-z_0-9]*):(?:\s*(.+))?", line):
            if m[1] in actions: raise ValueError(f"Line {number}: duplicate action")
            if m[2]: lines.insert(i+1, (4, m[2], number))
            if i+1 >= len(lines) or lines[i+1][0] <= 0: raise ValueError(f"Line {number}: empty action")
            body, i = block(i+1, lines[i+1][0])
            if statement_count(body) > MAX_ACTION_STEPS:
                raise ValueError(f"Line {number}: action exceeds statement limit")
            actions[m[1]] = body
            continue
        elif line.startswith("rule "):
            node = expression(line[5:], types, number, 6)
            if type_of(node, types) is not bool: raise ValueError(f"Line {number}: rule must be bool")
            rules.append(node)
        elif m := re.fullmatch(r"test ([A-Za-z_][A-Za-z_0-9]*):\s*(.*?)\s*->\s*(.+)", line):
            node = expression(m[3], types, number, m.start(3) + 1)
            if type_of(node, types) is not bool: raise ValueError(f"Line {number}: test must be bool")
            tests.append((m[1], tuple(x.strip() for x in m[2].split(",") if x.strip()), node))
        elif line == "screen main:":
            if screen_seen: raise ValueError(f"Line {number}: duplicate screen main")
            screen_seen = True
            i += 1
            widget_indent = lines[i][0] if i < len(lines) else 0
            while i < len(lines) and lines[i][0] > 0:
                widget_depth, item, n = lines[i]
                if widget_depth != widget_indent: raise ValueError(f"Line {n}: widget indentation")
                if m := re.fullmatch(r'text (.+)', item): widgets.append(("text", label(m[1], n, widget_depth + 6)))
                elif m := re.fullmatch(r"value ([A-Za-z_][A-Za-z_0-9]*)", item):
                    if m[1] not in types: raise ValueError(f"Line {n}: unknown state")
                    widgets.append(("value", m[1]))
                elif m := re.fullmatch(r'input ([A-Za-z_][A-Za-z_0-9]*)', item):
                    if m[1] not in states or type(states[m[1]]) not in (int, str):
                        raise ValueError(f"Line {n}: input requires an integer or text state")
                    widgets.append(("input_text" if type(states[m[1]]) is str else "input_int", m[1]))
                elif m := re.fullmatch(r'show ([A-Za-z_][A-Za-z_0-9]*) : text (.+)', item):
                    if m[1] not in types or types[m[1]] is not bool:
                        raise ValueError(f"Line {n}: show requires a boolean state or derive")
                    widgets.append(("show_text", m[1], label(m[2], n, widget_depth + m.start(2) + 1)))
                elif m := re.fullmatch(r'button (.+) -> ([A-Za-z_][A-Za-z_0-9]*)', item):
                    widgets.append(("button", label(m[1], n, widget_depth + 8), m[2]))
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
    # Bound expanded derived expressions: generators inline them in actions/rules.
    sizes = {key: 1 for key in states}
    for key, expr in derived.items():
        sizes[key] = sum(sizes[item.id] if isinstance(item, ast.Name) else 1 for item in ast.walk(expr))
        if sizes[key] > MAX_DERIVED_NODES:
            raise ValueError("Derived expression exceeds expansion limit")
    values = resolve(states, derived)
    if not all(evaluate(rule, values) for rule in rules): raise ValueError("Invalid initial state")
    return Program(name, states, actions, tuple(rules), tuple(tests), tuple(widgets), derived, tuple(persistent))

def resolve(state, derived):
    values = {name: checked_value(value) for name, value in state.items()}
    for name, expr in (derived or {}).items():
        values[name] = evaluate(expr, values)
    return values

def valid_state(program, state):
    try:
        if state.keys() != program.states.keys():
            return False
        for key, initial in program.states.items():
            checked_value(state[key], type(initial))
        values = resolve(state, program.derived)
        return all(evaluate(rule, values) for rule in program.rules)
    except (ValueError, KeyError):
        return False


def edit_state(program, state, key, value):
    if key not in program.states:
        return state.copy(), False
    candidate = {**state, key: value}
    return (candidate, True) if valid_state(program, candidate) else (state.copy(), False)


def restore_state(program, saved):
    candidate = program.states.copy()
    if type(saved) is dict:
        for key, initial in program.states.items():
            if key in program.persistent and key in saved:
                try:
                    candidate[key] = checked_value(saved[key], type(initial))
                except ValueError:
                    pass
    return candidate if valid_state(program, candidate) else program.states.copy()

def transition(program, state, action):
    if action not in program.actions: raise ValueError("Unknown action")
    if not valid_state(program, state): raise ValueError("Invalid action input state")
    candidate = state.copy()
    steps = 0
    def execute(stmts):
        nonlocal steps
        for stmt in stmts:
            steps += 1
            if steps > MAX_ACTION_STEPS:
                raise ValueError("Action exceeds execution step limit")
            if isinstance(stmt, Assign):
                candidate[stmt.name] = evaluate(stmt.expr, resolve(candidate, program.derived))
                resolve(candidate, program.derived)
            else:
                execute(stmt.yes if evaluate(stmt.condition, resolve(candidate, program.derived)) else stmt.no)
    execute(program.actions[action])
    values = resolve(candidate, program.derived)
    if not all(evaluate(rule, values) for rule in program.rules):
        return state.copy(), False
    return candidate, True

def run(program):
    for name, actions, expected in program.tests:
        state = program.states.copy()
        for action in actions:
            state, accepted = transition(program, state, action)
            if not accepted: raise AssertionError(f"{name}: invariant violated")
        if not evaluate(expected, resolve(state, program.derived)): raise AssertionError(f"{name}: assertion failed")
    return len(program.tests)
