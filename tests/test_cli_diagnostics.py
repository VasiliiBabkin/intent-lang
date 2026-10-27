"""CLI diagnostic location tests."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from intent_cli import main


class CliDiagnosticTests(unittest.TestCase):
    def test_filename_line_and_fallback_column(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "broken.intent"
            source.write_text('app "X"\nstate count = 0\naction go:\n    count = missing + 1\n', encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main(["check", str(source)])
            self.assertEqual(result, 1)
            self.assertIn(f"{source}:4:1: error: Unknown identifier: missing", stderr.getvalue())

    def test_non_source_errors_remain_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "missing.intent"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main(["check", str(source)])
            self.assertEqual(result, 1)
            self.assertIn("intent:", stderr.getvalue())
