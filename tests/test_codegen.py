import pathlib
import tempfile
import unittest
from android_codegen import generate

class CodegenTests(unittest.TestCase):
    def test_generates_android_project(self):
        source = (pathlib.Path(__file__).resolve().parents[1] / "examples/counter.intent").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            file = generate(source, directory)
            code = file.read_text(encoding="utf-8")
            self.assertIn("class MainActivity", code)
            self.assertIn("mutableStateOf(0)", code)
            self.assertIn('Button(onClick', code)
            self.assertTrue((pathlib.Path(directory) / "app/build.gradle.kts").exists())

    def test_reject_unknown_ui_action(self):
        source = 'app "X"\nstate ready = false\nscreen main:\n    button "Go" -> missing\n'
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "unknown action"):
                generate(source, directory)
