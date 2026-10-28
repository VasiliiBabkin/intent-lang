import pathlib
import unittest
from sedrava_core import parse, run, transition
from web_codegen import generate

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "examples/workflow.sdr").read_text(encoding="utf-8")

class WebBackendTests(unittest.TestCase):
    def test_workflow_generated(self):
        html = generate(SOURCE)
        self.assertIn("<!doctype html>", html)
        self.assertIn("nextState[\"count\"] = checkedInt(nextState[\"count\"] + 1)", html)
        self.assertIn("nextState[\"completed\"] = true", html)
        self.assertIn('data-action="advance"', html)
        self.assertIn('data-state="completed"', html)

    def test_atomic_invariant_guard(self):
        html = generate(SOURCE)
        self.assertIn("return (", html)
        self.assertIn("? nextState : state;", html)
        self.assertIn("const nextState = { ...state };", html)

    def test_escaped_ui(self):
        source = 'app "X"\nstate x = 0\naction go: x = 1\nscreen main:\n    text "<script>alert(1)</script>"\n    button "<b>" -> go'
        html = generate(source)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;b&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_interpreter_reference(self):
        program = parse(SOURCE)
        self.assertEqual(run(program), 2)
        state = program.states.copy()
        for _ in range(3):
            state, ok = transition(program, state, "advance")
            self.assertTrue(ok)
        self.assertEqual(state, {"count": 3, "completed": True})
