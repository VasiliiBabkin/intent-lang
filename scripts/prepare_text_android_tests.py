"""Add JVM conformance tests beside generated code, without changing app sources."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from android_codegen_v03 import literal, quoted
from sedrava_core import parse
from text_cases import operations, trace


def kotlin(value):
    if value is None:
        return 'null'
    if type(value) is str:
        return quoted(value)
    if type(value) is bool:
        return str(value).lower()
    if type(value) is int:
        return str(value) + ('L' if not -2147483648 <= value <= 2147483647 else '')
    if type(value) is float:
        return str(value)
    if type(value) is list:
        return 'listOf<Any?>(' + ', '.join(map(kotlin, value)) + ')'
    return 'mapOf<String, Any?>(' + ', '.join(quoted(k) + ' to ' + kotlin(v) for k, v in value.items()) + ')'

from sedrava_android_identity import project_identity, kotlin_path


def prepare(project, source):
    program = parse(source)
    steps = operations(source)
    expected = trace(program, steps)
    lines = ['package '+project_identity(project), 'import org.junit.Assert.*', 'import org.junit.Test',
             'class TextStateTest {', '  @Test fun pythonOracleActionsInputsAndRestore() {',
             '    var state = SedravaState()']
    for i, (step, outcome) in enumerate(zip(steps, expected)):
        lines.append('    val before_' + str(i) + ' = state')
        if step[0] == 'action':
            expression = 'transitionState(state, ' + quoted(step[1]) + ')'
        elif step[0] == 'input':
            expression = 'editState(state, ' + quoted(step[1]) + ', ' + kotlin(step[2]) + ')'
        elif type(step[1]) is dict:
            expression = 'restoreState(' + kotlin(step[1]) + ')'
        else:
            # SharedPreferences.all always has a map shape; malformed XML is
            # handled by Android. Test the same fallback with an empty map.
            expression = 'restoreState(emptyMap<String, Any?>())'
        lines.append('    state = ' + expression)
        args = ', '.join('sdr_' + key + ' = ' + literal(value) for key, value in outcome['state'].items())
        lines.append('    assertEquals("step ' + str(i) + '", SedravaState(' + args + '), state)')
        if outcome['accepted'] is not None:
            method = 'assertNotSame' if outcome['accepted'] else 'assertSame'
            lines.append('    ' + method + '("atomic step ' + str(i) + '", before_' + str(i) + ', state)')
    lines += ['  }', '  @Test fun unicodeScalarBoundariesAndSurrogates() {',
              '    assertTrue(validText("😀".repeat(1024)))',
              '    assertFalse(validText("😀".repeat(1025)))',
              '    assertFalse(validText("a".repeat(1025)))',
              '    assertFalse(validText("\\uD800"))',
              '    assertFalse(validText("\\uDFFF"))',
              '    assertFalse(validText("a\\uD800b"))',
              '    assertTrue(validText(""))',
              '    assertTrue(validText("\\uD83D\\uDE00"))',
              '    assertNotEquals("é", "é")',
              '  }', '}']
    path = kotlin_path(project, 'test', 'TextStateTest.kt')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{path}: {len(steps)} Python-oracle steps + Unicode scalar boundary test')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--source', type=Path, default=ROOT / 'examples/text_profile.sdr')
    args = parser.parse_args()
    prepare(args.project, args.source.read_text(encoding='utf-8'))
