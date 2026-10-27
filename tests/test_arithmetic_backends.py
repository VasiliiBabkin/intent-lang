"""Cross-backend regression checks for checked integer operations."""
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from intent_core import parse, transition
from web_codegen import generate as web_generate
from android_codegen_v03 import generate as android_generate

SOURCE = """app "Arithmetic"
state n = 2147483647
derive doubled = n * 2
action reset: n = 1
action add: n = n + 1
screen main:
    value n
    value doubled
    button "Reset" -> reset
"""

class ArithmeticBackendTests(unittest.TestCase):
    def test_interpreter_rejects_derived_overflow_on_evaluation(self):
        from intent_core import resolve
        p = parse(SOURCE)
        with self.assertRaisesRegex(ValueError, "Integer overflow"):
            resolve(p.states, p.derived)

    def test_web_emits_checked_arithmetic(self):
        output = web_generate(SOURCE)
        self.assertIn("checkedInt(", output)
        self.assertIn("function checkedInt", output)

    def test_android_emits_exact_arithmetic(self):
        with TemporaryDirectory() as directory:
            output = Path(android_generate(SOURCE, directory)).read_text(encoding="utf-8")
            self.assertIn("Math.multiplyExact(", output)
            self.assertIn("Math.addExact(", output)

    def test_unary_minus_web_checked(self):
        source = """app "Negate"
state n = -2147483647
action down: n = -n
screen main:
    value n
"""
        self.assertIn("checkedInt(-(", web_generate(source))

if __name__ == "__main__":
    unittest.main()
