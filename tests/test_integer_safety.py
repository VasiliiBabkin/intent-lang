"""Boundary tests for portable Intent integer semantics."""
import unittest
from intent_core import parse, transition

class IntegerSafetyTests(unittest.TestCase):
    def test_reject_large_initializer(self):
        with self.assertRaisesRegex(ValueError, "Integer overflow"):
            parse('app "Bounds"\nstate n = 2147483648\n')

    def test_reject_overflow_in_transition_without_mutating_input(self):
        program = parse('app "Bounds"\nstate n = 2147483647\naction add: n = n + 1\n')
        state = program.states.copy()
        with self.assertRaisesRegex(ValueError, "Integer overflow"):
            transition(program, state, "add")
        self.assertEqual(state["n"], 2147483647)

    def test_valid_boundary(self):
        program = parse('app "Bounds"\nstate n = 2147483647\naction sub: n = n - 1\n')
        result, accepted = transition(program, program.states, "sub")
        self.assertTrue(accepted)
        self.assertEqual(result["n"], 2147483646)

if __name__ == "__main__":
    unittest.main()
