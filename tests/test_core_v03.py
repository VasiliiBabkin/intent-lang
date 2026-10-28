import pathlib
import tempfile
import unittest
from sedrava_core import parse, run, transition
from android_codegen_v03 import generate

EXAMPLE = pathlib.Path(__file__).resolve().parents[1] / "examples/workflow.sdr"

class Core03Tests(unittest.TestCase):
    def test_workflow(self):
        p = parse(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(run(p), 2)
        state = p.states.copy()
        for _ in range(5):
            state, accepted = transition(p, state, "advance")
            self.assertTrue(accepted)
        self.assertEqual(state, {"count": 3, "completed": True})

    def test_atomic_rejection(self):
        p = parse('app "X"\nstate count = 0\naction dec:\n    count = count - 1\nrule count >= 0')
        original = p.states.copy()
        state, accepted = transition(p, original, "dec")
        self.assertFalse(accepted)
        self.assertEqual(state, original)
        self.assertEqual(original["count"], 0)

    def test_if_else(self):
        p = parse('app "X"\nstate count = 0\naction flip:\n    if count == 0:\n        count = 1\n    else:\n        count = 0')
        one, _ = transition(p, p.states, "flip")
        zero, _ = transition(p, one, "flip")
        self.assertEqual(zero["count"], 0)

    def test_reject_unsafe_expression(self):
        with self.assertRaises(ValueError):
            parse('app "X"\nstate count = 0\naction bad:\n    count = __import__("os").system("id")')

    def test_reject_type_error(self):
        with self.assertRaises(ValueError):
            parse('app "X"\nstate count = 0\naction bad:\n    count = count + true')

    def test_android_codegen(self):
        with tempfile.TemporaryDirectory() as path:
            target = generate(EXAMPLE.read_text(encoding="utf-8"), path)
            code = target.read_text(encoding="utf-8")
            self.assertIn("next_count = (next_count + 1)", code)
            self.assertIn("next_completed = true", code)
            self.assertIn("Button(onClick", code)
            self.assertTrue((pathlib.Path(path)/"app/build.gradle.kts").exists())
