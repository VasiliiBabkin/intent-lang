"""Sedrava identity and Android namespace regression tests."""
import pathlib
import tempfile
import unittest
import tomllib
from android_codegen_v03 import generate

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SedravaIdentityTests(unittest.TestCase):
    def test_distribution_and_entrypoint(self):
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["name"], "sedrava")
        self.assertEqual(metadata["project"]["scripts"]["sedrava"], "sedrava_cli:main")
        self.assertIn("sedrava_core", metadata["tool"]["setuptools"]["py-modules"])

    def test_android_namespace(self):
        source = (ROOT / "examples" / "workflow.sdr").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            output = generate(source, directory)
            kotlin = output.read_text(encoding="utf-8")
            gradle = (pathlib.Path(directory) / "app/build.gradle.kts").read_text(encoding="utf-8")
            self.assertIn("package org.sedrava.generated", kotlin)
            self.assertIn('namespace = "org.sedrava.generated"', gradle)
            self.assertIn('applicationId = "org.sedrava.generated"', gradle)
            self.assertTrue(output.exists())

    def test_no_legacy_python_imports_or_commands(self):
        import re
        legacy = re.compile(r"\\b(?:from|import)\\s+intent(?:_core|_cli)?\\b|\\bintent-lng\\b|\\bintent-lang\\b|\\bintent\\s+(?:check|test|build)\\b")
        for path in [*ROOT.glob("*.py"), *(ROOT / "tests").glob("*.py"), *(ROOT / "scripts").glob("*.py")]:
            if path.name == "test_rebrand_identity.py":
                continue
            with self.subTest(path=path.name):
                self.assertIsNone(legacy.search(path.read_text(encoding="utf-8")))

    def test_examples_use_sdr(self):
        self.assertTrue(list((ROOT / "examples").glob("*.sdr")))
        self.assertFalse(list((ROOT / "examples").glob("*.intent")))

if __name__ == "__main__":
    unittest.main()
