"""Line-aware diagnostic regression tests for Sedrava 0.8."""
import unittest

from sedrava_core import parse


class LineDiagnosticTests(unittest.TestCase):
    def assert_line_error(self, source, number):
        with self.assertRaisesRegex(ValueError, rf"Line {number}:"):
            parse(source)

    def test_unknown_symbol_in_action(self):
        self.assert_line_error('app "X"\nstate count = 0\naction go:\n    count = missing + 1\n', 4)

    def test_ill_typed_assignment(self):
        self.assert_line_error('app "X"\nstate count = 0\naction go:\n    count = true\n', 4)

    def test_invalid_rule(self):
        self.assert_line_error('app "X"\nstate count = 0\nrule count + true\n', 3)

    def test_invalid_test_expression(self):
        self.assert_line_error('app "X"\nstate count = 0\ntest bad: -> missing == 1\n', 3)

    def test_invalid_if_expression(self):
        self.assert_line_error('app "X"\nstate count = 0\naction go:\n    if missing > 0:\n        count = 1\n', 4)

    def test_duplicate_state(self):
        self.assert_line_error('app "X"\nstate count = 0\nstate count = 1\n', 3)

    def test_invalid_state_initializer(self):
        self.assert_line_error('app "X"\nstate count = missing\n', 2)

    def test_unknown_identifier_is_named(self):
        with self.assertRaisesRegex(ValueError, r"Line 4: column 13: Unknown identifier: missing"):
            parse('app "X"\nstate count = 0\naction go:\n    count = missing + 1\n')
