"""Regression cases found during the first public alpha audit."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from sedrava_core import parse, resolve, transition
from web_codegen import generate
from android_codegen_v03 import generate as android


class AlphaCore(unittest.TestCase):
    def test_signed_minimum_and_literal_overflow(self):
        p = parse('app "Bounds"\nstate n = -2147483648\naction up: n = n + 1\n')
        self.assertEqual(transition(p, p.states, 'up')[0]['n'], -2147483647)
        for expression in ('2147483648', '-2147483649', 'false and (2147483648 == 0)'):
            with self.subTest(expression=expression), self.assertRaisesRegex(ValueError, 'overflow'):
                parse('app "Bounds"\nstate n = ' + expression)

    def test_all_derived_values_validated_before_commit(self):
        p = parse('app "Atomic"\nstate n = 10\nstate b = false\nderive doubled = n * 2\naction bad:\n    b = true\n    n = 2147483647\n')
        original = p.states.copy()
        with self.assertRaisesRegex(ValueError, 'overflow'):
            transition(p, original, 'bad')
        self.assertEqual(original, {'n': 10, 'b': False})
        with self.assertRaisesRegex(ValueError, 'overflow'):
            parse('app "Bad"\nstate n = 2147483647\nderive doubled = n * 2\n')

    def test_duplicate_screen_tabs_reserved_names(self):
        for source in ('app "A"\nscreen main:\n    text "A"\nscreen main:\n    text "B"',
                       'app "A"\nstate n = 0\naction add:\n\tn = 1',
                       'app "A"\nstate true = 0', 'app "A"\nstate class = 0'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse(source)

    def test_empty_test_sequence_is_initial_state(self):
        from sedrava_core import run
        self.assertEqual(run(parse('app "A"\nstate n = 0\ntest initial: -> n == 0')), 1)

    def test_action_size_and_widget_indentation(self):
        source = 'app "Steps"\nstate n = 0\naction many:\n' + '    n=0\n' * 10001
        with self.assertRaisesRegex(ValueError, 'statement limit'):
            parse(source)
        with self.assertRaisesRegex(ValueError, 'indentation'):
            parse('app "Screen"\nscreen main:\n    text "A"\n        text "B"')

    def test_expansion_limit(self):
        source = 'app "Bounded"\nstate n = 0\nderive d0 = n\n'
        source += '\n'.join(f'derive d{i} = d{i-1} + d{i-1}' for i in range(1, 30))
        with self.assertRaisesRegex(ValueError, 'expansion limit'):
            parse(source)

    def test_cli_from_path_with_spaces(self):
        cli = Path(__file__).resolve().parents[1] / 'sedrava_cli.py'
        with tempfile.TemporaryDirectory(prefix='sedrava alpha ') as directory:
            source = Path(directory) / 'my app.sdr'
            source.write_text('app "A"\nstate n = 0\naction add: n = n + 1\n')
            result = subprocess.run([sys.executable, str(cli), 'run', str(source), 'add'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {'n': 1})
            result = subprocess.run([sys.executable, str(cli), 'run', str(source), 'missing'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn('Traceback', result.stderr)

    def test_script_and_kotlin_string_escaping(self):
        source = 'app "</script><script>globalThis.injected=true</script> $context"\nstate context = 0\naction add: context = context + 1\nscreen main:\n    text "$context"\n    value context\n    button "Add" -> add\n'
        page = generate(source)
        self.assertEqual(page.count('</script>'), 1)
        with tempfile.TemporaryDirectory() as directory:
            code = android(source, directory).read_text()
            self.assertIn('Text("\\$context"', code)
            self.assertIn('var sdr_context by rememberSaveable', code)
            self.assertIn('catch (_: ArithmeticException)', code)
