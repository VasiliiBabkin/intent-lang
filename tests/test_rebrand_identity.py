"""Sedrava identity and Android namespace regression tests."""
import pathlib
import tempfile
import unittest
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 test-only backport
    import tomli as tomllib
from android_codegen_v03 import generate
from sedrava_cli import VERSION
from sedrava_android_identity import application_id

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SedravaIdentityTests(unittest.TestCase):
    def test_distribution_and_entrypoint(self):
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["name"], "sedrava")
        self.assertEqual(metadata["project"]["version"], VERSION)
        self.assertEqual(metadata["project"]["scripts"]["sedrava"], "sedrava_cli:main")
        self.assertIn("sedrava_core", metadata["tool"]["setuptools"]["py-modules"])

    def test_android_namespace(self):
        source = (ROOT / "examples" / "workflow.sdr").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            output = generate(source, directory)
            kotlin = output.read_text(encoding="utf-8")
            gradle = (pathlib.Path(directory) / "app/build.gradle.kts").read_text(encoding="utf-8")
            package = application_id("Workflow")
            self.assertIn("package " + package, kotlin)
            self.assertIn('namespace = "'+package+'"', gradle)
            self.assertIn('applicationId = "'+package+'"', gradle)
            self.assertTrue(output.exists())
            manifest = (pathlib.Path(directory) / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
            self.assertIn("<intent-filter>", manifest)
            self.assertIn("android.intent.action.MAIN", manifest)
            self.assertIn("android.intent.category.LAUNCHER", manifest)
            self.assertNotIn("<sedrava-filter>", manifest)

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
