import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from intent import parse, run

class IntentTests(unittest.TestCase):
    def test_example(self):
        path = pathlib.Path(__file__).resolve().parents[1] / "examples/timer.intent"
        program = parse(path.read_text(encoding="utf-8"))
        self.assertEqual(run(program), 2)

    def test_arithmetic_counter(self):
        program = parse('app "X"\\nstate count = 0\\naction inc: count = count + 1\\ntest twice: inc, inc -> count == 2')
        self.assertEqual(run(program), 1)

    def test_reject_unsafe_expression(self):
        with self.assertRaisesRegex(ValueError, "Unsupported expression"):
            parse('app "X"\\nstate count = 0\\naction unsafe: count = __import__("os").system("echo bad")')

    def test_reject_unknown_action(self):
        with self.assertRaisesRegex(ValueError, "Unknown action"):
            parse('app "X"\nstate ready = false\ntest check: missing -> ready == true')

    def test_reject_type_mismatch(self):
        with self.assertRaisesRegex(ValueError, "type mismatch"):
            parse('app "X"\nstate ready = false\naction go: ready = 1')

    def test_invariant_violation(self):
        program = parse('app "X"\nstate count = 1\naction breakit: count = -1\nrule count >= 0\ntest check: breakit -> count == -1')
        with self.assertRaisesRegex(AssertionError, "invariant"):
            run(program)

if __name__ == "__main__":
    unittest.main()
