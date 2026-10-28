"""Intent 0.9 persistence and conditional display regression."""
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from intent_core import parse, run
from web_codegen import generate as web
from android_codegen_v03 import generate as android

SOURCE = Path(__file__).resolve().parents[1].joinpath("examples/daily_steps.intent").read_text(encoding="utf-8")

class PersistentUiTests(unittest.TestCase):
    def test_parser(self):
        p = parse(SOURCE)
        self.assertEqual(p.persistent, ("count",))
        self.assertIn(("show_text", "done", "Goal reached!"), p.widgets)
        self.assertEqual(run(p), 2)

    def test_web(self):
        html = web(SOURCE)
        self.assertIn("localStorage.getItem", html)
        self.assertIn("localStorage.setItem", html)
        self.assertIn('data-show="done"', html)

    def test_android(self):
        with TemporaryDirectory() as directory:
            code = Path(android(SOURCE, directory)).read_text(encoding="utf-8")
            self.assertIn('prefs.getInt("count", 0)', code)
            self.assertIn('putInt("count", next_count)', code)
            self.assertIn('if (done) { Text("Goal reached!") }', code)

    def test_invalid_persistence(self):
        with self.assertRaisesRegex(ValueError, "persist requires"):
            parse('app "Bad"\npersist missing\n')

    def test_invalid_conditional_type(self):
        with self.assertRaisesRegex(ValueError, "boolean"):
            parse('app "Bad"\nstate n = 0\nscreen main:\n    show n : text "No"\n')

if __name__ == "__main__":
    unittest.main()
