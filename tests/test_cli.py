import contextlib
import io
import pathlib
import tempfile
import unittest
from sedrava_cli import main

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "examples/workflow.sdr"

class CliTests(unittest.TestCase):
    def test_check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["check", str(SOURCE)]), 0)

    def test_test(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["test", str(SOURCE)]), 0)

    def test_build_web(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "index.html"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["build", "web", str(SOURCE), "--output", str(output)]), 0)
            self.assertIn("Workflow", output.read_text(encoding="utf-8"))

    def test_missing_file(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["check", "/definitely/not/a/file.sdr"]), 1)
