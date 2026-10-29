"""Shared Python/JavaScript/JVM operation corpus for the text increment."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def operations(source):
    from sedrava_core import parse
    program = parse(source)
    key = next(key for key, value in program.states.items() if type(value) is str)
    values = ['', ' ', '  name  ', 'Русский 中文 😀', 'é', 'é',
              'true false', '</script><script>globalThis.injected=true</script>',
              '${context} $name "quoted" \\ /', 'a\rb\nc\t', '\x00\x08\x0c',
              'a' * 1024, 'a' * 1025, '😀' * 1024, '😀' * 1025,
              '\ud800', '\udfff', 'a\ud800b', 1, True, None, [], {}, 1.5]
    steps = [('action', action) for action in program.actions]
    steps += [('input', key, value) for value in values]
    steps += [('input', 'missing', 'value')]
    for other, initial in program.states.items():
        if type(initial) in (int, bool):
            wrong = ['wrong', None, True if type(initial) is int else 0]
            steps += [('input', other, value) for value in wrong]
            steps += [('restore', {key: 'Stable', other: value}) for value in wrong]
    steps += [('restore', {key: value}) for value in values]
    steps += [('restore', value) for value in (None, [], 'broken', True)]
    steps += [('action', action) for action in program.actions]
    return steps


def trace(program, steps):
    from sedrava_core import edit_state, restore_state, transition
    state = program.states.copy()
    result = []
    for step in steps:
        if step[0] == 'action':
            try:
                state, accepted = transition(program, state, step[1])
            except ValueError:
                accepted = False
        elif step[0] == 'input':
            state, accepted = edit_state(program, state, step[1], step[2])
        else:
            state = restore_state(program, step[1])
            accepted = None
        result.append({'state': state.copy(), 'accepted': accepted})
    return result
