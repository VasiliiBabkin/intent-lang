"""Minimal deterministic Intent prototype (v0.1). No eval/exec."""
from dataclasses import dataclass
import re
import sys

IDENT = r"[A-Za-z_][A-Za-z_0-9]*"
@dataclass
class Program:
    name: str
    states: dict
    actions: dict
    rules: list
    tests: list

def value(token):
    token = token.strip()
    if token in ("true", "false"):
        return token == "true"
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    raise ValueError(f"Unsupported literal: {token}")

def predicate(source, state):
    match = re.fullmatch(rf"({IDENT})\s*(==|>=|<=|>|<|!=)\s*(-?\d+|true|false)", source.strip())
    if not match:
        raise ValueError(f"Invalid predicate: {source}")
    name, operator, literal = match.groups()
    if name not in state:
        raise ValueError(f"Unknown state: {name}")
    left, right = state[name], value(literal)
    if type(left) is not type(right):
        raise ValueError(f"Type mismatch: {name}")
    return {"==": lambda: left == right, "!=": lambda: left != right,
            ">=": lambda: left >= right, "<=": lambda: left <= right,
            ">": lambda: left > right, "<": lambda: left < right}[operator]()

def parse(source):
    name = None
    states, actions, rules, tests = {}, {}, [], []
    for lineno, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if m := re.fullmatch(r'app\s+"([^"]+)"', line):
                name = m[1]
            elif m := re.fullmatch(rf"state\s+({IDENT})\s*=\s*(.+)", line):
                if m[1] in states:
                    raise ValueError("Duplicate state")
                states[m[1]] = value(m[2])
            elif m := re.fullmatch(rf"action\s+({IDENT}):\s*({IDENT})\s*=\s*(.+)", line):
                if m[1] in actions:
                    raise ValueError("Duplicate action")
                actions[m[1]] = (m[2], value(m[3]))
            elif line.startswith("rule "):
                rules.append(line[5:])
            elif m := re.fullmatch(rf"test\s+({IDENT}):\s*(.*?)\s*->\s*(.+)", line):
                tests.append((m[1], [x.strip() for x in m[2].split(",")], m[3]))
            else:
                raise ValueError("Invalid syntax")
        except ValueError as exc:
            raise ValueError(f"Line {lineno}: {exc}") from exc
    if not name:
        raise ValueError("Missing app declaration")
    for action, (target, val) in actions.items():
        if target not in states:
            raise ValueError(f"Action {action}: unknown state {target}")
        if type(states[target]) is not type(val):
            raise ValueError(f"Action {action}: type mismatch")
    for rule in rules:
        predicate(rule, states)
    for _, sequence, expected in tests:
        predicate(expected, states)
        for action in sequence:
            if action not in actions:
                raise ValueError(f"Unknown action: {action}")
    return Program(name, states, actions, rules, tests)

def run(program):
    for name, sequence, expected in program.tests:
        state = program.states.copy()
        for action in sequence:
            target, val = program.actions[action]
            state[target] = val
            if not all(predicate(rule, state) for rule in program.rules):
                raise AssertionError(f"{name}: invariant violated after {action}")
        if not predicate(expected, state):
            raise AssertionError(f"{name}: assertion failed")
        print(f"PASS {name}")
    return len(program.tests)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python intent.py FILE.intent")
    with open(sys.argv[1], encoding="utf-8") as file:
        program = parse(file.read())
    print(f"Intent: {program.name}")
    run(program)
