"""Android backend code-generation regression checks (no Android SDK needed)."""
import tempfile
import unittest
from pathlib import Path

from android_codegen_v03 import generate


SOURCE = """app "Guarded"
state count = 0
state finished = false
action advance:
    if count < 2:
        count = count + 1
    if count == 2:
        finished = true
action reset:
    count = 0
    finished = false
rule count >= 0 and count <= 2
rule finished == (count == 2)
screen main:
    text "Guarded"
    value count
    value finished
    button "Advance" -> advance
    button "Reset" -> reset
"""


class AndroidBackendRegressionTests(unittest.TestCase):
    def test_generated_kotlin_guards_and_atomic_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            target = generate(SOURCE, Path(directory) / "android")
            code = target.read_text(encoding="utf-8")
            self.assertIn("var next_count = count", code)
            self.assertIn("var next_finished = finished", code)
            self.assertIn("next_count = Math.addExact(next_count, 1)", code)
            self.assertIn("next_finished = true", code)
            self.assertIn("(next_count >= 0)", code)
            self.assertIn("count = next_count", code)
            self.assertIn("finished = next_finished", code)
            self.assertIn('Text("Advance")', code)
            self.assertIn('Text("Reset")', code)
            self.assertLess(code.index("      if (((next_count >= 0)"), code.index("count = next_count"))

    def test_rejects_invalid_program_before_generation(self):
        source = SOURCE.replace("rule count >= 0 and count <= 2", "rule count < 0")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate(source, Path(directory) / "android")
