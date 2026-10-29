"""Sedrava 0.9 typed numeric input coverage."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from sedrava_core import parse
from web_codegen import generate as web
from android_codegen_v03 import generate as android

SOURCE = Path(__file__).resolve().parents[1].joinpath("examples/input_goal.sdr").read_text(encoding="utf-8")

class NumericInputTests(unittest.TestCase):
    def test_parse(self):
        p = parse(SOURCE)
        self.assertIn(("input_int", "target"), p.widgets)
        self.assertIn("target", p.persistent)

    def test_web(self):
        page = web(SOURCE)
        self.assertIn('data-input="target"', page)
        self.assertIn("Number.isInteger(parsed)", page)
        self.assertIn("const nextState = { ...state, [key]: isText ? raw : parsed }", page)

    def test_android(self):
        with TemporaryDirectory() as directory:
            code = Path(android(SOURCE, directory)).read_text(encoding="utf-8")
            self.assertIn("OutlinedTextField(value = draft_target", code)
            self.assertIn("draft_target = raw", code)
            self.assertIn("LaunchedEffect(sdr_target)", code)
            self.assertIn("?.toIntOrNull()", code)
            self.assertIn('putInt("target", state.sdr_target)', code)

    def test_bool_not_editable_as_number(self):
        with self.assertRaisesRegex(ValueError, "integer or text state"):
            parse('app "Bad"\nstate flag = true\nscreen main:\n    input flag\n')

if __name__ == "__main__":
    unittest.main()
