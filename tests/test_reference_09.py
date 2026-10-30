"""Reference application contract for Sedrava 0.9 across Python and generated platforms."""
import unittest
from pathlib import Path

from sedrava_core import parse, run, transition
from android_codegen_v03 import generate as generate_android
from web_codegen import generate as generate_web

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "examples" / "reference_09.sdr").read_text(encoding="utf-8")


class Reference09Tests(unittest.TestCase):
    def test_contract(self):
        p = parse(SOURCE)
        self.assertEqual(p.name, "Sedrava 0.9 Lab")
        self.assertEqual(set(p.persistent), {"goal", "progress", "sessions"})
        self.assertEqual(len(p.tests), 4)
        self.assertEqual(run(p), 4)

    def test_progress_bounds_and_atomic_transitions(self):
        p = parse(SOURCE)
        state = dict(p.states)
        for _ in range(7):
            state, accepted = transition(p, state, "add")
            self.assertTrue(accepted)
        self.assertEqual(state["progress"], 5)
        self.assertEqual(state["sessions"], 5)
        state, accepted = transition(p, state, "subtract")
        self.assertTrue(accepted)
        self.assertEqual(state["progress"], 4)
        state, accepted = transition(p, state, "reset")
        self.assertTrue(accepted)
        self.assertEqual(state["progress"], 0)
        self.assertEqual(state["sessions"], 5)
        state, accepted = transition(p, state, "restore")
        self.assertTrue(accepted)
        self.assertEqual(state, p.states)

    def test_web_contract(self):
        html = generate_web(SOURCE)
        for token in ('data-input="goal"', "localStorage", "Goal reached!", "Keep going", "Add progress"):
            self.assertIn(token, html)

    def test_android_contract(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            kt = generate_android(SOURCE, folder).read_text(encoding="utf-8")
            manifest = (Path(folder) / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
            for token in ("OutlinedTextField", "getSharedPreferences", "isError", "Add progress", "Restore defaults"):
                self.assertIn(token, kt)
            self.assertIn("android.intent.action.MAIN", manifest)
            self.assertIn("android.intent.category.LAUNCHER", manifest)


if __name__ == "__main__":
    unittest.main()
