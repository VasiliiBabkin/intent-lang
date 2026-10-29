"""Regression checks for rule-aware integer input generation."""
import tempfile
import unittest
from pathlib import Path

from android_codegen_v03 import generate as android_generate
from web_codegen import generate as web_generate

SOURCE = """app "Input test"
state target = 2
persist target
derive reached = target >= 5
action reset:
    target = 2
rule target >= 0 and target <= 10
test initial: reset -> target == 2
screen main:
    text "Input test"
    input target
    value target
    show reached : text "Reached"
    button "Reset" -> reset
"""


class InputValidationGenerationTests(unittest.TestCase):
    def test_android_error_feedback_and_commit_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            path = android_generate(SOURCE, folder)
            kotlin = Path(path).read_text(encoding="utf-8")
        self.assertIn("val error_target = draft_target.isNotEmpty() && !valid_target", kotlin)
        self.assertIn("isError = error_target", kotlin)
        self.assertIn("supportingText = { if (error_target)", kotlin)
        self.assertIn("draft_target = raw", kotlin)
        self.assertIn("if (validState(next_target))", kotlin)
        self.assertIn('prefs.edit().putInt("target", parsed).apply()', kotlin)

    def test_web_validation_and_accessibility(self):
        page = web_generate(SOURCE)
        self.assertIn('aria-describedby="error-target"', page)
        self.assertIn('role="alert" hidden', page)
        self.assertIn("el.setAttribute('aria-invalid', String(invalid))", page)
        self.assertIn("el.addEventListener('input', () => validateInput(el))", page)
        self.assertIn("accepted = ", page)
        self.assertNotIn("accepted = ;", page)
        self.assertIn("const nextState = { ...state, [key]: parsed };", page)
        self.assertIn("const invalid = raw !== '' && !accepted;", page)


if __name__ == "__main__":
    unittest.main()
