"""Sedrava 0.8 derived read-only values across backends."""
import tempfile
import unittest
from pathlib import Path
from sedrava_core import parse, transition, resolve
from web_codegen import generate as web_generate
from android_codegen_v03 import generate as android_generate

SOURCE = """app "Derived"
state count = 0
derive doubled = count * 2
derive ready = doubled >= 4
action advance:
    if not ready:
        count = count + 1
action reset:
    count = 0
rule doubled <= 4
test finish: advance, advance -> ready == true
screen main:
    text "Derived"
    value count
    value doubled
    value ready
    button "Next" -> advance
    button "Reset" -> reset
"""

class DerivedTests(unittest.TestCase):
    def test_interpreter_and_readonly(self):
        program = parse(SOURCE)
        self.assertEqual(resolve(program.states, program.derived)["doubled"], 0)
        state, accepted = transition(program, program.states, "advance")
        self.assertTrue(accepted)
        self.assertEqual(resolve(state, program.derived)["doubled"], 2)
        state, accepted = transition(program, state, "advance")
        self.assertTrue(accepted)
        self.assertTrue(resolve(state, program.derived)["ready"])
        next_state, accepted = transition(program, state, "advance")
        self.assertEqual(next_state, state)
        self.assertTrue(accepted)

    def test_derived_is_not_assignable(self):
        with self.assertRaisesRegex(ValueError, "invalid assignment"):
            parse(SOURCE.replace("count = count + 1", "doubled = 5"))

    def test_web_codegen(self):
        output = web_generate(SOURCE)
        self.assertIn('derivedState["doubled"]', output)
        self.assertIn('derivedState["ready"]', output)
        self.assertIn('nextState["count"]', output)

    def test_android_codegen(self):
        with tempfile.TemporaryDirectory() as directory:
            code = android_generate(SOURCE, Path(directory)).read_text(encoding="utf-8")
            self.assertIn("val doubled = Math.multiplyExact(count, 2)", code)
            self.assertIn("val ready = (doubled >= 4)", code)
            self.assertIn("Text(\"doubled: \" + doubled.toString())", code)

    def test_derive_declaration_is_parsed_and_typed(self):
        program = parse(SOURCE)
        self.assertEqual(list(program.derived), ["doubled", "ready"])
        self.assertIs(program.states["count"].__class__, int)
        self.assertEqual(resolve({"count": 2}, program.derived), {
            "count": 2, "doubled": 4, "ready": True,
        })

    def test_derive_must_not_shadow_state(self):
        with self.assertRaisesRegex(ValueError, "duplicate identifier"):
            parse(SOURCE.replace("derive doubled = count * 2", "derive count = count * 2"))
