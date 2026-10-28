"""Limits protect the compiler from oversized untrusted Sedrava sources."""
import unittest
from sedrava_core import parse, MAX_SOURCE_CHARS

class ResourceLimitTests(unittest.TestCase):
    def test_oversized_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "Source exceeds size limit"):
            parse(" " * (MAX_SOURCE_CHARS + 1))

    def test_oversized_expression_rejected(self):
        expression = " + ".join(["1"] * 140)
        with self.assertRaisesRegex(ValueError, "complexity limit"):
            parse('app "Limit"\nstate n = ' + expression + '\n')

    def test_small_program_still_works(self):
        p = parse('app "Small"\nstate n = 1 + 2\n')
        self.assertEqual(p.states["n"], 3)

if __name__ == "__main__":
    unittest.main()
