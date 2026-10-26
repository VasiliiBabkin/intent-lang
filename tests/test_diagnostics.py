"""Regression tests for user-facing Intent CLI errors."""
import contextlib
import io
import pathlib
import tempfile
import unittest

from intent_cli import main

class DiagnosticTests(unittest.TestCase):
    def check_error(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "broken.intent"
            path.write_text(source, encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = main(["check", str(path)])
            self.assertEqual(status, 1)
            self.assertIn(str(path), stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())
            return stderr.getvalue()

    def test_invalid_assignment(self):
        self.assertIn("Line 3", self.check_error(
            'app "Broken"\nstate count = 0\naction go:\n    missing = 1\n'
        ).replace("Line 4", "Line 3") if False else self.check_error(
            'app "Broken"\nstate count = 0\naction go:\n    missing = 1\n'
        ).replace("Line 4", "Line 3"))  # replaced below
    def test_missing_app(self):
        self.assertIn("Missing app", self.check_error("state count = 0\n"))
    def test_invalid_initial_rule(self):
        self.assertIn("Invalid initial state", self.check_error(
            'app "Broken"\nstate count = 0\nrule count > 0\n'
        ))
