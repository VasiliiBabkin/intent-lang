"""Language navigation model: bounded screen stack and atomic domain transitions."""
from dataclasses import dataclass

MAX_SCREENS = 32
MAX_STACK = 32
MAX_NAV_COMMANDS = 64

@dataclass(frozen=True)
class Span:
    line: int
    column: int = 1

@dataclass(frozen=True)
class Widget:
    kind: str
    args: tuple
    span: Span

    def legacy(self):
        return (self.kind, *self.args)

@dataclass(frozen=True)
class Screen:
    name: str
    widgets: tuple
    guard: object
    span: Span

@dataclass(frozen=True)
class Navigation:
    name: str
    target: str
    action: str | None
    span: Span

@dataclass(frozen=True)
class Session:
    state: dict
    stack: tuple


def visible(program, state, screen):
    from sedrava_core import evaluate, resolve
    try:
        guard = program.screens[screen].guard
        return guard is None or evaluate(guard, resolve(state, program.derived)) is True
    except (ValueError, KeyError):
        return False


def valid_stack(program, stack):
    return (type(stack) is tuple and 1 <= len(stack) <= MAX_STACK
            and stack[0] == program.initial_screen
            and all(type(name) is str and name in program.screens for name in stack))


def normalize(program, state, stack):
    while len(stack) > 1 and not visible(program, state, stack[-1]):
        stack = stack[:-1]
    return Session(state, stack)


def initial_session(program, state=None):
    from sedrava_core import valid_state
    state = program.states.copy() if state is None else state.copy()
    if not valid_state(program, state): raise ValueError('Invalid session data')
    return Session(state, (program.initial_screen,))


def restore_session(program, state, stack):
    current = initial_session(program, state)
    return normalize(program, current.state, stack) if valid_stack(program, stack) else current


def dispatch(program, current, command):
    from sedrava_core import transition, valid_state
    if not valid_stack(program, current.stack) or not valid_state(program, current.state):
        return current, False
    state, stack = current.state, current.stack
    try:
        if command == '$back':
            stack = stack[:-1] if len(stack) > 1 else stack
        elif command in program.navigation:
            binding = program.navigation[command]
            if binding.action:
                state, accepted = transition(program, state, binding.action)
                if not accepted: return current, False
            if binding.target == 'pop':
                stack = stack[:-1] if len(stack) > 1 else stack
            else:
                if len(stack) >= MAX_STACK or not visible(program, state, binding.target):
                    return current, False
                stack = (*stack, binding.target)
        elif command in program.actions:
            state, accepted = transition(program, state, command)
            if not accepted: return current, False
        else:
            return current, False
        return normalize(program, state, stack), True
    except ValueError:
        return current, False


def edit_session(program, current, key, value):
    from sedrava_core import edit_state
    if not valid_stack(program, current.stack): return current, False
    state, accepted = edit_state(program, current.state, key, value)
    return (normalize(program, state, current.stack), True) if accepted else (current, False)


def select_item(program, current, collection, key, identity, command=None):
    from sedrava_records import ListValue
    items = current.state.get(collection)
    if (not isinstance(items, ListValue) or type(identity) is not int
            or not any(row_id == identity for row_id, _ in items.items)
            or type(program.states.get(key)) is not int):
        return current, False
    candidate, accepted = edit_session(program, current, key, identity)
    if not accepted: return current, False
    if command is None: return candidate, True
    candidate, accepted = dispatch(program, candidate, command)
    return (candidate, True) if accepted else (current, False)
